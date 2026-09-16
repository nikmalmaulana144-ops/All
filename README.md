# ACX WEB — AlwaysCodex Client

Web interface untuk 60+ endpoint AlwaysCodex. by malz codex.

## Deploy ke Railway

1. Push folder ini ke GitHub repo
2. Buka railway.app → New Project → Deploy from GitHub
3. Pilih repo lu → otomatis detect Python
4. Selesai — dapet URL public

## Deploy ke Render

1. Push ke GitHub
2. Buka render.com → New Web Service
3. Connect repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Deploy

## Run lokal (Termux)

```bash
pip install flask gunicorn
python app.py
# buka http://localhost:8000