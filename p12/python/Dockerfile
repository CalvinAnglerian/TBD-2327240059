FROM python:3.12-slim
RUN pip install --no-cache-dir boto3 pandas fastavro confluent_kafka cassandra-driver pyarrow

# langkah-langkah
# 1. docker compose up -d cassandra3 kafka python

# 2. Membuat topic di Kafka
# docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9094 --create --topic sensor_readings

# 3. Masuk ke cassandra shell
# docker exec -it cassandra cqlsh
# docker exec -it cassandra2 cqlsh
# docker exec -it cassandra3 cqlsh

# 4.Membuat Keyspace otomatis tereplikasi di seluruh node di dalam cluster DC1, lakukan di cassandra saja
# - CREATE KEYSPACE IF NOT EXISTS iot
# - WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': 3};

# 5. Membuat tabel.
# CREATE TABLE IF NOT EXISTS iot.sensor_readings (
#     sensor_id   text,
#     ts          timestamp,
#     temperature double,
#     humidity    double,
#     PRIMARY KEY ((sensor_id), ts)
# ) WITH CLUSTERING ORDER BY (ts DESC);

# untuk cek sudah dibikin belum
# select * from iot.sensor_readings;

# 6. Memasukkan data sensor
# sensor_data.csv --> masukkan ke dalam folder python

# 7. docker exec -it python python3 app/p13/producer.py

# 8. select * from iot.sensor_readings;

#  sensor_id | ts                              | humidity | temperature
# -----------+---------------------------------+----------+-------------
#   sensor-A | 2026-10-23 09:02:00.000000+0000 |     69.8 |        29.2
#   sensor-A | 2026-10-23 09:01:00.000000+0000 |     70.1 |        29.3
#   sensor-A | 2026-10-23 09:00:00.000000+0000 |     70.5 |        29.1
#   sensor-C | 2026-10-23 09:00:00.000000+0000 |       74 |        27.5
#   sensor-B | 2026-10-23 09:02:00.000000+0000 |     65.9 |        30.8
#   sensor-B | 2026-10-23 09:00:00.000000+0000 |     65.2 |          31

# (6 rows)

# NoSQL Key-Value Store dan Document Store: untuk kebutuhan batch, mengambil atau mengolah data dari Data Lake, kemudian menyimpan hasilnya ke database seperti MongoDB.

# NoSQL Column-Family: untuk kebutuhan real-time, menerima data dari Kafka dan menyimpannya ke Cassandra agar bisa diakses aplikasi dengan cepat.