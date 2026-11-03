FROM quay.io/jupyter/minimal-notebook:latest
RUN pip install --no-cache-dir boto3 pandas fastavro kafka-python pyarrow pymongo

# catatan : parquet viewer digunakan untuk melihat file parquet di google.

# langkah-langkah :
# 1. docker compose up -d --build mongodb jupyter seaweedfs

# 2. buka seaweedfs
# create folder, kasih nama flight, terus masukkan file csv di dalam folder flight

# 3.buka jupyter

# 4. docker exec -it mongodb mongosh -u admin -p secretsecret

# 5.use admin
# db.createCollection("flights")

# 6.show collections
# db.flights.find()