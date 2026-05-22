#!/bin/bash
set -e

PROJECT_DIR="/home/dev/usazd"
PROJECT_NAME="USAZD"
DOMAIN="usazd.xpowl.xyz"
SERVICE_NAME="gunicorn-usazd"
VENV_PATH="$PROJECT_DIR/venv"
SOCKET_PATH="$PROJECT_DIR/gunicorn.sock"
CURRENT_USER=$(whoami)

echo "========================================="
echo "  Деплой $PROJECT_NAME на $DOMAIN"
echo "========================================="

echo "[1/7] Системные пакеты..."
sudo apt-get update -qq
sudo apt-get install -y -qq nginx certbot python3-certbot-nginx python3-pip python3-venv

echo "[2/7] Зависимости Python..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi
"$VENV_PATH/bin/pip" install --upgrade pip -q
"$VENV_PATH/bin/pip" install -r "$PROJECT_DIR/requirements.txt" -q
"$VENV_PATH/bin/pip" install gunicorn -q

echo "[3/7] Статика и мигирации..."
"$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" migrate --noinput
"$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" collectstatic --noinput --clear

echo "[4/7] Права доступа..."
sudo chown -R $CURRENT_USER:www-data "$PROJECT_DIR"

sudo find "$PROJECT_DIR" -not -path "*/venv/*" -type d -exec chmod 755 {} +
sudo find "$PROJECT_DIR" -not -path "*/venv/*" -type f -exec chmod 644 {} +
sudo chmod +x "$PROJECT_DIR/manage.py" || true

sudo mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/media"
sudo find "$PROJECT_DIR/logs" "$PROJECT_DIR/media" -type d -exec chmod 775 {} +
sudo find "$PROJECT_DIR/logs" "$PROJECT_DIR/media" -type f -exec chmod 664 {} +

if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    sudo chown $CURRENT_USER:www-data "$PROJECT_DIR/db.sqlite3"
    sudo chmod 664 "$PROJECT_DIR/db.sqlite3"
    sudo chmod 775 "$PROJECT_DIR" 
fi

echo "[5/7] systemd сервис..."
CPU_CORES=$(nproc)
WORKERS=$((CPU_CORES * 2 + 1))

sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null << EOF
[Unit]
Description=gunicorn daemon for $PROJECT_NAME
After=network.target

[Service]
User=$CURRENT_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="RUN_MAIN=true"
Environment="DJANGO_SETTINGS_MODULE=$PROJECT_NAME.settings"
ExecStart=$VENV_PATH/bin/gunicorn \\
    --access-logfile $PROJECT_DIR/logs/gunicorn-access.log \\
    --error-logfile $PROJECT_DIR/logs/gunicorn-error.log \\
    --workers $WORKERS \\
    --umask 007 \\
    --bind unix:$SOCKET_PATH \\
    $PROJECT_NAME.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "[6/7] Nginx..."
sudo tee "/etc/nginx/sites-available/$DOMAIN" > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /static/ {
        alias $PROJECT_DIR/static/;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        proxy_pass http://unix:$SOCKET_PATH;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
    }
}
EOF

if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    sudo ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
fi

if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo rm "/etc/nginx/sites-enabled/default"
fi

sudo nginx -t && sudo systemctl reload nginx

echo "[7/7] SSL..."
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@xpowl.xyz --redirect || {
        echo "Certbot упал. Проверь DNS для $DOMAIN"
        exit 1
    }
else
    echo "SSL уже есть"
fi

echo ""
echo "========================================="
echo "  Готово: https://$DOMAIN"
echo "========================================="
