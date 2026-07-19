# Aplikasi Manajemen Barang - Cloud Computing Docker Assignment

[![Docker](https://img.shields.io/badge/Docker-Containerization-blue)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Orchestration-blue)](https://docs.docker.com/compose/)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-red)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

## 📋 Daftar Isi

- [Tentang Project](#tentang-project)
- [Arsitektur & Network Topology](#arsitektur--network-topology)
- [Tugas yang Diselesaikan](#tugas-yang-diselesaikan)
- [Persyaratan](#persyaratan)
- [Setup & Installation](#setup--installation)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Testing & Monitoring](#testing--monitoring)
- [Struktur Project](#struktur-project)
- [Load Balancer](#load-balancer)
- [Scaling](#scaling)
- [Backup & Restore Volume](#backup--restore-volume)
- [Healthcheck](#healthcheck)
- [Troubleshooting](#troubleshooting)
- [Dokumentasi Lengkap](#dokumentasi-lengkap)

---

## Tentang Project

Aplikasi Manajemen Barang adalah project UTS (Ujian Tengah Semester) untuk mata kuliah **Komputasi Awan (Cloud Computing)** yang mendemonstrasikan:

✅ **Containerization** dengan Docker  
✅ **Microservices Architecture** (Web + API separation)  
✅ **Network Isolation** (Backend & Frontend network terpisah)  
✅ **Database Persistence** dengan PostgreSQL  
✅ **Healthcheck** untuk service dependency yang可靠  
✅ **Orchestration** menggunakan Docker Compose  
✅ **Scaling** dengan multiple container instances  
✅ **Load Balancing** dengan Nginx  
✅ **Backup & Restore** volume database  

### Fitur Utama

- 📦 **CRUD Operations**: Create, Read, Update, Delete barang
- 🔄 **REST API**: Backend API untuk mengelola data
- 🎨 **Web Interface**: Frontend untuk interaksi pengguna
- 💾 **Persistent Database**: PostgreSQL untuk data storage
- 🔒 **Network Isolation**: Backend & Frontend network terpisah
- ⚖️ **Load Balancing**: Nginx untuk distribusi traffic
- 📊 **Scaling**: Kemampuan scale API instances secara horizontal

---

## Arsitektur & Network Topology

### Arsitektur Multi-Layer Network

```
┌──────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE NETWORK                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               FRONTEND NETWORK                       │   │
│  │                    (frontend)                        │   │
│  │  ┌──────────┐                                       │   │
│  │  │   Web    │  Port 8000                             │   │
│  │  │ (Flask)  │  Bisa akses: api ✅, db ❌             │   │
│  │  └────┬─────┘                                       │   │
│  └───────┼──────────────────────────────────────────────┘   │
│          │                                                    │
│          ▼ (requests via http://api:8080)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           BACKEND NETWORK                             │   │
│  │                    (backend)                          │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │         API Cluster (Scalable)               │    │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌──────┐   │    │   │
│  │  │  │  API-1     │  │  API-2     │  │ ...  │   │    │   │
│  │  │  │  :8080     │  │  :8080     │  │      │   │    │   │
│  │  │  └──────┬─────┘  └──────┬─────┘  └──────┘   │    │   │
│  │  └─────────┼───────────────┼────────────────────┘    │   │
│  │            │               │                          │   │
│  │            ▼               ▼                          │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │  PostgreSQL (db)                             │    │   │
│  │  │  Port: 5432  │  Healthcheck: pg_isready      │    │   │
│  │  │  Volume: postgres_data (persistent)          │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    OPTIONAL: NGINX LOAD BALANCER (Port 80)           │   │
│  │    Round-robin distribution + health check           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Network Rules

| Dari \ Ke | db (backend) | api (backend+frontend) | web (frontend) |
|-----------|:-----------:|:---------------------:|:--------------:|
| **web** | ❌ Diblokir | ✅ Diizinkan | - |
| **api** | ✅ Diizinkan | ✅ Diizinkan | ❌ Diblokir |
| **db** | - | ❌ Diblokir | ❌ Diblokir |

### Container Details

| Container | Port | Network | Peran | Framework |
|-----------|------|---------|-------|-----------|
| **web** | 8000 | frontend | Frontend application | Flask + Python |
| **api** | 8080 (internal) | backend + frontend | Backend REST API | Flask + Python |
| **db** | 5432 | backend | Database | PostgreSQL 15 Alpine |
| **nginx** | 80 | - | Load Balancer (opsional) | Nginx |

---

## Tugas yang Diselesaikan

### ✅ Tugas 1: Network Separation
- **Tujuan**: Web tidak bisa akses database langsung, hanya melalui API
- **Hasil**: `docker compose exec web python -c "import socket; socket.getaddrinfo('db', 5432)"` → ❌ FAILED
- **Arsitektur**: Backend network (db + api) | Frontend network (web + api)
- **Status**: ✅ PASS

### ✅ Tugas 2: Backup & Restore Volume
- **Tujuan**: Backup data `postgres_data` ke file `.tar.gz`, hapus volume, restore kembali
- **Hasil**: Data berhasil dipulihkan 100% setelah restore
- **Command**:
  ```bash
  docker run --rm -v postgres_data:/data -v ${PWD}:/backup alpine tar czf /backup/barangdb-backup.tar.gz -C /data .
  ```
- **Status**: ✅ PASS

### ✅ Tugas 3: Healthcheck
- **Tujuan**: API menunggu database benar-benar siap sebelum start
- **Konfigurasi**: `pg_isready -U postgres` setiap 5 detik, `start_period: 10s`
- **Hasil**: API hanya start setelah db berstatus `(healthy)`
- **Status**: ✅ PASS

### ✅ Tugas 4: Horizontal Scaling
- **Tujuan**: Menjalankan 2 instance API dengan `--scale api=2`
- **Hasil**: 2 instance berjalan, sticky routing terdeteksi, load balancer direkomendasikan
- **Status**: ✅ PASS

---

## Persyaratan

### System Requirements

- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **RAM**: Minimal 2GB (untuk multiple instances)
- **Disk Space**: Minimal 500MB
- **OS**: Linux, macOS, atau Windows (dengan WSL2)

### Software yang Akan Diinstall Otomatis

- Python 3.9+
- Flask (Web Framework)
- psycopg2 (PostgreSQL adapter)
- requests (HTTP client)
- PostgreSQL 15 Alpine

---

## Setup & Installation

### 1. Clone/Download Project

```bash
# Jika menggunakan Git
git clone <repository-url>
cd permana-praktikum-docker

# Atau jika sudah punya folder project
cd /path/to/permana-praktikum-docker
```

### 2. Verifikasi struktur folder

```bash
# Pastikan struktur folder seperti ini:
ls -la

# Output yang diharapkan:
# ├── docker-compose.yml
# ├── docker-compose-with-nginx.yml
# ├── nginx.conf
# ├── api/
# │   ├── app.py
# │   ├── Dockerfile
# │   └── requirements.txt
# ├── web/
# │   ├── app.py
# │   ├── Dockerfile
# │   ├── requirements.txt
# │   └── templates/
# │       └── index.html
# ├── README.md
# ├── README.en.md
# ├── PLAN.md
# └── RINGKASAN.md
```

### 3. Check Docker Installation

```bash
# Verifikasi Docker
docker --version
docker ps

# Verifikasi Docker Compose
docker compose version
```

---

## Menjalankan Aplikasi

### Opsi 1: Tanpa Load Balancer (DEFAULT)

Ini adalah setup yang paling sederhana, cocok untuk development dan testing basic.

```bash
# 1. Navigate ke project directory
cd /path/to/permana-praktikum-docker

# 2. Build dan start services
docker compose up -d

# 3. Check status services
docker compose ps

# Output yang diharapkan:
# NAME                             SERVICE  STATUS          PORTS
# permana-praktikum-docker-db-1    db       Up (healthy)    5432/tcp
# permana-praktikum-docker-api-1   api      Up              8080/tcp
# permana-praktikum-docker-web-1   web      Up              0.0.0.0:8000->8000/tcp

# 4. Akses aplikasi
# - Web: http://localhost:8000
# - API: http://localhost:8080 (internal, dari container lain)
```

### Opsi 2: Dengan Load Balancer (ADVANCED)

Menggunakan Nginx untuk intelligent traffic distribution (round-robin).

```bash
# 1. Navigate ke project directory
cd /path/to/permana-praktikum-docker

# 2. Gunakan docker-compose-with-nginx.yml
docker compose -f docker-compose-with-nginx.yml up -d

# 3. Check status
docker compose -f docker-compose-with-nginx.yml ps

# 4. Akses aplikasi
# - Web: http://localhost (port 80)
# - API via Load Balancer: http://localhost/api/
```

### Opsi 3: Scaling dengan Multiple API Instances

```bash
# Scale API instances menjadi 2
docker compose up -d --scale api=2

# Verifikasi
docker compose ps
# Akan menampilkan: api-1, api-2

# Cek DNS resolve
docker compose exec web getent hosts api
# Output: 172.x.x.x api  (2 IP address)

# Check load distribution
docker compose exec web sh -c "for i in \$(seq 1 10); do curl -s -o /dev/null -w \"Request \$i: %{http_code}\\n\" http://api:8080/barang; done"
```

### Stop & Cleanup

```bash
# Stop services (keep volumes)
docker compose down

# Stop dan hapus semua data (termasuk database)
docker compose down -v

# Remove images juga
docker compose down -v --rmi all
```

---

## Testing & Monitoring

### 1. Health Check Services

```bash
# Cek semua container berjalan
docker compose ps

# Cek health status database
docker compose ps db
# Output: db-postgres  Up X minutes (healthy)

# Detail health check
docker inspect db-postgres --format "{{json .State.Health}}" | python -m json.tool

# Lihat logs web
docker compose logs -f web

# Lihat logs api
docker compose logs -f api

# Lihat logs database
docker compose logs -f db
```

### 2. Test API Endpoints

```bash
# GET semua barang
curl http://localhost:8080/barang

# GET barang by ID
curl http://localhost:8080/barang/1

# POST barang baru
curl -X POST http://localhost:8080/barang \
  -H "Content-Type: application/json" \
  -d '{"nama":"Laptop","harga":5000000}'

# PUT update barang
curl -X PUT http://localhost:8080/barang/1 \
  -H "Content-Type: application/json" \
  -d '{"nama":"Laptop Gaming","harga":6000000}'

# DELETE barang
curl -X DELETE http://localhost:8080/barang/1
```

**Catatan**: Karena port API tidak di-publish ke host, untuk akses dari host gunakan:
```bash
docker compose exec api-1 curl http://localhost:8080/barang
```

### 3. Test Web Interface

```bash
# Buka di browser
http://localhost:8000

# Test CRUD melalui web form
```

### 4. Test Network Isolation

```bash
# Web TIDAK bisa akses database (harus gagal ❌)
docker compose exec web python -c "import socket
try:
    socket.getaddrinfo('db', 5432)
    print('RESOLVES')
except Exception as e:
    print('FAILED', e)"

# Output: FAILED [Errno -5] No address associated with hostname

# API bisa akses database (harus sukses ✅)
docker compose exec api-1 python -c "import socket
try:
    socket.getaddrinfo('db', 5432)
    print('RESOLVES')
except Exception as e:
    print('FAILED', e)"

# Output: RESOLVES
```

### 5. Test Load Balancing (Jika Scale > 1)

```bash
# Cek DNS resolve
docker compose exec web getent hosts api

# Test distribusi request
docker compose exec web sh -c "for i in \$(seq 1 10); do curl -s -o /dev/null -w \"Request \$i: %{http_code}\\n\" http://api:8080/barang; done"

# Lihat logs dari tiap API instance
docker compose logs api-1 | grep "GET /barang"
docker compose logs api-2 | grep "GET /barang"
```

### 6. Monitor Resource Usage

```bash
# Real-time container statistics
docker stats

# CPU, Memory, Network, Block I/O per container
docker stats --no-stream
```

### 7. Database Inspection

```bash
# Connect ke PostgreSQL
docker compose exec db psql -U postgres -d barangdb

# List tables
\dt

# Show schema barang table
\d barang

# Query data
SELECT * FROM barang;

# Exit psql
\q
```

---

## Backup & Restore Volume

### Backup Volume ke tar.gz

```bash
# Backup data postgres_data ke file
docker run --rm \
  -v permana-praktikum-docker_postgres_data:/data \
  -v ${PWD}:/backup alpine \
  tar czf /backup/barangdb-backup.tar.gz -C /data .

# Verifikasi file backup
ls -la barangdb-backup.tar.gz
```

### Hapus Volume

```bash
# Stop container dan hapus volume
docker compose down -v

# Verifikasi volume terhapus
docker volume ls | Select-String "postgres"
```

### Buat Volume Baru & Restore

```bash
# Buat volume baru
docker volume create permana-praktikum-docker_postgres_data

# Restore backup ke volume baru
docker run --rm \
  -v permana-praktikum-docker_postgres_data:/data \
  -v ${PWD}:/backup alpine \
  tar xzf /backup/barangdb-backup.tar.gz -C /data

# Start container dan verifikasi data
docker compose up -d
docker compose exec db psql -U postgres -d barangdb -c "SELECT * FROM barang;"
```

---

## Healthcheck

### Konfigurasi di docker-compose.yml

```yaml
db:
  image: postgres:15-alpine
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s      # Periksa setiap 5 detik
    timeout: 5s       # Tunggu maksimal 5 detik per cek
    retries: 5        # Gagal 5x -> tandai unhealthy
    start_period: 10s # Grace period saat startup

api:
  build: ./api
  depends_on:
    db:
      condition: service_healthy  # Tunggu sampai DB HEALTHY
```

### Cara Kerja

```
1. Container db CREATED & STARTING
   -> PostgreSQL mulai inisialisasi...

2. Healthcheck STARTS (setelah start_period = 10s)
   -> Attempt 1: pg_isready -U postgres (exit code != 0)
   -> Tunggu 5s (interval)...
   -> Attempt 2: pg_isready -U postgres (exit code = 0)

3. Container db ditandai STATUS: (healthy)

4. depends_on service_healthy TERPENUHI
   -> Container api mulai dijalankan
   -> API berhasil koneksi ke database!
```

### Cek Status

```bash
docker compose ps db
docker inspect db-postgres --format "{{json .State.Health}}"
```

---

## Struktur Project

### Directory Layout

```
permana-praktikum-docker/
│
├── 📄 README.md                          # Dokumentasi (Bahasa Indonesia)
├── 📄 README.en.md                       # Dokumentasi (English)
├── 📄 PLAN.md                            # Project plan
├── 📄 RINGKASAN.md                       # Ringkasan hasil & kesimpulan
├── 📄 docker-compose.yml                 # Default setup (tanpa nginx)
├── 📄 docker-compose-with-nginx.yml      # Setup dengan load balancer
├── 📄 nginx.conf                         # Konfigurasi Nginx
├── 📄 barangdb-backup.tar.gz             # File backup database
│
├── 📁 api/                               # Backend API Service
│   ├── 📄 app.py                         # Flask API application
│   ├── 📄 Dockerfile                     # Docker image untuk API
│   └── 📄 requirements.txt               # Python dependencies
│
└── 📁 web/                               # Frontend Web Service
    ├── 📄 app.py                         # Flask web application
    ├── 📄 Dockerfile                     # Docker image untuk web
    ├── 📄 requirements.txt               # Python dependencies
    └── 📁 templates/
        └── 📄 index.html                 # HTML template

┌─────────────────────────────────────────────────────┐
│               DOCKER NETWORKS                       │
│  backend  ─── db, api                               │
│  frontend ─── web, api                              │
└─────────────────────────────────────────────────────┘
```

### File Descriptions

| File | Deskripsi |
|------|-----------|
| **docker-compose.yml** | Definisi services: web, api, db + network backend/frontend |
| **docker-compose-with-nginx.yml** | Menambah Nginx sebagai load balancer |
| **nginx.conf** | Konfigurasi Nginx (upstream, round-robin) |
| **api/app.py** | REST API endpoints (CRUD operations) |
| **api/Dockerfile** | Build image untuk API container (python:3.9-slim) |
| **web/app.py** | Web application dengan form interaktif |
| **web/Dockerfile** | Build image untuk web container (python:3.9-slim) |
| **web/templates/index.html** | Frontend HTML interface dengan modal edit |

---

## Load Balancer

### Konsep

**Load Balancer** adalah komponen yang mendistribusikan traffic secara merata ke multiple backend instances.

**Masalah tanpa Load Balancer (sticky routing):**
```
Request 1 → API-1 ✅
Request 2 → API-2 ✅
Request 3 → API-2 (sticky)
Request 4 → API-2 (sticky)
Request 5 → API-2 (sticky)
Distribusi: API-1 = 20%, API-2 = 80% ❌
```

**Solusi dengan Load Balancer (Nginx Round-Robin):**
```
Web → Nginx (Round-Robin)
      ├→ API-1 (50% traffic) ✅
      └→ API-2 (50% traffic) ✅
```

### Implementasi Nginx

File `nginx.conf` mengkonfigurasi:

```nginx
upstream api_backend {
    server api:8080;  # Auto-resolve ke semua API instances
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://api_backend;
    }
}
```

### Menggunakan Load Balancer

```bash
# Start dengan Nginx
docker compose -f docker-compose-with-nginx.yml up -d --scale api=2

# Nginx akan otomatis:
# ✅ Detect API-1 dan API-2
# ✅ Distribute traffic 50-50 (round-robin)
# ✅ Handle failover (jika 1 instance down)
```

---

## Scaling

### Horizontal Scaling (Add More Instances)

```bash
# Scale API menjadi 2 instances
docker compose up -d --scale api=2

# Scale menjadi 3 instances
docker compose up -d --scale api=3

# Kembali ke 1 instance
docker compose up -d --scale api=1
```

### Monitoring Scaled Instances

```bash
# Lihat semua instances
docker compose ps

# Lihat logs semua API instances
docker compose logs api

# Lihat logs specific instance
docker compose logs api-1
docker compose logs api-2

# Monitor real-time
docker stats
```

### Best Practices

1. **Mulai dengan 1 instance** untuk testing
2. **Gunakan load balancer** sebelum scale > 1
3. **Monitor resource usage** (CPU, Memory)
4. **Set resource limits** di docker-compose.yml jika perlu
5. **Test failover** dengan stop satu instance:
   ```bash
   docker compose stop api-1
   # Verifikasi traffic masih lancar via API-2
   ```

---

## Troubleshooting

### Error: "Cannot connect to database"

```bash
# 1. Check database status
docker compose ps db

# 2. Lihat logs database
docker compose logs db

# 3. Cek healthcheck database
docker inspect db-postgres --format "{{json .State.Health}}"

# 4. Restart services
docker compose restart
```

### Error: "Address already in use"

```bash
# Cek port yang sudah terpakai
netstat -ano | findstr :<PORT>    # Windows
lsof -i :<PORT>                   # Mac/Linux

# Opsi 1: Stop service yang menggunakan port
docker ps
docker stop <CONTAINER_ID>

# Opsi 2: Hapus port mapping, gunakan expose internal saja
# (seperti konfigurasi scaling di project ini)
```

### Error: "Web tidak bisa koneksi ke API"

```bash
# 1. Pastikan both services running
docker compose ps

# 2. Check network connectivity
docker compose exec web curl http://api:8080/barang

# 3. Check Docker network
docker network ls
docker network inspect permana-praktikum-docker_backend
docker network inspect permana-praktikum-docker_frontend

# 4. Restart services
docker compose restart
```

### Container Stuck/Slow

```bash
# 1. Check resource usage
docker stats

# 2. Lihat logs error
docker compose logs

# 3. Restart problematic container
docker compose restart <service_name>

# 4. Nuclear option: clean restart
docker compose down -v
docker compose up -d
```

### Data Loss

```bash
# Backup database:
docker run --rm \
  -v permana-praktikum-docker_postgres_data:/data \
  -v ${PWD}:/backup alpine \
  tar czf /backup/barangdb-backup.tar.gz -C /data .

# Restore:
docker run --rm \
  -v permana-praktikum-docker_postgres_data:/data \
  -v ${PWD}:/backup alpine \
  tar xzf /backup/barangdb-backup.tar.gz -C /data
```

---

## Dokumentasi Lengkap

Project ini menyediakan dokumentasi detail dalam file-file berikut:

| File | Bahasa | Deskripsi |
|------|--------|-----------|
| **README.md** | 🇮🇩 Indonesia | Dokumentasi utama (file ini) |
| **README.en.md** | 🇬🇧 English | Dokumentasi versi Bahasa Inggris |
| **PLAN.md** | 🇮🇩 Indonesia | Project plan & timeline |
| **RINGKASAN.md** | 🇮🇩 Indonesia | Ringkasan hasil & kesimpulan semua tugas |

---

## Quick Command Reference

### Build & Start
```bash
docker compose up -d                         # Start all services
docker compose up -d --scale api=2           # Start dengan 2 API instances
docker compose -f docker-compose-with-nginx.yml up -d  # Dengan Nginx
```

### Network
```bash
docker network ls                            # List semua network
docker network inspect <nama_network>        # Detail network
docker compose exec web getent hosts api     # Cek DNS resolve
```

### Monitoring
```bash
docker compose ps                            # List all containers
docker compose logs -f                       # Follow logs
docker stats                                 # Monitor resources
docker compose exec db psql -U postgres -d barangdb  # Database CLI
```

### Testing
```bash
docker compose exec api-1 curl http://localhost:8080/barang  # Test API
curl http://localhost:8000                                    # Test Web
```

### Healthcheck
```bash
docker compose ps db                          # Cek status healthy
docker inspect db-postgres --format "{{json .State.Health}}"  # Detail health
docker compose logs api --tail=20             # Cek startup logs
```

### Backup & Restore
```bash
docker run --rm -v permana-praktikum-docker_postgres_data:/data -v ${PWD}:/backup alpine tar czf /backup/barangdb-backup.tar.gz -C /data .   # Backup
docker run --rm -v permana-praktikum-docker_postgres_data:/data -v ${PWD}:/backup alpine tar xzf /backup/barangdb-backup.tar.gz -C /data .  # Restore
```

### Maintenance
```bash
docker compose restart                        # Restart all services
docker compose restart api-1                  # Restart specific service
docker compose down                           # Stop all (keep data)
docker compose down -v                        # Stop all (remove data)
```

### Scaling
```bash
docker compose up -d --scale api=2            # Scale to 2 instances
docker compose up -d --scale api=1            # Scale down to 1
```

---

## Key Learnings

| Konsep | Pelajaran Utama |
|--------|-----------------|
| **Network Isolation** | Pisahkan layer aplikasi ke network berbeda untuk security dan isolation yang lebih baik |
| **Volume Backup** | Backup dengan tar.gz container ephemeral adalah cara aman untuk backup data persistent |
| **Healthcheck** | Gunakan `condition: service_healthy` untuk memastikan dependency benar-benar siap |
| **Horizontal Scaling** | Scale container mudah, namun diperlukan load balancer untuk distribusi yang efektif |
| **Stateless Design** | Desain API stateless adalah prinsip kunci untuk cloud-native dan horizontal scaling |

---

## Author & License

**Nama**: Permana Rifky Anugerah  
**NIM**: 23083000012  
**Project**: UTS Komputasi Awan (Cloud Computing)  
**Course**: Cloud Computing Assignment  
**Technology Stack**: Docker, Docker Compose, Flask, PostgreSQL 15 Alpine, Nginx  

---

## Summary

Aplikasi ini mengdemonstrasikan core concepts dari Cloud Computing:

✅ **Containerization** — Encapsulation aplikasi dalam container  
✅ **Microservices** — Separation of concerns (Web ≠ API)  
✅ **Network Isolation** — Backend/Frontend network separation  
✅ **Orchestration** — Automated container management  
✅ **Scalability** — Easy horizontal scaling  
✅ **Load Balancing** — Intelligent traffic distribution  
✅ **Healthcheck** — Service dependency management  
✅ **Backup & Restore** — Data persistence & recovery  
✅ **Resilience** — Automatic failover capabilities  

---

## Perlu Bantuan?

1. **Baca dokumentasi lengkap** di folder project
2. **Check Docker logs** untuk debug informasi
3. **Lihat command reference** di atas untuk test dan maintenance
4. **Baca README.en.md** untuk versi Bahasa Inggris
5. **Lihat RINGKASAN.md** untuk ringkasan tugas dan kesimpulan

Happy learning! 🚀
