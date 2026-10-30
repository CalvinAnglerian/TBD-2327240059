import io
import boto3
from botocore.client import Config
import pandas as pd
from neo4j import GraphDatabase

S3_ENDPOINT = "http://seaweedfs:8333" 
ACCESS_KEY = "admin"
SECRET_KEY = "secret"
BUCKET_NAME = "silver"
PREFIX = "financial/"

print("Menghubungkan ke SeaweedFS S3 Data Lake...")
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

def read_csv_from_s3(file_name):
    file_key = f"{PREFIX}{file_name}"
    print(f"Mengambil file {file_key} dari Data Lake...")
    
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
    status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    
    if status_code == 200:
        content = response['Body'].read()
        return pd.read_csv(io.BytesIO(content))
    else:
        raise Exception(f"Gagal mengambil file {file_key} dari S3.")

df_customers = read_csv_from_s3("customers.csv")
df_merchants = read_csv_from_s3("merchants.csv")
df_transactions = read_csv_from_s3("transactions.csv")

print(f"Berhasil memuat: {len(df_customers)} customers, {len(df_merchants)} merchants, {len(df_transactions)} transactions.")


URI = "bolt://neo4j:7687"
AUTH = ("neo4j", "secretsecret")

print("Menghubungkan ke Neo4j dan membangun graf...")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    with driver.session() as session:

        for _, row in df_customers.iterrows():
            session.run(
                """
                MERGE (c:Customer {customer_id: $id})
                SET c.name = $name,
                    c.risk_score = $riskScore
                """,
                id=str(row["customer_id"]),
                name=str(row["name"]),
                riskScore=float(row["risk_score"])
            )

        for _, row in df_merchants.iterrows():
            session.run(
                """
                MERGE (m:Merchant {merchant_id: $id})
                SET m.merchant_name = $name,
                    m.category = $category
                """,
                id=str(row["merchant_id"]),
                name=str(row["merchant_name"]),
                category=str(row["category"])
            )

        for _, row in df_transactions.iterrows():
            session.run(
                """
                MATCH (c:Customer {customer_id: $custId})
                MATCH (m:Merchant {merchant_id: $merchantId})
                MERGE (c)-[t:TRANSACTION {transaction_id: $txId}]->(m)
                SET t.amount = $amount,
                    t.timestamp = $timestamp
                """,
                custId=str(row["source_customer_id"]),
                merchantId=str(row["target_merchant_id"]),
                txId=str(row["transaction_id"]),
                amount=float(row["amount"]),
                timestamp=str(row["timestamp"])
            )

print("Selesai! Pipeline berbasis Boto3 dari SeaweedFS S3 ke Neo4j berhasil dieksekusi.")
