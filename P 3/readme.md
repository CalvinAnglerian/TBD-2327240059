# Pertemuan 3

# CATATAN
# ls -al : untuk melihat folder
# docker compose up -d nama_container : untuk pilih mau merunkan container yang mana
# docker compose down -v : untuk menghentikan container dan menghapus volume



<!-- Docker exec -it nama.container (minio1) bash

    ls data
    ls data/palembang
    
    Docker exec -it nama.container (minio1) bash
    ls data
    ls data/palembang
-->

docker stop minio3

docker stop minio2

docker start minio3

<!-- PERTEMUAN 4 LATIHAN -->
bronze = data mentah
silver = data bersih
gold = ...

1.buat program(bebas bhs pemrograman apa saja) yang terhubung api nya ke dalam data lake

baca isi data di bucket bronze
(tampilkan daftar nama object yang ada dalam bucket bronze)

2.Bersihkan data dari bucket bronze, lalu simpan data yang sudah dibersihkan tersebut ke bucker silver

3.Lakukan aggregate pada data silver tersebut lalu simpan di bucket Gold

catatan:
- baca data dari bucket bronze, lakukan pembersihan data lalu simpan di silver
- ambil data dari silver lalu lakukan aggregate sesuai kebutuhan bisnis lalu simpan di gold