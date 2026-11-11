import os
import boto3
import pandas as pd
import io
import json

MINIO_HOST = os.getenv("MINIO_HOST", "192.168.1.100")
MINIO_ENDPOINT = f"http://192.168.3.40:9000"

s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin"
)

BUCKET_NAME = "datalake-company"

def clean_row(row):
    buyer_id = row.get('buyer_id') or row.get('buyer')
    seller_id = row.get('seller_id') or row.get('seller')
    quantity = int(row.get('quantity') or row.get('qty') or 0)
    unit_price = float(row.get('unit_price') or row.get('price') or 0.0)
    payment_method = row.get('payment_method') or row.get('payment')
    order_status = row.get('order_status') or row.get('status')
    total_amount = float(row.get('total_amount') or row.get('total') or 0.0)

    raw_dt = row.get('order_datetime') or row.get('order_date')
    if isinstance(raw_dt, (int, float)):
        order_datetime = pd.to_datetime(raw_dt, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
    else:
        order_datetime = pd.to_datetime(raw_dt).strftime('%Y-%m-%d %H:%M:%S')

    raw_cod = row.get('is_cod')
    is_cod = raw_cod.lower() == 'true' if isinstance(raw_cod, str) else bool(raw_cod)

    return {
        "order_id": str(row.get('order_id')),
        "platform": str(row.get('platform')),
        "order_datetime": order_datetime,
        "buyer_id": str(buyer_id),
        "seller_id": str(seller_id),
        "product_name": str(row.get('product_name')),
        "category": str(row.get('category')),
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_amount": float(row.get('discount_amount') or 0.0),
        "shipping_cost": float(row.get('shipping_cost') or 0.0),
        "total_amount": total_amount,
        "payment_method": str(payment_method),
        "order_status": str(order_status),
        "shipping_city": str(row.get('shipping_city')),
        "shipping_province": str(row.get('shipping_province')),
        "currency": str(row.get('currency', 'IDR')).upper(),
        "is_cod": is_cod,
        "voucher_code": row.get('voucher_code') if pd.notna(row.get('voucher_code')) else "NONE",
        "review_score": float(row.get('review_score')) if pd.notna(row.get('review_score')) else 0.0,
        "source_batch": str(row.get('source_batch')),
        "ingested_at": str(row.get('ingested_at'))
    }

def main():
    # 1. Baca data kotor dari Bronze
    bronze_key = "bronze/orders/raw_orders_batch1.json"
    res = s3.get_object(Bucket=BUCKET_NAME, Key=bronze_key)
    lines = res['Body'].read().decode('utf-8').strip().split('\n')
    raw_records = [json.loads(line) for line in lines]

    # 2. Schema-on-Write (Pembersihan & Transformasi)
    cleaned_records = [clean_row(r) for r in raw_records]
    df_silver = pd.DataFrame(cleaned_records)

    # 3. Simpan ke Silver Zone
    csv_buffer = io.StringIO()
    df_silver.to_csv(csv_buffer, index=False)
    silver_key = "silver/orders/cleaned_orders_batch1.csv"
    
    s3.put_object(Bucket=BUCKET_NAME, Key=silver_key, Body=csv_buffer.getvalue().encode('utf-8'))
    print(f"[PC 2] Schema-on-Write berhasil, data bersih disimpan di Silver: s3://{BUCKET_NAME}/{silver_key}")

if __name__ == "__main__":
    main()