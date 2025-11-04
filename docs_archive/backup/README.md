# Système de Backup ULC-ICAM

Stratégie de sauvegarde complète et sécurisée pour le système ULC-ICAM.

## 🎯 Objectifs

- **Backup complet** de la base de données chaque semaine
- **Backup incrémentiel** de la base de données chaque jour  
- **Sauvegarde quotidienne** des fichiers étudiants
- **Rotation automatique** des sauvegardes (30 jours)
- **Chiffrement** au repos et en transit
- **Tests réguliers** de restauration

## 📁 Structure

```
backup/
├── backup_config.py          # Configuration centralisée
├── backup_manager.py         # Gestionnaire principal
├── backup_scheduler.py       # Planificateur de tâches
├── cloud_providers.py        # Adaptateurs cloud
├── cron_scripts.sh           # Scripts d'automatisation
├── crontab_config            # Configuration cron
├── docker-compose.backup.yml # Déploiement Docker
├── Dockerfile.backup         # Image Docker
├── install_backup.sh         # Installation automatisée
└── requirements.backup.txt   # Dépendances Python
```

## 🚀 Installation

### Installation Locale (Serveur)

```bash
# Cloner les scripts
git clone <repo> /tmp/ulc-backup
cd /tmp/ulc-backup/backup

# Exécuter l'installation
sudo chmod +x install_backup.sh
sudo ./install_backup.sh

# Configurer les variables d'environnement
sudo nano /opt/ulc-icam/.env
```

### Installation Docker

```bash
# Configurer les variables d'environnement
cp .env.example .env
nano .env

# Démarrer les services
docker-compose -f docker-compose.backup.yml up -d
```

## ⚙️ Configuration

### Variables d'environnement (.env)

```bash
# Base de données
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ulc_icam_db
DB_USER=ulc_admin
DB_PASSWORD=your_password

# Stockage cloud (AWS S3)
CLOUD_PROVIDER=s3
CLOUD_BUCKET=ulc-icam-backups
CLOUD_REGION=us-east-1
CLOUD_ACCESS_KEY=your_access_key
CLOUD_SECRET_KEY=your_secret_key

# Répertoires
UPLOADS_DIR=/opt/ulc-icam/uploads
REPORTS_DIR=/opt/ulc-icam/reports
BACKUP_BASE_DIR=/opt/ulc-icam/backups

# Notifications
BACKUP_NOTIFICATION_EMAIL=admin@ulc-icam.cd
BACKUP_RETENTION_DAYS=30
```

### Fournisseurs Cloud Supportés

#### AWS S3
```bash
CLOUD_PROVIDER=s3
CLOUD_BUCKET=ulc-icam-backups
CLOUD_REGION=us-east-1
CLOUD_ACCESS_KEY=AKIA...
CLOUD_SECRET_KEY=...
```

#### Azure Blob Storage
```bash
CLOUD_PROVIDER=azure
CLOUD_CONTAINER=ulc-icam-backups
CLOUD_ACCOUNT_NAME=ulcicam
CLOUD_ACCOUNT_KEY=...
```

#### Google Cloud Storage
```bash
CLOUD_PROVIDER=gcp
CLOUD_BUCKET=ulc-icam-backups
CLOUD_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
```

## 🔄 Utilisation

### Commandes Manuelles

```bash
# Backup quotidien
python backup_scheduler.py daily

# Backup hebdomadaire complet
python backup_scheduler.py weekly

# Test de restauration
python backup_scheduler.py test

# Restauration depuis un backup
python backup_scheduler.py restore --file /path/to/backup.enc
```

### Planification Automatique

Les tâches sont automatiquement planifiées via cron :

- **02:00** - Backup quotidien (incrémentiel DB + fichiers)
- **01:00 Dimanche** - Backup hebdomadaire complet
- **03:00 1er du mois** - Test mensuel de restauration

## 🔒 Sécurité

### Chiffrement
- **Clé de chiffrement** générée automatiquement
- **Chiffrement AES-256** via Fernet (cryptography)
- **Stockage sécurisé** des clés (permissions 600)

