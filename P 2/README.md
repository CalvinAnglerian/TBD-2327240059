# Pertemuan 2

# docker compose up -d : untuk menjalankan dan mengaktifkan semua layanan (container) yang terdaftar di dalam file docker-compose.yaml Anda secara otomatis di latar belakang.

# PS C:\TBD-2327240059> docker compose up -d

# PS C:\TBD-2327240059> docker image ls
                                                                                      
# PS C:\TBD-2327240059> docker container ls

# PS C:\TBD-2327240059> docker ps : melihat semua container yang directorynya ada di semua tempat

# docker compose ps : melihat daftar container yang hanya ada di compose ini saja ( di docker-compose.yaml)

# docker exec -it postgres bash : masuk ke bash container
# cttan : postgres = nama container

# psql -U admin -d postgres : masuk ke database postgres (default database)

# postgres=# CREATE DATABASE mahasiswa_db; Membuat database mahasiswa_db

# exit;

# psql -U admin -d mahasiswa_db