# YT Telegram Downloader (Render deployable)

**Use responsibly. Only download content you have rights to.**

## What this repo
A simple Telegram bot that accepts YouTube links and sends back the downloaded file. Deployable on Render with Docker.

## Files
- `app.py` — Flask app + webhook handler
- `downloader.py` — background download & upload worker
- `utils.py` — Telegram helper functions
- `Dockerfile`, `render.yaml` — for Render deployment

## Setup (GitHub -> Render)
1. Create a Telegram bot with @BotFather and get the `TELEGRAM_BOT_TOKEN`.
2. Create a GitHub repo and push this project.
3. On Render:
   - Create a new Web Service from GitHub (or use `render.yaml`).
   - Choose Docker, connect repo.
   - In Render dashboard -> Environment, add:
     - `TELEGRAM_BOT_TOKEN` = your token
     - (optional) `WEBHOOK_URL` = `https://<your-render-service>.onrender.com/webhook`
   - Deploy.

4. If you didn't set `WEBHOOK_URL`, set webhook manually once:
