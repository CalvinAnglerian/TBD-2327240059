import os
from io import BytesIO

import boto3
import pandas as pd
import psycopg2

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:8333"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "admin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "secret"),
    region_name="us-east-1",
)

# Membuat bucket zona Bronze jika belum tersedia
try:
    s3.create_bucket(Bucket="bronze")
except Exception:
    pass

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    dbname=os.getenv("DB_NAME", "hospital_db"),
    user=os.getenv("DB_USER", "hospital"),
    password=os.getenv("DB_PASSWORD", "hospital123"),
)

try:
    df = pd.read_sql_query(
        "SELECT * FROM transaksi_layanan ORDER BY id_transaksi",
        conn
    )
finally:
    conn.close()

buffer = BytesIO()
df.to_parquet(buffer, index=False, engine="pyarrow")
buffer.seek(0)

s3.put_object(
    Bucket="bronze",
    Key="transaksi_layanan.parquet",
    Body=buffer.getvalue(),
)

print(f"Batch ingestion selesai: {len(df)} transaksi.")
print("File tersimpan di Bronze/transaksi_layanan.parquet")
