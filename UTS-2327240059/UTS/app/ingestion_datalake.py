
import io
import os
import time
import pandas as pd
import boto3

from botocore.client import Config

CSV_PATH = "/app/data/smartphone_manufacture.csv"

S3_ENDPOINT = "http://seaweedfs:8333"
ACCESS_KEY = "admin"
SECRET_KEY = "secret"

BUCKETS = ["bronze", "silver", "gold"]


def connect_s3():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1"
    )


def wait_for_s3():
    for attempt in range(30):
        try:
            client = connect_s3()
            client.list_buckets()
            return client

        except Exception as error:
            print(f"Menunggu SeaweedFS: {attempt + 1}/30")
            time.sleep(5)

    raise RuntimeError("SeaweedFS belum dapat diakses")


def ensure_buckets(s3):
    existing = {
        bucket["Name"]
        for bucket in s3.list_buckets()["Buckets"]
    }

    for bucket in BUCKETS:
        if bucket not in existing:
            s3.create_bucket(Bucket=bucket)
            print(f"Bucket dibuat: {bucket}")


def main():

    print("Memeriksa dataset...")

    if not os.path.isfile(CSV_PATH):
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: {CSV_PATH}"
        )

    print("Membaca dataset...")

    df = pd.read_csv(CSV_PATH)

    print(f"Jumlah data awal: {len(df):,}")

    s3 = wait_for_s3()

    ensure_buckets(s3)

    # BRONZE
    print("\nMemproses Bronze...")

    with open(CSV_PATH, "rb") as file:
        s3.upload_fileobj(
            file,
            "bronze",
            "smartphone/smartphone_manufacture.csv"
        )

    print("Bronze berhasil disimpan.")

    # SILVER
    print("\nMemproses Silver...")

    clean = df.copy()

    clean["Assembly_Date"] = pd.to_datetime(
        clean["Assembly_Date"],
        errors="coerce"
    )

    clean = clean.dropna(
        subset=["Assembly_Date"]
    )

    clean = clean.drop_duplicates(
        subset=["Serial_Number"]
    )

    for col in ["Assembly_Plant", "Brand", "Model_Name"]:
        clean[col] = clean[col].astype("string").str.strip()

    clean["Defect_Classification"] = (
        clean["Defect_Classification"]
        .fillna("Not Classified")
    )

    silver_buffer = io.BytesIO()

    clean.to_parquet(
        silver_buffer,
        index=False
    )

    silver_buffer.seek(0)

    s3.upload_fileobj(
        silver_buffer,
        "silver",
        "smartphone/smartphone_clean.parquet"
    )

    print(f"Silver berhasil disimpan: {len(clean):,} baris.")

    # GOLD
    print("\nMemproses Gold...")

    aggregations = {
        "Serial_Number": "count",
        "Unit_BOM_Cost_USD": "mean",
        "Battery_Capacity_Test_mAh": "mean"
    }

    summary = clean.groupby(
        ["Assembly_Plant", "Brand", "Model_Name"]
    ).agg(aggregations).reset_index()

    summary = summary.rename(columns={
        "Serial_Number": "Total_Production",
        "Unit_BOM_Cost_USD": "Average_BOM_Cost_USD",
        "Battery_Capacity_Test_mAh": "Average_Battery_mAh"
    })

    gold_buffer = io.BytesIO()

    summary.to_parquet(
        gold_buffer,
        index=False
    )

    gold_buffer.seek(0)

    s3.upload_fileobj(
        gold_buffer,
        "gold",
        "smartphone/production_summary.parquet"
    )

    print(f"Gold berhasil disimpan: {len(summary):,} baris.")

    # GOLD DEFECT SUMMARY
    defects = clean[
        clean["Defect_Classification"] != "Not Classified"
    ]

    defect_summary = defects.groupby(
        ["Assembly_Plant", "Defect_Classification"]
    ).size().reset_index(name="Total_Defects")

    defect_buffer = io.BytesIO()

    defect_summary.to_parquet(
        defect_buffer,
        index=False
    )

    defect_buffer.seek(0)

    s3.upload_fileobj(
        defect_buffer,
        "gold",
        "smartphone/defect_summary.parquet"
    )

    print("Ringkasan defect berhasil disimpan.")

    print("\nINGESTION DATA LAKE SELESAI!")

    print("Buka http://localhost:8888")


if __name__ == "__main__":
    main()
