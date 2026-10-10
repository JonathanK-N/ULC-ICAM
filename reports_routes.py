"""Reports controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('reports', __name__)

    @blueprint.route('/teacher/generate_report_async/<int:assignment_id>', methods=['POST'])
    def queue_assignment_report(assignment_id):
        user = namespace['session'].get('user')
        from report_service import assignment_report
        try:
            assignment_report(namespace['collect_storage_snapshot'](), assignment_id, user)
        except PermissionError:
            return namespace['jsonify'](error='Accès interdit'), 403
        if namespace['relational_repository'] is None:
            return namespace['jsonify'](error='Les rapports asynchrones nécessitent PostgreSQL'), 503
        try:
            from celery_tasks import configure_celery, generate_assignment_report
            configure_celery()
            task = generate_assignment_report.apply_async(args=[assignment_id, user], retry=False)
        except Exception:
            return namespace['jsonify'](error='Le worker est indisponible. Utilisez le rapport direct.'), 503
        if namespace['request'].is_json:
            return namespace['jsonify'](success=True, task_id=task.id), 202
        namespace['flash']('Rapport en préparation. Le lien apparaîtra dans vos notifications.')
        return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))

    @blueprint.route('/reports/generated/<identifier>')
    def generated_report(identifier):
        user = namespace['session'].get('user')
        record = next((item for item in namespace['generated_reports']
                       if item['id'] == identifier and item['username'] == user), None)
        if record is None:
            return namespace['jsonify'](error='Rapport introuvable'), 404
        from report_service import assignment_report
        try:
            assignment_report(namespace['collect_storage_snapshot'](), record['assignment_id'], user)
        except PermissionError:
            return namespace['jsonify'](error='Accès interdit'), 403
        return namespace['send_from_directory'](
            namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'reports'),
            record['filename'], as_attachment=True)

    @blueprint.route('/teacher/generate_report/<int:assignment_id>')
    def generate_assignment_report(assignment_id):
        """Génère un rapport PDF pour un devoir"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a.get('teacher') == namespace['session']['user']), None)
        if not assignment:
            namespace['flash']('Devoir non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assignments'))
        pdf_buffer = namespace['generate_assignment_report_pdf'](assignment_id)
        if not pdf_buffer:
            namespace['flash']('Erreur lors de la génération du rapport')
            return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))
        response = namespace['make_response'](pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'''attachment; filename="rapport_{assignment['title']}.pdf"'''
        return response

    @blueprint.route('/teacher/export_course_data/<int:course_id>')
    def export_course_data(course_id):
        """Exporte les données d'un cours en CSV"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        if not course:
            namespace['flash']('Cours non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        csv_data = namespace['generate_course_report_csv'](course_id)
        response = namespace['make_response'](csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'''attachment; filename="donnees_{course['name']}.csv"'''
        return response

    @blueprint.route('/admin/system_report')
    def system_report():
        """Génère un rapport système complet"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        stats = {'total_users': len(namespace['users']), 'students': sum((1 for u in namespace['users'].values() if u.get('role') == 'student')), 'teachers': sum((1 for u in namespace['users'].values() if u.get('role') == 'teacher')), 'courses': len(namespace['admin_courses']), 'assignments': len(namespace['assignments']), 'submissions': len(namespace['submissions']), 'corrected': len(namespace['correction_results'])}
        return namespace['render_template']('system_report.html', stats=stats)

    @blueprint.route('/admin/export_all_data')
    def export_all_data():
        """Exporte toutes les données système"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        data = {'users': {name: {k: v for k, v in user.items() if k not in ('password', 'temp_password')} for name, user in namespace['users'].items()}, 'admin_courses': namespace['admin_courses'], 'course_assignments': namespace['course_assignments'], 'course_enrollments': namespace['course_enrollments'], 'assignments': namespace['assignments'], 'submissions': namespace['submissions'], 'correction_results': namespace['correction_results'], 'plagiarism_results': namespace['plagiarism_results']}
        response = namespace['make_response'](namespace['json'].dumps(data, ensure_ascii=False, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = 'attachment; filename="ulc_export_complet.json"'
        return response

    @blueprint.route('/admin/generate_full_report')
    def generate_full_report():
        """Génère un rapport PDF complet"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if not namespace['REPORTLAB_AVAILABLE']:
            namespace['flash']('ReportLab non disponible - génération PDF impossible')
            return namespace['redirect'](namespace['url_for']('system_report'))
        try:
            buffer = namespace['io'].BytesIO()
            doc = namespace['SimpleDocTemplate'](buffer, pagesize=namespace['letter'])
            styles = namespace['getSampleStyleSheet']()
            story = []
            title = namespace['Paragraph']('Rapport Système - Université Loyola du Congo', styles['Title'])
            story.append(title)
            story.append(namespace['Spacer'](1, 12))
            stats_data = [['Utilisateurs totaux:', str(len(namespace['users']))], ['Étudiants:', str(sum((1 for u in namespace['users'].values() if u.get('role') == 'student')))], ['Professeurs:', str(sum((1 for u in namespace['users'].values() if u.get('role') == 'teacher')))], ['Cours:', str(len(namespace['admin_courses']))], ['Devoirs:', str(len(namespace['assignments']))], ['Soumissions:', str(len(namespace['submissions']))]]
            stats_table = namespace['Table'](stats_data)
            story.append(stats_table)
            doc.build(story)
            buffer.seek(0)
            response = namespace['make_response'](buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename="rapport_systeme_ulc.pdf"'
            return response
        except Exception as e:
            namespace['flash'](f'Erreur génération PDF: {e}')
            return namespace['redirect'](namespace['url_for']('system_report'))

    @blueprint.route('/admin/download_backup')
    def download_backup():
        """Télécharge une sauvegarde complète"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_users = {}
        for uname, udata in namespace['users'].items():
            safe_user = {k: v for k, v in udata.items() if k not in ('password', 'temp_password')}
            safe_users[uname] = safe_user
        backup_data = {'timestamp': timestamp, 'version': '1.0', 'university': 'Université Loyola du Congo', 'note': 'Les mots de passe sont exclus de la sauvegarde pour des raisons de sécurité.', 'data': {'users': safe_users, 'admin_courses': namespace['admin_courses'], 'course_assignments': namespace['course_assignments'], 'course_enrollments': namespace['course_enrollments'], 'assignments': namespace['assignments'], 'submissions': namespace['submissions']}}
        response = namespace['make_response'](namespace['json'].dumps(backup_data, ensure_ascii=False, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="sauvegarde_ulc_{timestamp}.json"'
        return response
    return blueprint
