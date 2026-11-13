
import io
import re
import boto3
import pandas as pd

from botocore.client import Config
from botocore.exceptions import ClientError


# ==========================================
# KONFIGURASI S3 SEAWEEDFS
# ==========================================

ENDPOINT_URL = "http://192.168.5.28:8333"

BUCKET_NAME = "bucket"

BRONZE_PREFIX = "bronze/"
SILVER_KEY = "silver/cleaned_transactions.parquet"

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id="any",
    aws_secret_access_key="any",
    region_name="us-east-1",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)


# ==========================================
# FUNGSI STANDARISASI NAMA KOLOM
# ==========================================

def normalize_column_name(column):

    column = str(column).strip().lower()

    column = re.sub(r"[^a-z0-9]+", "_", column)

    column = column.strip("_")

    return column


# ==========================================
# FUNGSI MEMBACA DATA BRONZE
# ==========================================

def read_bronze_data():

    print("\n[PC 2] Mengambil data dari Bronze Layer...")

    try:

        # Memastikan bucket tersedia
        s3_client.head_bucket(Bucket=BUCKET_NAME)

        # Mengambil daftar seluruh file Parquet
        paginator = s3_client.get_paginator("list_objects_v2")

        pages = paginator.paginate(
            Bucket=BUCKET_NAME,
            Prefix=BRONZE_PREFIX
        )

        parquet_files = []

        for page in pages:

            for obj in page.get("Contents", []):

                key = obj["Key"]

                if key.lower().endswith(".parquet"):
                    parquet_files.append(key)

        if not parquet_files:
            raise FileNotFoundError(
                "Tidak ditemukan file Parquet di Bronze Layer."
            )

        print(f"[INFO] Ditemukan {len(parquet_files)} file Parquet.")

        dataframes = []

        # Membaca setiap file Parquet
        for key in sorted(parquet_files):

            print(f"[PROSES] Membaca: {key}")

            response = s3_client.get_object(
                Bucket=BUCKET_NAME,
                Key=key
            )

            content = response["Body"].read()

            df = pd.read_parquet(
                io.BytesIO(content),
                engine="pyarrow"
            )

            print(
                f"[INFO] {len(df)} baris, "
                f"{len(df.columns)} kolom"
            )

            dataframes.append(df)

        # Menggabungkan seluruh file
        df_bronze = pd.concat(
            dataframes,
            ignore_index=True,
            sort=False
        )

        print(
            f"\n[INFO] Total data Bronze: "
            f"{len(df_bronze)} baris"
        )

        return df_bronze

    except Exception as e:

        print(f"[PC 2 ERROR] Gagal membaca Bronze: {e}")

        return None


# ==========================================
# FUNGSI SCHEMA-ON-WRITE
# ==========================================

def apply_schema_on_write(df):

    print("\n[PC 2] Menerapkan Schema-on-Write...")

    # Menyeragamkan nama seluruh kolom
    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    # Menghapus kolom yang namanya kosong
    df = df.loc[:, df.columns != ""]

    # Menyeragamkan nilai teks tanpa mengubah tipe kolom lain
    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[column] = df[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    # Menghapus baris yang seluruh nilainya kosong
    df = df.dropna(how="all")

    # Menghapus data duplikat
    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(f"[INFO] Data duplikat dihapus: {removed} baris")
    print(f"[INFO] Jumlah data bersih: {len(df)} baris")

    print("\n[INFO] Struktur kolom Silver:")

    print(df.dtypes)

    return df


# ==========================================
# FUNGSI MENYIMPAN DATA SILVER
# ==========================================

def save_silver_data(df):

    print("\n[PC 2] Menyimpan data ke Silver Layer...")

    try:

        out_buffer = io.BytesIO()

        df.to_parquet(
            out_buffer,
            index=False,
            engine="pyarrow",
            compression="snappy"
        )

        out_buffer.seek(0)

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=SILVER_KEY,
            Body=out_buffer.getvalue(),
            ContentType="application/vnd.apache.parquet"
        )

        # Verifikasi hasil upload
        result = s3_client.head_object(
            Bucket=BUCKET_NAME,
            Key=SILVER_KEY
        )

        print("\n========================================")
        print("[PC 2 SUCCESS] SILVER LAYER BERHASIL")
        print("========================================")

        print(f"[INFO] Total baris : {len(df)}")
        print(f"[INFO] Total kolom : {len(df.columns)}")

        print(
            f"[INFO] Ukuran file : "
            f"{result['ContentLength'] / (1024 * 1024):.2f} MB"
        )

        print(
            f"[INFO] Lokasi      : "
            f"s3://{BUCKET_NAME}/{SILVER_KEY}"
        )

    except Exception as e:

        print(f"[PC 2 ERROR] Gagal menyimpan Silver: {e}")


# ==========================================
# PROGRAM UTAMA PC 2
# ==========================================

def run_pc2_silver():

    print("========================================")
    print("=== PC 2: SILVER LAYER (SCHEMA-ON-WRITE) ===")
    print("========================================")

    df_bronze = read_bronze_data()

    if df_bronze is None:
        return

    if df_bronze.empty:
        print("[ERROR] Data Bronze kosong.")
        return

    df_silver = apply_schema_on_write(df_bronze)

    if df_silver.empty:
        print("[ERROR] Tidak ada data yang dapat disimpan.")
        return

    save_silver_data(df_silver)


if __name__ == "__main__":

    run_pc2_silver()
