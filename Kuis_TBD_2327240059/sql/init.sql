CREATE TABLE IF NOT EXISTS transaksi_layanan (
    id_transaksi SERIAL PRIMARY KEY,
    tanggal_transaksi TIMESTAMP NOT NULL,
    id_pasien VARCHAR(20) NOT NULL,
    jenis_layanan VARCHAR(30) NOT NULL,
    poli VARCHAR(50),
    metode_pembayaran VARCHAR(30),
    biaya NUMERIC(14, 2) NOT NULL,
    status VARCHAR(20) NOT NULL
);
