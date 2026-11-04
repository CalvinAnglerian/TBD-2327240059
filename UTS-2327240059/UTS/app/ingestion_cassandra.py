
import time
import pandas as pd

from cassandra.cluster import Cluster
from cassandra.concurrent import execute_concurrent_with_args
from cassandra import ConsistencyLevel

CSV_PATH = "/app/data/smartphone_manufacture.csv"

HOSTS = [
    "cassandra1",
    "cassandra2",
    "cassandra3"
]


def connect_cassandra():

    for attempt in range(60):

        try:
            cluster = Cluster(HOSTS)
            session = cluster.connect()

            print("Berhasil terhubung ke Cassandra.")

            return cluster, session

        except Exception as error:

            print(f"Menunggu Cassandra: {attempt + 1}/60")

            time.sleep(5)

    raise RuntimeError("Cassandra belum siap.")


def main():

    import os

    if not os.path.isfile(CSV_PATH):
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {CSV_PATH}"
        )

    print("Membaca dataset...")

    df = pd.read_csv(CSV_PATH)

    df["Assembly_Date"] = pd.to_datetime(
        df["Assembly_Date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Serial_Number", "Assembly_Plant", "Assembly_Date"]
    )

    df = df.drop_duplicates(
        subset=["Serial_Number"]
    )

    df["assembly_month"] = df["Assembly_Date"].dt.strftime("%Y-%m")

    cluster, session = connect_cassandra()

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS smartphone_db
        WITH replication = {
            'class': 'NetworkTopologyStrategy',
            'DC1': 3
        }
    """)

    session.set_keyspace("smartphone_db")

    session.execute("""
        CREATE TABLE IF NOT EXISTS manufacturing (

            assembly_plant text,
            assembly_month text,
            serial_number text,

            brand text,
            model_name text,
            production_line text,
            critical_component text,

            assembly_date date,
            unit_bom_cost_usd double,
            battery_capacity_test_mah int,

            defect_classification text,
            qc_inspector_id text,

            PRIMARY KEY (
                (assembly_plant, assembly_month),
                serial_number
            )
        )
    """)

    insert = session.prepare("""
        INSERT INTO manufacturing (
            assembly_plant,
            assembly_month,
            serial_number,
            brand,
            model_name,
            production_line,
            critical_component,
            assembly_date,
            unit_bom_cost_usd,
            battery_capacity_test_mah,
            defect_classification,
            qc_inspector_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    insert.consistency_level = ConsistencyLevel.LOCAL_QUORUM

    def get_value(row, column):

        value = row.get(column)

        if pd.isna(value):
            return None

        return value

    params = []

    for _, row in df.iterrows():

        params.append((

            str(row["Assembly_Plant"]),
            str(row["assembly_month"]),
            str(row["Serial_Number"]),

            get_value(row, "Brand"),
            get_value(row, "Model_Name"),
            get_value(row, "Production_Line"),
            get_value(row, "Critical_Component"),

            row["Assembly_Date"].date(),

            float(row["Unit_BOM_Cost_USD"])
            if pd.notna(row["Unit_BOM_Cost_USD"])
            else None,

            int(row["Battery_Capacity_Test_mAh"])
            if pd.notna(row["Battery_Capacity_Test_mAh"])
            else None,

            get_value(row, "Defect_Classification"),
            get_value(row, "QC_Inspector_ID")

        ))

    print(f"Memasukkan {len(params):,} data ke Cassandra...")

    success = 0

    for start in range(0, len(params), 500):

        batch = params[start:start + 500]

        results = execute_concurrent_with_args(
            session,
            insert,
            batch,
            concurrency=50,
            raise_on_first_error=False
        )

        success += sum(
            1 for ok, _ in results if ok
        )

        print(
            f"Progress: {min(start + len(batch), len(params)):,}/{len(params):,}"
        )

    print(f"Berhasil: {success:,}")
    print(f"Gagal: {len(params) - success:,}")

    print("\nINGESTION CASSANDRA SELESAI!")

    cluster.shutdown()


if __name__ == "__main__":
    main()
