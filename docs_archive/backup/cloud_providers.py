#!/usr/bin/env python3
"""
ULC-ICAM TURNIN SYSTEM - ADAPTATEURS CLOUD
Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
Tous droits réservés - Logiciel Propriétaire

Adaptateurs pour différents fournisseurs de stockage cloud

UTILISATION RESTREINTE - Voir LICENSE pour les conditions
"""
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
from backup_config import CLOUD_CONFIG

class CloudStorageAdapter:
    def __init__(self, provider=None):
        self.provider = provider or CLOUD_CONFIG['provider']
        self.client = self._get_client()
    
    def _get_client(self):
        if self.provider == 's3':
            return boto3.client(
                's3',
                aws_access_key_id=CLOUD_CONFIG['access_key'],
                aws_secret_access_key=CLOUD_CONFIG['secret_key'],
                region_name=CLOUD_CONFIG['region']
            )
        elif self.provider == 'azure':
            return BlobServiceClient(
                account_url=f"https://{CLOUD_CONFIG['account_name']}.blob.core.windows.net",
                credential=CLOUD_CONFIG['account_key']
            )
        elif self.provider == 'gcp':
            return gcs.Client.from_service_account_json(CLOUD_CONFIG['service_account_path'])
        else:
            raise ValueError(f"Fournisseur non supporté: {self.provider}")
    
    def upload_file(self, local_path, remote_key):
        """Upload un fichier vers le cloud"""
        if self.provider == 's3':
            self.client.upload_file(local_path, CLOUD_CONFIG['bucket'], remote_key)
        elif self.provider == 'azure':
            blob_client = self.client.get_blob_client(
                container=CLOUD_CONFIG['container'], 
                blob=remote_key
            )
            with open(local_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
        elif self.provider == 'gcp':
            bucket = self.client.bucket(CLOUD_CONFIG['bucket'])
            blob = bucket.blob(remote_key)
            blob.upload_from_filename(local_path)
    
    def download_file(self, remote_key, local_path):
        """Télécharge un fichier depuis le cloud"""
        if self.provider == 's3':
            self.client.download_file(CLOUD_CONFIG['bucket'], remote_key, local_path)
        elif self.provider == 'azure':
            blob_client = self.client.get_blob_client(
                container=CLOUD_CONFIG['container'], 
                blob=remote_key
            )
            with open(local_path, 'wb') as data:
                data.write(blob_client.download_blob().readall())
        elif self.provider == 'gcp':
            bucket = self.client.bucket(CLOUD_CONFIG['bucket'])
            blob = bucket.blob(remote_key)
            blob.download_to_filename(local_path)
    
    def list_files(self, prefix=''):
        """Liste les fichiers dans le cloud"""
        if self.provider == 's3':
            response = self.client.list_objects_v2(
                Bucket=CLOUD_CONFIG['bucket'], 
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        elif self.provider == 'azure':
            container_client = self.client.get_container_client(CLOUD_CONFIG['container'])
            return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]
        elif self.provider == 'gcp':
            bucket = self.client.bucket(CLOUD_CONFIG['bucket'])
            return [blob.name for blob in bucket.list_blobs(prefix=prefix)]
    
    def delete_file(self, remote_key):
        """Supprime un fichier du cloud"""
        if self.provider == 's3':
            self.client.delete_object(Bucket=CLOUD_CONFIG['bucket'], Key=remote_key)
        elif self.provider == 'azure':
            blob_client = self.client.get_blob_client(
                container=CLOUD_CONFIG['container'], 
                blob=remote_key
            )
            blob_client.delete_blob()
        elif self.provider == 'gcp':
            bucket = self.client.bucket(CLOUD_CONFIG['bucket'])
            blob = bucket.blob(remote_key)
            blob.delete()