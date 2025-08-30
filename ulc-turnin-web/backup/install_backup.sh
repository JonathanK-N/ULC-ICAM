#!/bin/bash
# ULC-ICAM TURNIN SYSTEM - INSTALLATION BACKUP
# Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
# Tous droits réservés - Logiciel Propriétaire
# 
# Script d'installation du système de backup ULC-ICAM
# UTILISATION RESTREINTE - Voir LICENSE pour les conditions

set -e

echo "🚀 Installation du système de backup ULC-ICAM"

# Variables
INSTALL_DIR="/opt/ulc-icam"
BACKUP_DIR="$INSTALL_DIR/backup"
BACKUP_DATA_DIR="$INSTALL_DIR/backups"
SERVICE_USER="ulc-backup"

# Vérification des privilèges root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Ce script doit être exécuté en tant que root"
   exit 1
fi

# Création de l'utilisateur de service
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "👤 Création de l'utilisateur $SERVICE_USER"
    useradd -r -s /bin/bash -d $INSTALL_DIR $SERVICE_USER
fi

# Création des répertoires
echo "📁 Création des répertoires"
mkdir -p $BACKUP_DIR
mkdir -p $BACKUP_DATA_DIR/{database,files,logs}
mkdir -p /var/log/ulc-icam

# Installation des dépendances système
echo "📦 Installation des dépendances"
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y python3 python3-pip python3-venv postgresql-client mysql-client cron mailutils
elif command -v yum &> /dev/null; then
    # RHEL/CentOS
    yum install -y python3 python3-pip postgresql mysql crontabs mailx
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y python3 python3-pip postgresql mysql crontabs mailx
fi

# Création de l'environnement virtuel Python
echo "🐍 Configuration de l'environnement Python"
python3 -m venv $INSTALL_DIR/venv
source $INSTALL_DIR/venv/bin/activate

# Installation des dépendances Python
pip install --upgrade pip
pip install -r requirements.backup.txt

# Copie des scripts
echo "📋 Installation des scripts"
cp *.py $BACKUP_DIR/
cp *.sh $BACKUP_DIR/
chmod +x $BACKUP_DIR/*.py $BACKUP_DIR/*.sh

# Configuration des permissions
echo "🔒 Configuration des permissions"
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chmod 700 $BACKUP_DATA_DIR
chmod 600 $BACKUP_DIR/*.py

# Configuration de la rotation des logs
echo "📝 Configuration de la rotation des logs"
cat > /etc/logrotate.d/ulc-icam-backup << EOF
/var/log/ulc-icam-backup.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
}
EOF

# Installation des tâches cron
echo "⏰ Installation des tâches cron"
crontab -u $SERVICE_USER crontab_config

# Création du fichier de configuration d'environnement
echo "⚙️  Création du fichier de configuration"
cat > $INSTALL_DIR/.env << EOF
# Configuration ULC-ICAM Backup
BACKUP_BASE_DIR=$BACKUP_DATA_DIR
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ulc_icam_db
DB_USER=ulc_admin
DB_PASSWORD=
UPLOADS_DIR=$INSTALL_DIR/uploads
REPORTS_DIR=$INSTALL_DIR/reports
LOGS_DIR=/var/log/ulc-icam
CLOUD_PROVIDER=s3
CLOUD_BUCKET=ulc-icam-backups
CLOUD_REGION=us-east-1
CLOUD_ACCESS_KEY=
CLOUD_SECRET_KEY=
BACKUP_NOTIFICATION_EMAIL=admin@ulc-icam.cd
BACKUP_RETENTION_DAYS=30
EOF

chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/.env
chmod 600 $INSTALL_DIR/.env

# Création du service systemd
echo "🔧 Création du service systemd"
cat > /etc/systemd/system/ulc-backup.service << EOF
[Unit]
Description=ULC-ICAM Backup Service
After=network.target postgresql.service

[Service]
Type=oneshot
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$BACKUP_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/python backup_scheduler.py daily
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Activation du service
systemctl daemon-reload
systemctl enable ulc-backup.service

# Test initial
echo "🧪 Test initial du système"
sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/python $BACKUP_DIR/backup_scheduler.py test

echo "✅ Installation terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Configurer les variables dans $INSTALL_DIR/.env"
echo "2. Tester le backup: sudo -u $SERVICE_USER $BACKUP_DIR/backup_scheduler.py daily"
echo "3. Vérifier les logs: tail -f /var/log/ulc-icam-backup.log"
echo "4. Configurer le stockage cloud dans .env"
echo ""
echo "📁 Répertoires importants:"
echo "   - Scripts: $BACKUP_DIR"
echo "   - Backups: $BACKUP_DATA_DIR"
echo "   - Config: $INSTALL_DIR/.env"
echo "   - Logs: /var/log/ulc-icam-backup.log"