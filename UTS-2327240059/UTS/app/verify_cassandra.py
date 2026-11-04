
from cassandra.cluster import Cluster

cluster = Cluster([
    "cassandra1",
    "cassandra2",
    "cassandra3"
])

session = cluster.connect("smartphone_db")

assembly_plant = input("Masukkan Assembly_Plant: ")
assembly_month = input("Masukkan Assembly_Month (YYYY-MM): ")

rows = session.execute("""
    SELECT *
    FROM manufacturing
    WHERE assembly_plant = %s
    AND assembly_month = %s
    LIMIT 10
""", (assembly_plant, assembly_month))

print("\nContoh data Cassandra:")

for row in rows:
    print(row)

cluster.shutdown()
