# MATERI STREAM PROCESSING

FROM python:3.12-slim

RUN pip install --no-cache-dir boto3 pandas fastavro confluent_kafka

# jalankan
# C:\Users\user602\Documents\GitHub\TBD-2327240059\P10>docker compose up -d --build python kafka seaweedfs

# melihat topik dalam kafka
# docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9094 --list

# buat topik
# docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9094 --create---topic pesanan #(nama topik)

# tampilkan
# docker exec -it python python3 P10/app/producer.py
# docker exec -it python python3 P10/app/consumer.py
# docker exec -it python python3 P10/app/result.py

# Materi kuis --> Dari Materi 1 smpai data ingestion / materi 10

# # catatan
# Data ingestion = data mentah
# Batch processing =
# Stream processing = 
# Event processing = 