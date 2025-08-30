# ===============================================================================
# Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 19:00
# Description: Module notifications email pour ULC-ICAM Turnin System
# Fonctionnalités: Emails automatiques, templates HTML, envoi asynchrone
# Nouvelles: Notifications rapports, compression, téléchargements
# ===============================================================================

from flask_mail import Mail, Message
from flask import current_app
import threading
from datetime import datetime
import json

# Instance Flask-Mail
mail = Mail()

def init_mail(app):
    """Initialise Flask-Mail avec l'application"""
    mail.init_app(app)

def send_async_email(app, msg):
    """Envoie un email de manière asynchrone"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Email envoyé: {msg.subject}")
        except Exception as e:
            print(f"Erreur envoi email: {e}")

def send_email(subject, recipients, html_body, text_body=None):
    """Envoie un email avec gestion asynchrone"""
    if not current_app.config.get('NOTIFICATIONS_ENABLED', False):
        print("Notifications désactivées")
        return
    
    if not recipients:
        print("Aucun destinataire pour l'email")
        return
    
    try:
        msg = Message(
            subject=f"[ULC-ICAM] {subject}",
            recipients=recipients,
            html=html_body,
            body=text_body or html_body
        )
        
        # Envoi asynchrone
        thread = threading.Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        )
        thread.start()
        
    except Exception as e:
        print(f"Erreur création email: {e}")

def get_enrolled_students_emails(course_id, users, course_enrollments):
    """Récupère les emails des étudiants inscrits à un cours"""
    emails = []
    enrolled_students = course_enrollments.get(course_id, [])
    
    for student_username in enrolled_students:
        if student_username in users:
            student = users[student_username]
            if student.get('email'):
                emails.append(student['email'])
    
    return emails

def notify_new_assignment(assignment, course, users, course_enrollments):
    """Notifie les étudiants d'un nouveau devoir"""
    student_emails = get_enrolled_students_emails(course['id'], users, course_enrollments)
    
    if not student_emails:
        return
    
    subject = f"Nouveau devoir: {assignment['title']}"
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1e3a8a; color: white; padding: 20px; text-align: center;">
            <h1>ULC-ICAM Turnin</h1>
            <h2>Nouveau devoir disponible</h2>
        </div>
        
        <div style="padding: 20px; background: #f8fafc;">
            <h3 style="color: #1e3a8a;">{assignment['title']}</h3>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <p><strong>Cours:</strong> {course['name']}</p>
                <p><strong>Description:</strong> {assignment.get('description', 'Aucune description')}</p>
                <p><strong>Date limite:</strong> <span style="color: #dc2626;">{assignment.get('due_date', 'Non définie')}</span></p>
                <p><strong>Note maximale:</strong> {assignment.get('max_score', 100)} points</p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <p>Connectez-vous à la plateforme pour soumettre votre travail.</p>
            </div>
        </div>
        
        <div style="background: #374151; color: white; padding: 15px; text-align: center; font-size: 12px;">
            <p>© 2024 ULC-ICAM Turnin System - Développé par Jonathan Kakesa</p>
            <p>Université Libre du Congo - Institut Catholique d'Arts et Métiers</p>
        </div>
    </div>
    """
    
    send_email(subject, student_emails, html_body)

def notify_grades_published(assignment, course, users, course_enrollments, correction_results):
    """Notifie les étudiants que les notes sont publiées"""
    student_emails = get_enrolled_students_emails(course['id'], users, course_enrollments)
    
    if not student_emails:
        return
    
    subject = f"Notes publiées: {assignment['title']}"
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #059669; color: white; padding: 20px; text-align: center;">
            <h1>ULC-ICAM Turnin</h1>
            <h2>Notes publiées</h2>
        </div>
        
        <div style="padding: 20px; background: #f8fafc;">
            <h3 style="color: #059669;">{assignment['title']}</h3>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <p><strong>Cours:</strong> {course['name']}</p>
                <p><strong>Date de publication:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <p>Connectez-vous pour consulter vos résultats détaillés.</p>
            </div>
        </div>
        
        <div style="background: #374151; color: white; padding: 15px; text-align: center; font-size: 12px;">
            <p>© 2024 ULC-ICAM Turnin System - Développé par Jonathan Kakesa</p>
        </div>
    </div>
    """
    
    send_email(subject, student_emails, html_body)