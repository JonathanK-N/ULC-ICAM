# Guide de Sauvegarde - Système ULC-ICAM

## Table des Matières
1. [Vue d'Ensemble](#vue-densemble)
2. [Configuration Initiale](#configuration-initiale)
3. [Types de Sauvegarde](#types-de-sauvegarde)
4. [Planification Automatique](#planification-automatique)
5. [Sauvegarde Manuelle](#sauvegarde-manuelle)
6. [Restauration](#restauration)
7. [Stockage Cloud](#stockage-cloud)
8. [Surveillance et Maintenance](#surveillance-et-maintenance)
9. [Procédures d'Urgence](#procédures-durgence)

## Vue d'Ensemble

Le système de sauvegarde ULC-ICAM assure la protection complète des données académiques avec :
- **Chiffrement AES-256** : Sécurité maximale des données
- **Sauvegarde multi-niveaux** : Complète et incrémentale
- **Stockage cloud** : AWS S3, Google Cloud, Azure
- **Planification automatique** : Sauvegardes programmées
- **Restauration rapide** : Récupération en cas de problème

### Architecture de Sauvegarde
```
Données Source
├── Base de données SQLite
├── Fichiers uploadés
├── Logs système
├── Configuration
└── Code source

Sauvegarde
├── Chiffrement AES-256
├── Compression GZIP
├── Stockage local
└── Upload cloud automatique
```

## Configuration Initiale

### 1. Configuration de Base
Éditez `backup/backup_config.py` :
```python
BACKUP_CONFIG = {
    'encryption': {
        'enabled': True,
        'key_file': 'backup/encryption.key',
        'algorithm': 'AES-256'
    },
    'retention': {
        'local_days': 30,
        'cloud_days': 90,
        'full_backups': 4,
        'incremental_backups': 30
    },
    'schedule': {
        'full_backup': '0 2 * * 0',      # Dimanche 2h00
        'incremental': '0 2 * * 1-6',    # Lundi-Samedi 2h00
        'cleanup': '0 3 * * 0'           # Dimanche 3h00
    }
}
```

### 2. Génération de la Clé de Chiffrement
```bash
# Générer une clé de chiffrement sécurisée
cd backup/
python -c "
from cryptography.fernet import Fernet
key = Fernet.generate_key()
with open('encryption.key', 'wb') as f:
    f.write(key)
print('Clé de chiffrement générée')
"

# Sécuriser la clé
chmod 600 encryption.key
```

### 3. Configuration des Fournisseurs Cloud

#### AWS S3
```python
AWS_CONFIG = {
    'access_key_id': 'VOTRE_ACCESS_KEY',
    'secret_access_key': 'VOTRE_SECRET_KEY',
    'region': 'eu-west-1',
    'bucket_name': 'ulc-icam-backups',
    'storage_class': 'STANDARD_IA'
}
```

#### Google Cloud Storage
```python
GCP_CONFIG = {
    'service_account_file': 'path/to/service-account.json',
    'bucket_name': 'ulc-icam-backups',
    'project_id': 'votre-projet-gcp',
    'storage_class': 'NEARLINE'
}
```

#### Azure Blob Storage
```python
AZURE_CONFIG = {
    'connection_string': 'DefaultEndpointsProtocol=https;...',
    'container_name': 'ulc-icam-backups',
    'storage_tier': 'Cool'
}
```

## Types de Sauvegarde

### 1. Sauvegarde Complète
Inclut toutes les données du système :
- **Base de données** : Dump complet SQLite
- **Fichiers uploadés** : Tous les documents étudiants
- **Configuration** : Paramètres système
- **Logs** : Historique complet
- **Code source** : Version actuelle

```bash
# Lancer une sauvegarde complète
python backup/backup_manager.py --full

# Avec destination spécifique
python backup/backup_manager.py --full --destination s3
```

### 2. Sauvegarde Incrémentale
Sauvegarde uniquement les modifications depuis la dernière sauvegarde :
- **Nouveaux fichiers** : Ajoutés depuis la dernière sauvegarde
- **Fichiers modifiés** : Changements détectés
- **Métadonnées** : Informations de changement
- **Optimisation** : Taille réduite et rapidité

```bash
# Lancer une sauvegarde incrémentale
python backup/backup_manager.py --incremental

# Avec compression maximale
python backup/backup_manager.py --incremental --compress-level 9
```

### 3. Sauvegarde de Configuration
Sauvegarde uniquement les paramètres système :
- **Fichiers de configuration** : config.py, .env
- **Structure de la base** : Schéma sans données
- **Paramètres utilisateur** : Préférences système
- **Clés et certificats** : Éléments de sécurité

```bash
# Sauvegarde de configuration
python backup/backup_manager.py --config-only
```

## Planification Automatique

### 1. Configuration du Planificateur
```bash
# Initialiser le planificateur
cd backup/
python backup_scheduler.py --setup

# Vérifier la configuration
python backup_scheduler.py --status
```

### 2. Planification par Défaut
- **Sauvegarde complète** : Dimanche 2h00
- **Sauvegarde incrémentale** : Lundi-Samedi 2h00
- **Nettoyage** : Dimanche 3h00
- **Vérification** : Quotidienne 4h00

### 3. Crontab (Linux/macOS)
```bash
# Éditer le crontab
crontab -e

# Ajouter les tâches
0 2 * * 0 /chemin/vers/app/backup/weekly_backup.sh
0 2 * * 1-6 /chemin/vers/app/backup/daily_backup.sh
0 3 * * 0 /chemin/vers/app/backup/cleanup.sh
0 4 * * * /chemin/vers/app/backup/verify.sh
```

### 4. Tâche Planifiée Windows
```batch
# Créer une tâche planifiée
schtasks /create /tn "ULC-ICAM Backup" /tr "C:\chemin\vers\app\backup\backup.bat" /sc daily /st 02:00

# Vérifier les tâches
schtasks /query /tn "ULC-ICAM Backup"
```

## Sauvegarde Manuelle

### 1. Interface Web
1. **Connexion administrateur** : Tableau de bord admin
2. **Section Sauvegarde** : Cliquez sur "Sauvegarde"
3. **Sélection du type** : Complète, Incrémentale, Configuration
4. **Destination** : Local, AWS S3, Google Cloud, Azure
5. **Lancement** : Cliquez "Démarrer la sauvegarde"
6. **Suivi** : Barre de progression en temps réel

### 2. Ligne de Commande
```bash
# Sauvegarde complète avec upload cloud
python backup/backup_manager.py --full --upload-cloud

# Sauvegarde avec notification email
python backup/backup_manager.py --incremental --notify

# Sauvegarde avec vérification
python backup/backup_manager.py --full --verify

# Sauvegarde silencieuse
python backup/backup_manager.py --incremental --quiet
```

### 3. Scripts Personnalisés
```bash
#!/bin/bash
# backup_custom.sh

# Variables
BACKUP_DIR="/backups/ulc-icam"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/ulc-icam-backup.log"

# Fonction de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Sauvegarde
log "Début de la sauvegarde personnalisée"
python /chemin/vers/app/backup/backup_manager.py --full --destination local
log "Sauvegarde terminée"

# Upload cloud
log "Upload vers le cloud"
python /chemin/vers/app/backup/cloud_upload.py --latest
log "Upload terminé"
```

## Restauration

### 1. Préparation à la Restauration
```bash
# Arrêter l'application
sudo systemctl stop ulc-icam
# ou
pkill -f "python app.py"

# Sauvegarder l'état actuel
cp ulc_icam.db ulc_icam.db.pre-restore
cp -r uploads uploads.pre-restore
```

### 2. Restauration Complète
```bash
# Lister les sauvegardes disponibles
python backup/restore_manager.py --list

# Restaurer une sauvegarde spécifique
python backup/restore_manager.py --restore backup_20241215_020000.tar.gz.enc

# Restauration avec vérification
python backup/restore_manager.py --restore backup_20241215_020000.tar.gz.enc --verify
```

### 3. Restauration Sélective
```bash
# Restaurer uniquement la base de données
python backup/restore_manager.py --restore-db backup_20241215_020000.tar.gz.enc

# Restaurer uniquement les fichiers
python backup/restore_manager.py --restore-files backup_20241215_020000.tar.gz.enc

# Restaurer la configuration
python backup/restore_manager.py --restore-config backup_20241215_020000.tar.gz.enc
```

### 4. Vérification Post-Restauration
```bash
# Vérifier l'intégrité de la base de données
sqlite3 ulc_icam.db "PRAGMA integrity_check;"

# Tester la connectivité
python -c "from app import db; print('DB OK' if db.engine.execute('SELECT 1').scalar() == 1 else 'DB ERROR')"

# Redémarrer l'application
python app.py
```

## Stockage Cloud

### 1. Configuration AWS S3
```python
# backup/cloud_providers.py
class S3Provider:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key'],
            region_name=AWS_CONFIG['region']
        )
    
    def upload(self, local_file, remote_key):
        self.client.upload_file(
            local_file, 
            AWS_CONFIG['bucket_name'], 
            remote_key,
            ExtraArgs={'StorageClass': AWS_CONFIG['storage_class']}
        )
```

### 2. Synchronisation Multi-Cloud
```bash
# Upload vers tous les fournisseurs configurés
python backup/cloud_sync.py --all

# Upload vers un fournisseur spécifique
python backup/cloud_sync.py --provider s3

# Vérification de la synchronisation
python backup/cloud_sync.py --verify
```

### 3. Gestion des Coûts
- **Classe de stockage** : Standard-IA, Nearline, Cool
- **Cycle de vie** : Archivage automatique après 90 jours
- **Compression** : Réduction de 60-80% de la taille
- **Déduplication** : Évite les doublons

## Surveillance et Maintenance

### 1. Monitoring des Sauvegardes
```bash
# Statut des dernières sauvegardes
python backup/backup_monitor.py --status

# Rapport détaillé
python backup/backup_monitor.py --report

# Alertes par email
python backup/backup_monitor.py --check-alerts
```

### 2. Logs de Sauvegarde
```bash
# Consulter les logs
tail -f logs/backup.log

# Logs d'erreur uniquement
grep ERROR logs/backup.log

# Statistiques de sauvegarde
python backup/backup_stats.py --summary
```

### 3. Tests de Restauration
```bash
# Test automatique mensuel
python backup/test_restore.py --monthly

# Test complet avec environnement temporaire
python backup/test_restore.py --full-test

# Rapport de test
python backup/test_restore.py --report
```

### 4. Maintenance Préventive
```bash
# Nettoyage des anciennes sauvegardes
python backup/cleanup.py --older-than 30

# Optimisation de l'espace
python backup/optimize.py --compress-old

# Vérification d'intégrité
python backup/verify.py --all-backups
```

## Procédures d'Urgence

### 1. Perte Complète du Système
```bash
# 1. Installer un nouveau système
# 2. Installer l'application ULC-ICAM
# 3. Télécharger la dernière sauvegarde
python backup/emergency_restore.py --download-latest

# 4. Restaurer complètement
python backup/emergency_restore.py --full-restore

# 5. Vérifier et redémarrer
python backup/emergency_restore.py --verify-and-start
```

### 2. Corruption de Base de Données
```bash
# Diagnostic
sqlite3 ulc_icam.db "PRAGMA integrity_check;"

# Restauration d'urgence
python backup/emergency_restore.py --db-only --latest

# Vérification
python -c "from app import db; db.create_all(); print('DB restored')"
```

### 3. Récupération Partielle
```bash
# Récupérer uniquement les fichiers récents
python backup/partial_restore.py --files --since "2024-12-01"

# Récupérer les données d'un cours spécifique
python backup/partial_restore.py --course-data --course-id 123

# Récupérer les soumissions d'un étudiant
python backup/partial_restore.py --student-data --student-id 456
```

### 4. Contact d'Urgence
En cas de problème critique :
1. **Email** : emergency@ulc-icam.edu.km
2. **Téléphone** : +269 XX XX XX XX
3. **Documentation** : Consultez ce guide
4. **Support 24/7** : Disponible pour les urgences

## Bonnes Pratiques

### 1. Sécurité
- **Chiffrement obligatoire** : Toutes les sauvegardes
- **Clés sécurisées** : Stockage séparé des données
- **Accès restreint** : Permissions minimales
- **Audit régulier** : Vérification des accès

### 2. Performance
- **Planification intelligente** : Heures creuses
- **Compression optimale** : Équilibre taille/temps
- **Parallélisation** : Upload simultané
- **Monitoring** : Surveillance des performances

### 3. Fiabilité
- **Tests réguliers** : Vérification des restaurations
- **Redondance** : Multiple destinations
- **Vérification** : Intégrité des sauvegardes
- **Documentation** : Procédures à jour

---

**Support Sauvegarde** : backup@ulc-icam.edu.km  
**Urgences 24/7** : emergency@ulc-icam.edu.km  
**Documentation mise à jour** : Décembre 2024