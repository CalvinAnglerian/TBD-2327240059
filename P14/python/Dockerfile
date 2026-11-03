FROM python:3.12-slim
# RUN pip install --no-cache-dir boto3 pandas fastavro confluent_kafka cassandra-driver pyarrow neo4j

# yg dipakai di pertemuan ini
RUN pip install --no-cache-dir boto3 pandas neo4j

# catatan:
# docker compose up -d --build python seaweedfs neo4j

# Membuat node (di neo4j browser)
# MERGE (m:Mahasiswa {id: "2428240001"})
# SET m.nama = "Budi",
#     m.alamat = "Palembang"
# RETURN m

# MERGE (m:Mahasiswa {id: "2428240002"})
# SET m.nama = "Andra",
#     m.alamat = "Jakarta"
# RETURN m

# Membuat Edge
# MATCH (m1:Mahasiswa {id: "2428240001"})
# MATCH (m2:Mahasiswa {id: "2428240002"})
# MERGE (m1)-[:Teman]->(m2)
# RETURN m1, m2

# MATCH p=()-[Teman]->() RETURN p LIMIT 25;



# docker exec -it python python3 app/p14/app.py