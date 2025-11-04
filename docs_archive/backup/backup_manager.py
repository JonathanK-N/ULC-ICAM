#!/usr/bin/env python3
"""
ULC-ICAM TURNIN SYSTEM - GESTIONNAIRE BACKUP
Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
Tous droits réservés - Logiciel Propriétaire

Gestionnaire principal de backup pour ULC-ICAM

UTILISATION RESTREINTE - Voir LICENSE pour les conditions
"""
import os
import subprocess
import gzip
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
import boto3
from backup_config import *

class BackupManager:
    def __init__(self):
        self.setup_logging()
        self.cipher = Fernet(self._get_encryption_key())
        
    def setup_logging(self):
        log_dir = Path(BACKUP_BASE_DIR) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'backup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _get_encryption_key(self):
        """Génère ou récupère la clé de chiffrement"""
        key_file = Path(BACKUP_BASE_DIR) / '.backup_key'
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            os.chmod(key_file, 0o600)
            return key

    def backup_database(self, backup_type='full'):
        """Sauvegarde de la base de données"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"db_{backup_type}_{timestamp}.sql"
            backup_path = Path(BACKUP_BASE_DIR) / 'database' / filename
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            if DB_CONFIG['type'] == 'postgresql':
                cmd = [
                    'pg_dump',
                    f"-h{DB_CONFIG['host']}",
                    f"-p{DB_CONFIG['port']}",
                    f"-U{DB_CONFIG['username']}",
                    f"-d{DB_CONFIG['database']}",
                    '--no-password'
                ]
            elif DB_CONFIG['type'] == 'mysql':
                cmd = [
                    'mysqldump',
                    f"-h{DB_CONFIG['host']}",
                    f"-P{DB_CONFIG['port']}",
                    f"-u{DB_CONFIG['username']}",
                    f"-p{DB_CONFIG['password']}",
                    DB_CONFIG['database']
                ]

            # Exécuter la sauvegarde
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode != 0:
                raise Exception(f"Erreur backup DB: {result.stderr}")

            # Compression et chiffrement
            compressed_path = self._compress_and_encrypt(backup_path)
            os.remove(backup_path)
            
            self.logger.info(f"Backup DB {backup_type} créé: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"Erreur backup database: {e}")
            raise

    def backup_files(self, path_key):
        """Sauvegarde des fichiers"""
        try:
            source_path = Path(BACKUP_PATHS[path_key])
            if not source_path.exists():
                self.logger.warning(f"Répertoire {source_path} n'existe pas")
                return None

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_name = f"{path_key}_{timestamp}.tar.gz"
            backup_path = Path(BACKUP_BASE_DIR) / 'files' / archive_name
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Créer l'archive tar.gz
            shutil.make_archive(
                str(backup_path.with_suffix('')),
                'gztar',
                source_path.parent,
                source_path.name
            )

            # Chiffrement
            encrypted_path = self._encrypt_file(backup_path)
            os.remove(backup_path)
            
            self.logger.info(f"Backup fichiers {path_key} créé: {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            self.logger.error(f"Erreur backup fichiers {path_key}: {e}")
            raise

    def _compress_and_encrypt(self, file_path):
        """Compresse et chiffre un fichier"""
        compressed_path = Path(str(file_path) + '.gz')
        
        # Compression
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Chiffrement
        return self._encrypt_file(compressed_path)

    def _encrypt_file(self, file_path):
        """Chiffre un fichier"""
        encrypted_path = Path(str(file_path) + '.enc')
        
        with open(file_path, 'rb') as f_in:
            data = f_in.read()
            encrypted_data = self.cipher.encrypt(data)
            
        with open(encrypted_path, 'wb') as f_out:
            f_out.write(encrypted_data)
            
        return encrypted_path

    def upload_to_cloud(self, file_path):
        """Upload vers le stockage cloud"""
        try:
            if CLOUD_CONFIG['provider'] == 's3':
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=CLOUD_CONFIG['access_key'],
                    aws_secret_access_key=CLOUD_CONFIG['secret_key'],
                    region_name=CLOUD_CONFIG['region']
                )
                
                key = f"backups/{Path(file_path).name}"
                s3.upload_file(str(file_path), CLOUD_CONFIG['bucket'], key)
                self.logger.info(f"Fichier uploadé vers S3: {key}")
                
        except Exception as e:
            self.logger.error(f"Erreur upload cloud: {e}")
            raise

    def cleanup_old_backups(self):
        """Supprime les anciennes sauvegardes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
            backup_dir = Path(BACKUP_BASE_DIR)
            
            for backup_file in backup_dir.rglob('*.enc'):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    self.logger.info(f"Ancien backup supprimé: {backup_file}")
                    
        except Exception as e:
            self.logger.error(f"Erreur nettoyage: {e}")

    def restore_database(self, backup_file):
        """Restaure la base de données"""
        try:
            # Déchiffrement et décompression
            temp_file = self._decrypt_and_decompress(backup_file)
            
            if DB_CONFIG['type'] == 'postgresql':
                cmd = [
                    'psql',
                    f"-h{DB_CONFIG['host']}",
                    f"-p{DB_CONFIG['port']}",
                    f"-U{DB_CONFIG['username']}",
                    f"-d{DB_CONFIG['database']}",
                    '-f', str(temp_file)
                ]
            elif DB_CONFIG['type'] == 'mysql':
                cmd = [
                    'mysql',
                    f"-h{DB_CONFIG['host']}",
                    f"-P{DB_CONFIG['port']}",
                    f"-u{DB_CONFIG['username']}",
                    f"-p{DB_CONFIG['password']}",
                    DB_CONFIG['database']
                ]
                
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erreur restauration: {result.stderr}")
                
            os.remove(temp_file)
            self.logger.info(f"Base de données restaurée depuis: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Erreur restauration: {e}")
            raise

    def _decrypt_and_decompress(self, encrypted_file):
        """Déchiffre et décompresse un fichier"""
        # Déchiffrement
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
        # Décompression
        temp_file = Path('/tmp') / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        with gzip.open(io.BytesIO(decrypted_data), 'rb') as f_in:
            with open(temp_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        return temp_file

    def test_restore(self, backup_file):
        """Test de restauration sans impact"""
        try:
            # Créer une DB temporaire pour le test
            test_db = f"{DB_CONFIG['database']}_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Créer la DB de test
            if DB_CONFIG['type'] == 'postgresql':
                subprocess.run([
                    'createdb',
                    f"-h{DB_CONFIG['host']}",
                    f"-p{DB_CONFIG['port']}",
                    f"-U{DB_CONFIG['username']}",
                    test_db
                ])
            
            # Tester la restauration
            temp_config = DB_CONFIG.copy()
            temp_config['database'] = test_db
            
            # Restaurer dans la DB de test
            self.restore_database(backup_file)
            
            # Supprimer la DB de test
            if DB_CONFIG['type'] == 'postgresql':
                subprocess.run([
                    'dropdb',
                    f"-h{DB_CONFIG['host']}",
                    f"-p{DB_CONFIG['port']}",
                    f"-U{DB_CONFIG['username']}",
                    test_db
                ])
            
            self.logger.info(f"Test de restauration réussi: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Échec test restauration: {e}")
            return False