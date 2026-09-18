# Pertemuan 2

# docker compose up -d : untuk menjalankan dan mengaktifkan semua layanan (container) yang 
#                        terdaftar di dalam file docker-compose.yaml Anda secara otomatis di latar belakang.

# PS C:\TBD-2327240059> docker compose up -d
[+] up 16/16
 ✔ Image postgres:15-alpine         Pulled                                                                                                                                                                      38.4s
 ✔ Network tbd-2327240059_docker_network Created                                                                                                                                                                      0.0s
 ✔ Volume tbd-2327240059_pgdata          Created                                                                                                                                                                      0.0s
 ✔ Container postgres                    Started                                                                                                                                                                      1.1s

# PS C:\TBD-2327240059> docker image ls
                                                                                                                                                                                                      i Info →   U  In Use
IMAGE                                            ID             DISK USAGE   CONTENT SIZE   EXTRA
mongodb/mongodb-community-server:8.3-ubi9-slim   04bf69d01eaa        658MB          160MB    U   
nginx:alpine                                     3a7edb153fcd       94.4MB         27.2MB        
postgres:15-alpine                               444c177ac122        417MB          116MB    U   

# PS C:\TBD-2327240059> docker container ls
CONTAINER ID   IMAGE                COMMAND                  CREATED              STATUS              PORTS                                         NAMES
3ccd65d9391b   postgres:15-alpine   "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   postgres

# PS C:\TBD-2327240059> docker ps : melihat semua container yang directorynya ada di semua tempat
CONTAINER ID   IMAGE                COMMAND                  CREATED              STATUS              PORTS                                         NAMES
3ccd65d9391b   postgres:15-alpine   "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   postgres

# docker compose ps : melihat daftar container yang hanya ada di compose ini saja ( di docker-compose.yaml)

# docker exec -it postgres bash : masuk ke bash container
# cttan : postgres = nama container

# psql -U admin -d postgres : masuk ke database postgres (default database)

# postgres=# CREATE DATABASE mahasiswa_db; Membuat database mahasiswa_db

# exit;

# psql -U admin -d mahasiswa_db