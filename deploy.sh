#!/bin/bash
set -e

# ============================================
# Автоматический деплой USAZD
# ============================================

PROJECT_DIR="/home/dev/usazd"
PROJECT_NAME="USAZD"
DOMAIN="usazd.xpowl.xyz"
SERVICE_NAME="gunicorn-usazd"
VENV_PATH="$PROJECT_DIR/venv"
SOCKET_PATH="$PROJECT_DIR/gunicorn.sock"
STATIC_DIR="$PROJECT_DIR/static"
MEDIA_DIR="$PROJECT_DIR/media"
LOG_DIR="$PROJECT_DIR/logs"

echo "========================================="
echo "  Деплой $PROJECT_NAME на $DOMAIN"
echo "========================================="


echo "[1/8] Установка системных пакетов..."
sudo apt-get update -qq
sudo apt-get install -y -qq nginx certbot python3-certbot-nginx python3-pip python3-venv


echo "[2/8] Настройка виртуального окружения..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi
source "$VENV_PATH/bin/activate"
pip install --upgrade pip -q
pip install -r "$PROJECT_DIR/requirements.txt" -q
pip install gunicorn -q


echo "[3/8] Сбор статических файлов..."
python "$PROJECT_DIR/manage.py" collectstatic --noinput --clear


echo "[4/8] Применение миграций..."
python "$PROJECT_DIR/manage.py" migrate --noinput


echo "[5/8] Настройка прав доступа..."
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"
sudo chmod 600 "$PROJECT_DIR/db.sqlite3" 2>/dev/null || true
sudo mkdir -p "$LOG_DIR"
sudo chown -R www-data:www-data "$LOG_DIR"


echo "[6/8] Настройка systemd сервиса..."
sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null << 'SERVICEEOF'
[Unit]
Description=gunicorn daemon for USAZD project
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/dev/usazd
Environment="RUN_MAIN=true"
Environment="DJANGO_SETTINGS_MODULE=USAZD.settings"
ExecStart=/home/dev/usazd/venv/bin/gunicorn \
    --access-logfile - \
    --error-logfile - \
    --workers 1 \
    --bind unix:/home/dev/usazd/gunicorn.sock \
    USAZD.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"


echo "[7/8] Настройка Nginx..."
sudo tee "/etc/nginx/sites-available/$DOMAIN" > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name usazd.xpowl.xyz;

    location /static/ {
        alias /home/dev/usazd/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/dev/usazd/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/dev/usazd/gunicorn.sock;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
NGINXEOF

if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    sudo ln -s "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
fi

sudo nginx -t && sudo systemctl reload nginx


echo "[8/8] Настройка SSL сертификата..."
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@xpowl.xyz --redirect
else
    echo "SSL сертификат уже существует, пропускаем..."
fi

echo ""
echo "========================================="
echo "  Деплой завершён!"
echo "========================================="
echo "Сайт: https://$DOMAIN"
echo ""
echo "Полезные команды:"
echo "  Статус:      sudo systemctl status $SERVICE_NAME"
echo "  Логи:        sudo journalctl -u $SERVICE_NAME -f"
echo "  Перезапуск:  sudo systemctl restart $SERVICE_NAME"