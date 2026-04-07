import json, os
d = json.load(open('ulc_icam_data.json', encoding='utf-8'))
print('Utilisateurs   :', len(d['users']))
print('  Profs        :', sum(1 for u in d['users'].values() if u.get('role')=='teacher'))
print('  Etudiants    :', sum(1 for u in d['users'].values() if u.get('role')=='student'))
print('  Admin        :', sum(1 for u in d['users'].values() if u.get('role')=='admin'))
print('Cours          :', len(d['admin_courses']))
print('Devoirs        :', len(d['assignments']))
print('Soumissions    :', len(d['submissions']))
inscriptions = sum(len(v) for v in d['course_enrollments'].values())
print('Inscriptions   :', inscriptions)
print()
total = 0
for root, dirs, files in os.walk('uploads'):
    for f in files:
        total += 1
        size = os.path.getsize(os.path.join(root, f))
        ext  = f.rsplit('.',1)[-1].upper()
        print(f'  [{ext:5s}] {f} ({size//1024} KB)')
print('Total fichiers :', total)
