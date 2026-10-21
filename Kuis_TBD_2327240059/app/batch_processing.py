import os
import json
from io import BytesIO

import boto3
import pandas as pd

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:8333"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "admin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "secret"),
    region_name="us-east-1",
)

# Pastikan bucket zona tersedia
for bucket in ["silver", "gold"]:
    try:
        s3.create_bucket(Bucket=bucket)
    except Exception:
        pass

# 1. Membaca data mentah dari Bronze
obj = s3.get_object(
    Bucket="bronze",
    Key="transaksi_layanan.parquet"
)

df = pd.read_parquet(BytesIO(obj["Body"].read()))

# 2. Membersihkan dan menstandarkan data
df["tanggal_transaksi"] = pd.to_datetime(
    df["tanggal_transaksi"], errors="coerce"
)
df["biaya"] = pd.to_numeric(df["biaya"], errors="coerce")
df["status"] = df["status"].astype("string").str.strip()
df["jenis_layanan"] = (
    df["jenis_layanan"].astype("string").str.strip()
)

df = df.drop_duplicates(subset=["id_transaksi"])
df = df.dropna(
    subset=["id_transaksi", "tanggal_transaksi", "biaya", "jenis_layanan"]
)
df = df[df["biaya"] >= 0].copy()

# Simpan data bersih ke Silver
silver_buffer = BytesIO()
df.to_parquet(silver_buffer, index=False, engine="pyarrow")
silver_buffer.seek(0)

s3.put_object(
    Bucket="silver",
    Key="transaksi_layanan_clean.parquet",
    Body=silver_buffer.getvalue(),
)

# 3. Buat data summary untuk direksi
# Transaksi selesai dipakai untuk menghitung pendapatan.
selesai = df[df["status"].str.lower() == "selesai"].copy()

selesai["tanggal"] = selesai["tanggal_transaksi"].dt.strftime("%Y-%m-%d")

summary = (
    selesai.groupby(["tanggal", "jenis_layanan"], as_index=False)
    .agg(
        jumlah_transaksi=("id_transaksi", "count"),
        total_pendapatan=("biaya", "sum"),
        rata_rata_biaya=("biaya", "mean"),
    )
)

# Simpan summary ke Gold dalam format Parquet
gold_buffer = BytesIO()
summary.to_parquet(gold_buffer, index=False, engine="pyarrow")
gold_buffer.seek(0)

s3.put_object(
    Bucket="gold",
    Key="summary_layanan_harian.parquet",
    Body=gold_buffer.getvalue(),
)

# Simpan juga versi JSON agar mudah diperiksa
json_data = summary.to_json(
    orient="records",
    indent=2,
    force_ascii=False
)

s3.put_object(
    Bucket="gold",
    Key="summary_layanan_harian.json",
    Body=json_data.encode("utf-8"),
    ContentType="application/json",
)

print("Batch processing selesai.")
print(f"Data bersih di Silver: {len(df)} transaksi.")
print(f"Summary di Gold: {len(summary)} baris.")
print(summary.to_string(index=False))
