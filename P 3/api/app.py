# LATIHAN PERTEMUAN 4

from fastapi import FastAPI
from minio import Minio
import os
import json
import io

app = FastAPI()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "bronze")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


@app.get("/")
def home():
    return {
        "message": "Data Lake API",
        "bucket": MINIO_BUCKET
    }


@app.get("/objects")
def get_objects():

    objects = minio_client.list_objects(
        MINIO_BUCKET,
        recursive=True
    )

    object_list = []

    for obj in objects:
        object_list.append({
            "name": obj.object_name,
            "size": obj.size,
            "last_modified": obj.last_modified
        })

    return {
        "bucket": MINIO_BUCKET,
        "total_objects": len(object_list),
        "objects": object_list
    }

# Tambahkan endpoint sementara utk membaca isi e-commerce.json dari bucket bronze
@app.get("/read-ecommerce")
def read_ecommerce():
    try:
        # Mendapatkan objek e-commerce.json dari bucket bronze
        response = minio_client.get_object(
            MINIO_BUCKET, 
            "ecommerce.json"
        )
        
        data = response.read().decode("utf-8")
        response.close()
        response.release_conn()

        return {
            "data": data
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# Endpoint untuk membersihkan bucket bronze
@app.get("/clean-ecommerce")
def clean_ecommerce():
    try:
        # Membaca data dari bucket bronze
        response = minio_client.get_object(
            MINIO_BUCKET, 
            "ecommerce.json"
        )

        raw_data = response.read().decode("utf-8")
        response.close()
        response.release_conn()

        # Mengubah data JSON menjadi Python
        data = json.loads(raw_data)

        # Membersihkan data e-commerce (contoh: menghapus field yang tidak perlu)
        for transaction in data["payload"]:
            transaction["customer"]["full_name"] = transaction["customer"]["full_name"].strip().title()
            transaction["notes"] = transaction["notes"].strip()

        # Mengubah kembali data menjadi JSON
        clean_data = json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ).encode("utf-8")

        # Nama bucket silver
        silver_bucket = "silver"

        # Menyimpan data yang sudah dibersihkan ke bucket silver
        minio_client.put_object(
            silver_bucket,
            "ecommerce_clean.json",
            io.BytesIO(clean_data),
            length=len(clean_data),
            content_type="application/json"
        )

        return {
            "message": "Data e-commerce berhasil dibersihkan dan disimpan ke bucket silver.",
            "bucket": silver_bucket,
            "object": "ecommerce_clean.json"
        }

        # TIDAK PERLU
        # # Menghapus objek e-commerce.json dari bucket bronze
        # minio_client.remove_object(MINIO_BUCKET, "ecommerce.json")
        # return {
        #     "message": "e-commerce.json has been removed from the bucket."
        # }

    except Exception as e:
        return {
            "error": str(e)
        }

# ENDPOINT untuk aggregate data e-commerce dari bucket silver
# catatan : menggabungkan atau merangkum banyak data menjadi informasi yang lebih ringkas.
@app.get("/aggregate-ecommerce")
def aggregate_ecommerce():
    try:
        # Membaca data dari bucket silver
        response = minio_client.get_object(
            "silver",
            "ecommerce_clean.json"
        )

        raw_data = response.read().decode("utf-8")
        response.close()
        response.release_conn()

        # Mengubah data JSON menjadi Python
        data = json.loads(raw_data)

        # Melakukan aggregate data e-commerce (contoh: menghitung total transaksi dan total revenue)
        aggregate = {}

        for transaction in data["payload"]:
            status = transaction["status"]

            if status not in aggregate:
                aggregate[status] = {
                    "total_transactions": 0,
                    "total_items": 0,
                    "total_sales": 0
                }
            
            aggregate[status]["total_transactions"] += 1
            aggregate[status]["total_sales"] += transaction["total_paid"]

            # membaca items yang memang ada di JSON.
            for item in transaction["items"]:
                aggregate[status]["total_items"] += item["qty"]
        
        # Mengubah hasil aggregate menjadi JSON
        gold_data = json.dumps(
            aggregate,
            indent=2,
            ensure_ascii=False
        ).encode("utf-8")

        # Nama bucket gold
        gold_bucket = "gold"

        # # Membuat bucket gold jika belum ada
        # if not minio_client.bucket_exists(gold_bucket):
        #     minio_client.make_bucket(gold_bucket)

        # Menyimpan hasil aggregate ke bucket gold
        minio_client.put_object(
            gold_bucket,
            "ecommerce_aggregate.json",
            io.BytesIO(gold_data),
            length=len(gold_data),
            content_type="application/json"
        )

        return {
            "message": "Data e-commerce berhasil di-aggregate dan disimpan ke bucket gold.",
            "bucket": gold_bucket,
            "object": "ecommerce_aggregate.json"
        }
    
    except Exception as e:
        return {
            "error": str(e)
        }