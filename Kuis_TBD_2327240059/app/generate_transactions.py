import os
import random
from datetime import datetime, timedelta

import psycopg2

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    dbname=os.getenv("DB_NAME", "hospital_db"),
    user=os.getenv("DB_USER", "hospital"),
    password=os.getenv("DB_PASSWORD", "hospital123"),
)

layanan = {
    "Rawat Jalan": ["Poli Umum", "Poli Anak", "Poli Jantung"],
    "Rawat Inap": ["Ruang A", "Ruang B", "Ruang C"],
    "IGD": ["IGD"],
}

pembayaran = ["BPJS", "Asuransi", "Umum"]
status_transaksi = ["Selesai", "Selesai", "Selesai", "Pending"]

try:
    with conn:
        with conn.cursor() as cur:
            for i in range(100):
                jenis = random.choice(list(layanan.keys()))
                poli = random.choice(layanan[jenis])
                tanggal = datetime.now() - timedelta(
                    days=random.randint(0, 29),
                    hours=random.randint(0, 23)
                )

                biaya = {
                    "Rawat Jalan": random.randint(100_000, 500_000),
                    "Rawat Inap": random.randint(1_000_000, 8_000_000),
                    "IGD": random.randint(300_000, 2_000_000),
                }[jenis]

                cur.execute(
                    """
                    INSERT INTO transaksi_layanan (
                        tanggal_transaksi, id_pasien, jenis_layanan,
                        poli, metode_pembayaran, biaya, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        tanggal,
                        f"PSN-{random.randint(1, 40):04d}",
                        jenis,
                        poli,
                        random.choice(pembayaran),
                        biaya,
                        random.choice(status_transaksi),
                    )
                )

    print("Berhasil menyimpan 100 transaksi ke PostgreSQL.")

finally:
    conn.close()