### Accès
- **Utilisateur dédié** `ulc-backup`
- **Permissions restreintes** sur les répertoires
- **Variables d'environnement** protégées

### Transport
- **HTTPS/TLS** pour les uploads cloud
- **Authentification** par clés API

## 📊 Monitoring

### Logs
```bash
# Logs principaux
tail -f /var/log/ulc-icam-backup.log

# Logs système
journalctl -u ulc-backup.service -f
```

### Notifications
- **Email automatique** en cas de succès/échec
- **Alertes d'espace disque** (>85%)
- **Rapports mensuels** de test de restauration

### Métriques (Docker)
- **Prometheus** pour le monitoring
- **Grafana** pour les tableaux de bord
- **Alertmanager** pour les notifications

## 🔧 Maintenance

### Vérifications Régulières

```bash
# Vérifier l'espace disque
df -h /opt/ulc-icam/backups

# Lister les backups récents
ls -la /opt/ulc-icam/backups/database/

# Tester la connectivité cloud
aws s3 ls s3://ulc-icam-backups/

# Vérifier les tâches cron
crontab -u ulc-backup -l
```

### Rotation des Backups

```bash
# Nettoyage manuel des anciens backups
find /opt/ulc-icam/backups -name "*.enc" -mtime +30 -delete

# Nettoyage cloud (AWS S3)
aws s3 ls s3://ulc-icam-backups/ --recursive | \
  awk '$1 < "'$(date -d '30 days ago' '+%Y-%m-%d')'" {print $4}' | \
  xargs -I {} aws s3 rm s3://ulc-icam-backups/{}
```

## 🚨 Procédure de Restauration

### Restauration Complète

1. **Arrêter l'application**
```bash
systemctl stop ulc-icam
```

2. **Sauvegarder l'état actuel**
```bash
pg_dump ulc_icam_db > /tmp/current_backup.sql
```

3. **Restaurer depuis le backup**
```bash
python backup_scheduler.py restore --file /path/to/backup.enc
```

4. **Vérifier la restauration**
```bash
psql -d ulc_icam_db -c "SELECT COUNT(*) FROM users;"
```

5. **Redémarrer l'application**
```bash
systemctl start ulc-icam
```

### Restauration Partielle (Fichiers)

```bash
# Déchiffrer et extraire l'archive
python -c "
from backup_manager import BackupManager
manager = BackupManager()
manager._decrypt_and_decompress('/path/to/files_backup.enc')
"

# Extraire vers le répertoire cible
tar -xzf /tmp/decrypted_files.tar.gz -C /opt/ulc-icam/
```

## 📋 Checklist de Déploiement

### Pré-déploiement
- [ ] Serveur configuré avec PostgreSQL/MySQL
- [ ] Utilisateur de base de données créé
- [ ] Stockage cloud configuré (S3/Azure/GCP)
- [ ] Certificats SSL/TLS en place
- [ ] Notifications email configurées

### Post-déploiement
- [ ] Test de backup quotidien
- [ ] Test de backup hebdomadaire
- [ ] Test de restauration
- [ ] Vérification des notifications
- [ ] Monitoring opérationnel
- [ ] Documentation mise à jour

## 🆘 Dépannage

### Erreurs Communes

**Erreur de connexion DB**
```bash
# Vérifier la connectivité
pg_isready -h localhost -p 5432

# Tester les credentials
psql -h localhost -U ulc_admin -d ulc_icam_db -c "SELECT 1;"
```

**Erreur d'upload cloud**
```bash
# Tester AWS CLI
aws s3 ls s3://ulc-icam-backups/

# Vérifier les permissions
aws iam get-user
```

**Espace disque insuffisant**
```bash
# Nettoyer les anciens backups
find /opt/ulc-icam/backups -name "*.enc" -mtime +7 -delete

# Vérifier l'espace
df -h /opt/ulc-icam/backups
```

## 📞 Support

- **Documentation** : Ce README
- **Logs** : `/var/log/ulc-icam-backup.log`
- **Contact** : admin@ulc-icam.cd
- **Issues** : Créer un ticket dans le système de gestion