## RAG Backend (FastAPI) – Document Upload & Listing

Fitur yang tersedia saat ini:
- `POST /documents`: upload dokumen (PDF/DOCX/HTML) → file disimpan ke local storage, metadata disimpan ke MySQL
- `GET /documents`: ambil semua dokumen

### Prasyarat
- Python 3.10+
- MySQL 8+

### Setup cepat
1. Install dependency:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Siapkan environment variables (lihat `env.example`).

3. Migrasi database (pilih salah satu):
- **Manual SQL**: jalankan `infrastructure/migrations/001_create_documents.sql`
- **Alembic (recommended)**:
  - Generate migration (jika belum ada):
    - `make migrate-revision MSG="create documents"`
  - Apply:
    - `make migrate-up`
  - Revert 1 step:
    - `make migrate-down`

4. Jalankan API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Contoh request
- Upload:

```bash
curl -F "file=@dataset/essay_sample_1.pdf" http://127.0.0.1:8000/documents
```

- List:

```bash
curl http://127.0.0.1:8000/documents
```
