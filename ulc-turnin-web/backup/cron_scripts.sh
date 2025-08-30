#!/bin/bash
# ULC-ICAM TURNIN SYSTEM - SCRIPTS CRON BACKUP
# Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
# Tous droits réservés - Logiciel Propriétaire
# 
# Scripts cron pour automatisation des backups ULC-ICAM
# UTILISATION RESTREINTE - Voir LICENSE pour les conditions

# Variables d'environnement
export BACKUP_BASE_DIR="/opt/ulc-icam/backups"
export DB_TYPE="postgresql"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="ulc_icam_db"
export DB_USER="ulc_admin"
export UPLOADS_DIR="/opt/ulc-icam/uploads"
export REPORTS_DIR="/opt/ulc-icam/reports"
export LOGS_DIR="/opt/ulc-icam/logs"
export CLOUD_PROVIDER="s3"
export CLOUD_BUCKET="ulc-icam-backups"

# Répertoire des scripts
SCRIPT_DIR="/opt/ulc-icam/backup"
PYTHON_ENV="/opt/ulc-icam/venv/bin/python"

# Fonction de logging
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> /var/log/ulc-icam-backup.log
}

# Backup quotidien (tous les jours à 2h00)
daily_backup() {
    log_message "Début backup quotidien"
    
    if $PYTHON_ENV $SCRIPT_DIR/backup_scheduler.py daily; then
        log_message "Backup quotidien réussi"
        
        # Notification de succès
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Backup quotidien ULC-ICAM terminé avec succès" | \
            mail -s "✅ Backup ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    else
        log_message "Échec backup quotidien"
        
        # Notification d'erreur
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Échec du backup quotidien ULC-ICAM. Vérifiez les logs." | \
            mail -s "❌ Erreur Backup ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    fi
}

# Backup hebdomadaire (dimanche à 1h00)
weekly_backup() {
    log_message "Début backup hebdomadaire"
    
    if $PYTHON_ENV $SCRIPT_DIR/backup_scheduler.py weekly; then
        log_message "Backup hebdomadaire réussi"
        
        # Test de restauration après backup hebdomadaire
        if $PYTHON_ENV $SCRIPT_DIR/backup_scheduler.py test; then
            log_message "Test de restauration réussi"
        else
            log_message "Échec test de restauration"
        fi
        
        # Notification
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Backup hebdomadaire ULC-ICAM terminé avec succès" | \
            mail -s "✅ Backup Hebdomadaire ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    else
        log_message "Échec backup hebdomadaire"
        
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Échec du backup hebdomadaire ULC-ICAM. Vérifiez les logs." | \
            mail -s "❌ Erreur Backup Hebdomadaire ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    fi
}

# Test mensuel de restauration (1er de chaque mois à 3h00)
monthly_test() {
    log_message "Début test mensuel de restauration"
    
    if $PYTHON_ENV $SCRIPT_DIR/backup_scheduler.py test; then
        log_message "Test mensuel de restauration réussi"
        
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Test mensuel de restauration ULC-ICAM réussi" | \
            mail -s "✅ Test Restauration ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    else
        log_message "Échec test mensuel de restauration"
        
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Échec du test mensuel de restauration ULC-ICAM. Action requise!" | \
            mail -s "🚨 URGENT - Échec Test Restauration ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    fi
}

# Vérification de l'espace disque
check_disk_space() {
    BACKUP_USAGE=$(df $BACKUP_BASE_DIR | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ $BACKUP_USAGE -gt 85 ]; then
        log_message "ALERTE: Espace disque backup à ${BACKUP_USAGE}%"
        
        if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
            echo "Espace disque des backups ULC-ICAM critique: ${BACKUP_USAGE}%" | \
            mail -s "🚨 ALERTE Espace Disque ULC-ICAM - $(date '+%Y-%m-%d')" $BACKUP_NOTIFICATION_EMAIL
        fi
    fi
}

# Exécution selon l'argument
case "$1" in
    "daily")
        daily_backup
        check_disk_space
        ;;
    "weekly")
        weekly_backup
        check_disk_space
        ;;
    "monthly_test")
        monthly_test
        ;;
    *)
        echo "Usage: $0 {daily|weekly|monthly_test}"
        exit 1
        ;;
esac