"""Durable email delivery without importing the Flask application."""
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
from email.utils import parseaddr
import os
import smtplib
import ssl
import uuid


def send_mail(job):
    recipients = job['recipients']
    if not recipients or len(recipients) > 500 or any(parseaddr(value)[1] != value or '@' not in value for value in recipients):
        raise ValueError('Invalid recipients')
    message = EmailMessage()
    message['Subject'] = job['subject']
    message['From'] = os.environ['MAIL_DEFAULT_SENDER']
    # Recipients never appear in each other's headers.
    message['To'] = 'undisclosed-recipients:;'
    message.set_content('Une information est disponible dans votre espace Cognito Web.')
    message.add_alternative(job['html'], subtype='html')
    host = os.environ['MAIL_SERVER']
    port = int(os.environ.get('MAIL_PORT', '587'))
    context = ssl.create_default_context()
    if port == 465:
        smtp = smtplib.SMTP_SSL(host, port, timeout=15, context=context)
    else:
        smtp = smtplib.SMTP(host, port, timeout=15)
    with smtp:
        if port != 465:
            smtp.starttls(context=context)
        smtp.login(os.environ['MAIL_USERNAME'], os.environ['MAIL_PASSWORD'])
        smtp.send_message(message, to_addrs=recipients)


def deliver_emails(repository, sender=send_mail):
    if os.environ.get('NOTIFICATIONS_ENABLED', '').lower() not in ('true', '1', 'yes'):
        return {'status': 'disabled'}
    with repository.transaction() as connection:
        data = repository.load(connection)
        candidates = []
        for job in data.get('email_jobs', []):
            if job.get('status') in ('sent', 'failed') or job.get('attempts', 0) >= 3:
                continue
            if job.get('status') == 'sending':
                try:
                    if datetime.now(timezone.utc) - datetime.fromisoformat(job['started']) < timedelta(minutes=10):
                        continue
                except (KeyError, ValueError, TypeError):
                    pass
            candidates.append(job)
        pending = candidates[:1]
        for job in pending:
            job.update(status='sending', token=uuid.uuid4().hex,
                       started=datetime.now(timezone.utc).isoformat())
        repository.save(connection, data)
    for job in pending:
        try:
            sender(job)
            outcome = 'sent'
        except Exception:
            outcome = 'retry'
        with repository.transaction() as connection:
            current = repository.load(connection)
            target = next((item for item in current.get('email_jobs', []) if item['id'] == job['id']), None)
            if target and target.get('token') == job['token']:
                target['attempts'] = target.get('attempts', 0) + 1
                target['status'] = 'failed' if outcome == 'retry' and target['attempts'] >= 3 else outcome
                target.pop('token', None)
                repository.save(connection, current)
    return {'status': 'completed', 'processed': len(pending)}
