#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de seeding — ULC-ICAM Turnin System
Génère :
  - 5 professeurs, 20 étudiants, 1 admin
  - 8 cours avec assignations et inscriptions
  - 10 devoirs
  - 30+ soumissions avec notes et résultats plagiat
  - Fichiers de cours : PDF, Word (.docx), PowerPoint (.pptx)
Auteur : Jonathan Kakesa
"""

import os, json, hashlib, random, shutil
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# ── Dossiers ────────────────────────────────────────────────────────────────
UPLOAD   = 'uploads'
CHAPTERS = os.path.join(UPLOAD, 'chapters')
ASSIGN   = os.path.join(UPLOAD, 'assignments')
SUBMITS  = os.path.join(UPLOAD, 'submissions')
CODE_DIR = os.path.join(UPLOAD, 'code_submissions')
CORRECTS = os.path.join(UPLOAD, 'corrections')
SYLLABUS = os.path.join(UPLOAD, 'syllabus')

for d in [UPLOAD, CHAPTERS, ASSIGN, SUBMITS, CODE_DIR, CORRECTS, SYLLABUS]:
    os.makedirs(d, exist_ok=True)

random.seed(42)
NOW = datetime.now()


# ════════════════════════════════════════════════════════════════════════════
# 1.  GÉNÉRATION DES FICHIERS DE COURS
# ════════════════════════════════════════════════════════════════════════════

# ── PDF via ReportLab ────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

def _header_style():
    s = getSampleStyleSheet()
    return {
        'title':  ParagraphStyle('title',  parent=s['Title'],   fontSize=20, textColor=colors.HexColor('#1e3a8a'), spaceAfter=6),
        'h1':     ParagraphStyle('h1',     parent=s['Heading1'],fontSize=14, textColor=colors.HexColor('#1e3a8a'), spaceBefore=14, spaceAfter=4),
        'h2':     ParagraphStyle('h2',     parent=s['Heading2'],fontSize=12, textColor=colors.HexColor('#374151'), spaceBefore=10, spaceAfter=3),
        'body':   ParagraphStyle('body',   parent=s['Normal'],  fontSize=11, leading=16, alignment=TA_JUSTIFY),
        'bullet': ParagraphStyle('bullet', parent=s['Normal'],  fontSize=11, leftIndent=20, spaceBefore=2),
        'center': ParagraphStyle('center', parent=s['Normal'],  fontSize=11, alignment=TA_CENTER),
        'small':  ParagraphStyle('small',  parent=s['Normal'],  fontSize=9,  textColor=colors.gray),
    }

def _pdf_banner(story, st, titre, sous_titre, prof, annee='2024-2025'):
    data = [[Paragraph(f'<b>ULC-ICAM</b> — Université Loyola du Congo', st['center']),
             Paragraph(f'Année académique {annee}', st['center'])]]
    t = Table(data, colWidths=[10*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0),(-1,-1), colors.white),
        ('FONTSIZE',  (0,0),(-1,-1), 10),
        ('PADDING',   (0,0),(-1,-1), 8),
    ]))
    story += [t, Spacer(1, 0.4*cm),
              Paragraph(titre, st['title']),
              Paragraph(sous_titre, st['h2']),
              Paragraph(f'Enseignant : {prof}', st['small']),
              HRFlowable(width='100%', thickness=1, color=colors.HexColor('#1e3a8a')),
              Spacer(1, 0.3*cm)]

def make_pdf_cours(path, titre, prof, contenu_sections):
    """contenu_sections : list of (titre_section, [paragraphes])"""
    doc   = SimpleDocTemplate(path, pagesize=A4,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2*cm,  bottomMargin=2*cm)
    st    = _header_style()
    story = []
    _pdf_banner(story, st, titre, 'Notes de cours', prof)
    for sec_titre, paras in contenu_sections:
        story.append(Paragraph(sec_titre, st['h1']))
        for p in paras:
            if p.startswith('•'):
                story.append(Paragraph(p, st['bullet']))
            else:
                story.append(Paragraph(p, st['body']))
            story.append(Spacer(1, 0.15*cm))
        story.append(Spacer(1, 0.2*cm))
    doc.build(story)
    print(f'  [PDF]  {path}')

def make_pdf_devoir(path, titre, prof, enonce, bareme):
    doc   = SimpleDocTemplate(path, pagesize=A4,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2*cm,  bottomMargin=2*cm)
    st    = _header_style()
    story = []
    _pdf_banner(story, st, titre, 'Énoncé du devoir', prof)
    story.append(Paragraph('Énoncé', st['h1']))
    for line in enonce:
        story.append(Paragraph(line, st['body']))
        story.append(Spacer(1, 0.1*cm))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Barème', st['h1']))
    table_data = [['Partie', 'Points']] + bareme
    t = Table(table_data, colWidths=[13*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),  colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0),(-1,0),  colors.white),
        ('FONTNAME',  (0,0),(-1,0),  'Helvetica-Bold'),
        ('BACKGROUND',(0,1),(-1,-1), colors.HexColor('#f0f4ff')),
        ('GRID',      (0,0),(-1,-1), 0.5, colors.gray),
        ('FONTSIZE',  (0,0),(-1,-1), 10),
        ('PADDING',   (0,0),(-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#e8eeff')]),
    ]))
    story.append(t)
    doc.build(story)
    print(f'  [PDF]  {path}')

# ── Word via python-docx ─────────────────────────────────────────────────────
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def make_word_cours(path, titre, prof, sections):
    doc = Document()
    # Styles
    doc.core_properties.author = prof
    doc.core_properties.title  = titre
    # Bandeau
    header_p = doc.add_paragraph()
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header_p.add_run(f'ULC-ICAM  —  {titre}')
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0x1e, 0x3a, 0x8a)
    doc.add_paragraph(f'Enseignant : {prof}  |  Année 2024-2025').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    for sec_titre, paras in sections:
        h = doc.add_heading(sec_titre, level=1)
        h.runs[0].font.color.rgb = RGBColor(0x1e, 0x3a, 0x8a)
        for p in paras:
            if p.startswith('•'):
                doc.add_paragraph(p[1:].strip(), style='List Bullet')
            else:
                para = doc.add_paragraph(p)
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.save(path)
    print(f'  [DOCX] {path}')

def make_word_tp(path, titre, prof, questions):
    doc = Document()
    doc.core_properties.author = prof
    header_p = doc.add_paragraph()
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header_p.add_run(f'TRAVAUX PRATIQUES — {titre}')
    run.bold = True; run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x1e, 0x3a, 0x8a)
    doc.add_paragraph(f'Enseignant : {prof}').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_heading('Questions', level=1)
    for i, q in enumerate(questions, 1):
        p = doc.add_paragraph()
        run = p.add_run(f'Question {i} : ')
        run.bold = True
        p.add_run(q)
        doc.add_paragraph()
    doc.save(path)
    print(f'  [DOCX] {path}')

# ── PowerPoint via python-pptx ───────────────────────────────────────────────
from pptx import Presentation
from pptx.util import Inches, Pt as PtPPT, Emu
from pptx.dml.color import RGBColor as PPTColor
from pptx.enum.text import PP_ALIGN

BLEU  = PPTColor(0x1e, 0x3a, 0x8a)
BLANC = PPTColor(0xff, 0xff, 0xff)
GRIS  = PPTColor(0x37, 0x41, 0x51)

def _add_slide(prs, layout_idx=1):
    return prs.slides.add_slide(prs.slide_layouts[layout_idx])

def _set_text(shape, text, size=20, bold=False, color=None, align=PP_ALIGN.LEFT):
    tf = shape.text_frame
    tf.clear()
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = PtPPT(size)
    run.font.bold  = bold
    if color:
        run.font.color.rgb = color

def make_ppt_cours(path, titre, prof, slides_data):
    """slides_data : list of (titre_slide, [bullet_points])"""
    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    # Slide titre
    slide = _add_slide(prs, 0)
    slide.shapes.title.text = titre
    slide.shapes.title.text_frame.paragraphs[0].runs[0].font.color.rgb = BLEU
    slide.shapes.title.text_frame.paragraphs[0].runs[0].font.bold = True
    slide.placeholders[1].text = f'{prof}\nULC-ICAM — Année 2024-2025'

    for slide_titre, bullets in slides_data:
        slide   = _add_slide(prs, 1)
        title_s = slide.shapes.title
        body_s  = slide.placeholders[1]
        title_s.text = slide_titre
        title_s.text_frame.paragraphs[0].runs[0].font.color.rgb = BLEU
        title_s.text_frame.paragraphs[0].runs[0].font.bold = True
        tf = body_s.text_frame
        tf.clear()
        for i, bullet in enumerate(bullets):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text  = bullet
            p.level = 1 if bullet.startswith('  ') else 0
            if p.runs:
                p.runs[0].font.size  = PtPPT(18)
                p.runs[0].font.color.rgb = GRIS

    prs.save(path)
    print(f'  [PPTX] {path}')

# ── Soumissions étudiantes (code Python + textes) ────────────────────────────
def make_student_code(path, student_name, assignment_title, code_lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# Auteur  : {student_name}\n")
        f.write(f"# Devoir  : {assignment_title}\n")
        f.write(f"# Date    : {NOW.strftime('%Y-%m-%d')}\n\n")
        f.write('\n'.join(code_lines))
    print(f'  [PY]   {path}')

def make_student_text(path, student_name, assignment_title, paragraphes):
    doc = Document()
    doc.core_properties.author = student_name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(assignment_title)
    run.bold = True; run.font.size = Pt(16)
    doc.add_paragraph(f'Étudiant : {student_name}  |  {NOW.strftime("%d/%m/%Y")}').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    for para in paragraphes:
        doc.add_paragraph(para).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.save(path)
    print(f'  [DOCX] {path}')


# ════════════════════════════════════════════════════════════════════════════
# 2.  DONNÉES JSON
# ════════════════════════════════════════════════════════════════════════════

# ── Professeurs ──────────────────────────────────────────────────────────────
PROFS = [
    {
        'username':       'jb.mukendi',
        'password':       generate_password_hash('Prof@2024'),
        'role':           'teacher',
        'must_change_password': False,
        'name':           'Prof. Jean-Baptiste Mukendi',
        'nom':            'Mukendi',
        'postnom':        'Kalamba',
        'prenom':         'Jean-Baptiste',
        'sexe':           'M',
        'date_naissance': '1975-03-12',
        'cip':            'ULC-T-001',
        'email':          'jb.mukendi@ulc-icam.cd',
        'telephone':      '+243 810 001 001',
        'cours_dispenses': 'Algorithmique, Structures de données, Programmation Python',
        'departement':    'Génie Informatique',
        'grade':          'Prof. Ordinaire',
        'bureau':         'Bât. A — Bureau 101',
        'faculte':        'Faculté des Sciences et Technologies (ULC-ICAM)',
    },
    {
        'username':       'mc.ngoma',
        'password':       generate_password_hash('Prof@2024'),
        'role':           'teacher',
        'must_change_password': False,
        'name':           'CT Marie-Claire Ngoma',
        'nom':            'Ngoma',
        'postnom':        'Banza',
        'prenom':         'Marie-Claire',
        'sexe':           'F',
        'date_naissance': '1982-07-25',
        'cip':            'ULC-T-002',
        'email':          'mc.ngoma@ulc-icam.cd',
        'telephone':      '+243 820 001 002',
        'cours_dispenses': 'Bases de données, Réseaux informatiques, Sécurité informatique',
        'departement':    'Génie Informatique',
        'grade':          'CT',
        'bureau':         'Bât. A — Bureau 102',
        'faculte':        'Faculté des Sciences et Technologies (ULC-ICAM)',
    },
    {
        'username':       'f.kabila',
        'password':       generate_password_hash('Prof@2024'),
        'role':           'teacher',
        'must_change_password': False,
        'name':           'Ass. François Kabila',
        'nom':            'Kabila',
        'postnom':        'Mutombo',
        'prenom':         'François',
        'sexe':           'M',
        'date_naissance': '1989-11-05',
        'cip':            'ULC-T-003',
        'email':          'f.kabila@ulc-icam.cd',
        'telephone':      '+243 830 001 003',
        'cours_dispenses': 'Circuits électroniques, Électronique numérique, Microcontrôleurs',
        'departement':    'Génie Électrique',
        'grade':          'Ass.',
        'bureau':         'Bât. B — Bureau 201',
        'faculte':        'Faculté des Sciences et Technologies (ULC-ICAM)',
    },
    {
        'username':       's.mwamba',
        'password':       generate_password_hash('Prof@2024'),
        'role':           'teacher',
        'must_change_password': False,
        'name':           'Prof. Sophie Mwamba',
        'nom':            'Mwamba',
        'postnom':        'Ilunga',
        'prenom':         'Sophie',
        'sexe':           'F',
        'date_naissance': '1978-04-18',
        'cip':            'ULC-T-004',
        'email':          's.mwamba@ulc-icam.cd',
        'telephone':      '+243 840 001 004',
        'cours_dispenses': 'Mathématiques Appliquées, Analyse numérique, Statistiques',
        'departement':    'Mathématiques & Informatique',
        'grade':          'Prof. Associé',
        'bureau':         'Bât. C — Bureau 301',
        'faculte':        'Faculté des Sciences et Technologies (ULC-ICAM)',
    },
    {
        'username':       'p.lumumba',
        'password':       generate_password_hash('Prof@2024'),
        'role':           'teacher',
        'must_change_password': False,
        'name':           'Prof. Pierre Lumumba',
        'nom':            'Lumumba',
        'postnom':        'Nkosi',
        'prenom':         'Pierre',
        'sexe':           'M',
        'date_naissance': '1971-09-30',
        'cip':            'ULC-T-005',
        'email':          'p.lumumba@ulc-icam.cd',
        'telephone':      '+243 850 001 005',
        'cours_dispenses': 'Mécanique des fluides, Thermodynamique, Résistance des matériaux',
        'departement':    'Génie Mécanique',
        'grade':          'Prof. Ordinaire',
        'bureau':         'Bât. D — Bureau 401',
        'faculte':        'Faculté des Sciences et Technologies (ULC-ICAM)',
    },
]

# ── Étudiants ─────────────────────────────────────────────────────────────────
ETUDIANTS_RAW = [
    # (prenom, nom, postnom, sexe, ddn, promotion, dept, cip)
    ('Grâce',    'Kasongo',   'Mbuyi',   'F', '2003-05-14', 'L1', 'Génie Informatique',     'ULC-S-001'),
    ('Élie',     'Tshisekedi','Mwana',   'M', '2002-08-22', 'L1', 'Génie Informatique',     'ULC-S-002'),
    ('Nadège',   'Lukusa',    'Kabena',  'F', '2003-01-09', 'L1', 'Génie Électrique',       'ULC-S-003'),
    ('David',    'Mulamba',   'Tshibola','M', '2002-11-17', 'L1', 'Génie Mécanique',        'ULC-S-004'),
    ('Ruth',     'Nkulu',     'Wa Biaya','F', '2001-06-03', 'L2', 'Génie Informatique',     'ULC-S-005'),
    ('Joël',     'Kabongo',   'Kanda',   'M', '2001-03-28', 'L2', 'Génie Informatique',     'ULC-S-006'),
    ('Esther',   'Mwangi',    'Kalala',  'F', '2001-09-11', 'L2', 'Génie Électrique',       'ULC-S-007'),
    ('Patrick',  'Kapumba',   'Tshibal', 'M', '2000-12-25', 'L2', 'Génie Mécanique',        'ULC-S-008'),
    ('Déborah',  'Mutombo',   'Ngoy',    'F', '2000-04-07', 'L3', 'Génie Informatique',     'ULC-S-009'),
    ('Samuel',   'Luboya',    'Mubika',  'M', '2000-07-19', 'L3', 'Génie Informatique',     'ULC-S-010'),
    ('Christelle','Ilunga',   'Nkulu',   'F', '1999-02-14', 'L3', 'Génie Électrique',       'ULC-S-011'),
    ('Emmanuel', 'Mbuyi',     'Tshibal', 'M', '1999-10-31', 'L3', 'Génie Mécanique',        'ULC-S-012'),
    ('Lydie',    'Kazadi',    'Wa Banza','F', '1998-08-05', 'M1', 'Génie Informatique',     'ULC-S-013'),
    ('Thierry',  'Nzinga',    'Mwamba',  'M', '1998-03-22', 'M1', 'Mathématiques & Informatique','ULC-S-014'),
    ('Prisca',   'Kalombo',   'Luba',    'F', '2002-06-30', 'L1', 'Physique & Chimie',      'ULC-S-015'),
    ('Hervé',    'Mukendi',   'Kalala',  'M', '2001-05-17', 'L2', 'Mathématiques & Informatique','ULC-S-016'),
    ('Ornella',  'Tshimanga', 'Ngalula', 'F', '2003-09-08', 'L1', 'Génie Mécanique',        'ULC-S-017'),
    ('Kevin',    'Kabamba',   'Nkuba',   'M', '2000-11-02', 'L3', 'Physique & Chimie',      'ULC-S-018'),
    ('Micheline','Ngandu',    'Mujinga', 'F', '2001-07-24', 'L2', 'Génie Électrique',       'ULC-S-019'),
    ('Willy',    'Tshilombo', 'Nkubu',  'M', '2002-04-15', 'L1', 'Génie Informatique',     'ULC-S-020'),
]

def make_student(i, row):
    prenom, nom, postnom, sexe, ddn, promo, dept, cip = row
    username = f"{prenom.lower().replace('é','e').replace('è','e').replace('â','a').replace('ê','e')}.{nom.lower()}"
    return {
        'username':       username,
        'password':       generate_password_hash('Etudiant@2024'),
        'role':           'student',
        'must_change_password': False,
        'name':           f"{prenom} {nom}",
        'nom':            nom,
        'postnom':        postnom,
        'prenom':         prenom,
        'sexe':           sexe,
        'date_naissance': ddn,
        'promotion':      promo,
        'cip':            cip,
        'email':          f"{username}@etud.ulc-icam.cd",
        'telephone':      f"+243 8{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
        'faculte':        'Faculté des Sciences et Technologies (ULC-ICAM)',
        'departement':    dept,
        'adresse':        f"Avenue de la Paix, N°{random.randint(10,200)}, Kinshasa",
    }

ETUDIANTS = [make_student(i, r) for i, r in enumerate(ETUDIANTS_RAW)]

# ── Cours ────────────────────────────────────────────────────────────────────
COURSES = [
    {'id':1,'name':'Algorithmique et Structures de Données','code':'INFO-L2-ASD',
     'credits':4,'promotions':['L2'],'departement':'Génie Informatique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Étude des algorithmes fondamentaux et des structures de données classiques (listes, piles, files, arbres, graphes).'},
    {'id':2,'name':'Programmation Python','code':'INFO-L1-PY',
     'credits':3,'promotions':['L1'],'departement':'Génie Informatique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Introduction à la programmation impérative et orientée objet avec Python 3.'},
    {'id':3,'name':'Bases de Données','code':'INFO-L2-BDD',
     'credits':4,'promotions':['L2'],'departement':'Génie Informatique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Modélisation relationnelle, SQL avancé, transactions et normalisation.'},
    {'id':4,'name':'Réseaux Informatiques','code':'INFO-L3-NET',
     'credits':4,'promotions':['L3'],'departement':'Génie Informatique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Architecture des réseaux, protocoles TCP/IP, routage et sécurité réseau.'},
    {'id':5,'name':'Circuits Électroniques','code':'ELEC-L2-CIR',
     'credits':4,'promotions':['L2'],'departement':'Génie Électrique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Analyse des circuits AC/DC, amplificateurs opérationnels et filtres.'},
    {'id':6,'name':'Mathématiques Appliquées','code':'MATH-L1-APP',
     'credits':4,'promotions':['L1','L2'],'departement':'Mathématiques & Informatique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Algèbre linéaire, calcul différentiel et intégral appliqués à l\'ingénierie.'},
    {'id':7,'name':'Mécanique des Fluides','code':'MECA-L3-FLU',
     'credits':3,'promotions':['L3'],'departement':'Génie Mécanique',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Statique et dynamique des fluides, équations de Bernoulli, turbulence.'},
    {'id':8,'name':'Physique des Semiconducteurs','code':'PHYS-L2-SEMI',
     'credits':3,'promotions':['L2'],'departement':'Physique & Chimie',
     'faculte':'Faculté des Sciences et Technologies (ULC-ICAM)',
     'description':'Propriétés électroniques des semiconducteurs, jonctions PN, transistors bipolaires.'},
]

# ── Assignations prof→cours ───────────────────────────────────────────────────
# {course_id: [prof_username]}
COURSE_ASSIGNMENTS = {
    '1': ['jb.mukendi'],
    '2': ['jb.mukendi'],
    '3': ['mc.ngoma'],
    '4': ['mc.ngoma'],
    '5': ['f.kabila'],
    '6': ['s.mwamba'],
    '7': ['p.lumumba'],
    '8': ['s.mwamba'],
}

# ── Inscriptions étudiant→cours ───────────────────────────────────────────────
def get_stud(promo, dept=None):
    return [e['username'] for e in ETUDIANTS
            if e['promotion'] == promo and (dept is None or e['departement'] == dept)]

def get_studs_multi(promos, dept=None):
    result = []
    for p in promos:
        result += get_stud(p, dept)
    return list(set(result))

COURSE_ENROLLMENTS = {
    '1': get_stud('L2', 'Génie Informatique'),                    # ASD
    '2': get_stud('L1', 'Génie Informatique') + get_stud('L1', 'Génie Mécanique') + ['willy.tshilombo'],
    '3': get_stud('L2', 'Génie Informatique') + ['herve.mukendi'],
    '4': get_stud('L3', 'Génie Informatique'),                    # Réseaux
    '5': get_stud('L2', 'Génie Électrique'),                      # Circuits
    '6': get_studs_multi(['L1', 'L2']),                           # Maths (tous)
    '7': get_stud('L3', 'Génie Mécanique'),                       # Mécaflu
    '8': get_stud('L2', 'Physique & Chimie') + get_stud('L2', 'Génie Électrique'),
}
# Supprimer les doublons
COURSE_ENROLLMENTS = {k: list(dict.fromkeys(v)) for k, v in COURSE_ENROLLMENTS.items()}

# ── Devoirs ───────────────────────────────────────────────────────────────────
DUE_PAST  = lambda d: (NOW - timedelta(days=d)).strftime('%Y-%m-%dT23:59')
DUE_SOON  = lambda d: (NOW + timedelta(days=d)).strftime('%Y-%m-%dT23:59')

ASSIGNMENTS = [
    {'id':1,'title':'TP1 — Tri par insertion et tri rapide',
     'description':'Implémenter et comparer les algorithmes de tri par insertion et tri rapide en Python. Analyser leur complexité théorique et mesurer les temps d\'exécution expérimentaux.',
     'course_id':1,'course':'Algorithmique et Structures de Données',
     'teacher':'jb.mukendi','teacher_name':'Prof. Jean-Baptiste Mukendi',
     'due_date':DUE_PAST(10),'max_score':20,'results_published':True,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':True,'is_group_work':False,'group_formation':'manual',
     'group_size':2,'is_code_assignment':True,'is_mixed_assignment':False,'test_cases':[],
     'files':['devoir_asd_tri.pdf']},
    {'id':2,'title':'TP2 — Arbres binaires de recherche',
     'description':'Implémenter un arbre binaire de recherche avec insertion, suppression et parcours (infixe, préfixe, suffixe). Calculer la hauteur et l\'équilibre.',
     'course_id':1,'course':'Algorithmique et Structures de Données',
     'teacher':'jb.mukendi','teacher_name':'Prof. Jean-Baptiste Mukendi',
     'due_date':DUE_SOON(7),'max_score':20,'results_published':False,'results_release_date':'',
     'auto_correct':True,'plagiarism_check':True,'is_group_work':False,'group_formation':'manual',
     'group_size':2,'is_code_assignment':True,'is_mixed_assignment':False,'test_cases':[],
     'files':[]},
    {'id':3,'title':'Projet Python — Gestionnaire de contacts',
     'description':'Créer une application Python en ligne de commande permettant de gérer une liste de contacts (ajouter, modifier, supprimer, rechercher). Utiliser la POO et persister les données en JSON.',
     'course_id':2,'course':'Programmation Python',
     'teacher':'jb.mukendi','teacher_name':'Prof. Jean-Baptiste Mukendi',
     'due_date':DUE_PAST(5),'max_score':20,'results_published':True,'results_release_date':'',
     'auto_correct':True,'plagiarism_check':True,'is_group_work':True,'group_formation':'manual',
     'group_size':2,'is_code_assignment':True,'is_mixed_assignment':False,'test_cases':[],
     'files':['devoir_python_contacts.pdf']},
    {'id':4,'title':'Devoir SQL — Requêtes avancées',
     'description':'Écrire les requêtes SQL correspondant aux énoncés fournis. Travailler sur la base de données "Université" fournie en annexe.',
     'course_id':3,'course':'Bases de Données',
     'teacher':'mc.ngoma','teacher_name':'CT Marie-Claire Ngoma',
     'due_date':DUE_PAST(3),'max_score':20,'results_published':True,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':True,'is_group_work':False,'group_formation':'manual',
     'group_size':2,'is_code_assignment':False,'is_mixed_assignment':False,'test_cases':[],
     'files':['devoir_sql_avance.pdf']},
    {'id':5,'title':'TP Réseaux — Configuration OSPF',
     'description':'Configurer un réseau multi-routeurs avec OSPF sur Cisco Packet Tracer. Documenter la configuration et tester la convergence.',
     'course_id':4,'course':'Réseaux Informatiques',
     'teacher':'mc.ngoma','teacher_name':'CT Marie-Claire Ngoma',
     'due_date':DUE_SOON(14),'max_score':20,'results_published':False,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':False,'is_group_work':True,'group_formation':'auto',
     'group_size':3,'is_code_assignment':False,'is_mixed_assignment':False,'test_cases':[],
     'files':[]},
    {'id':6,'title':'Labo Circuits — Amplificateur opérationnel',
     'description':'Monter et analyser un circuit amplificateur inverseur et non-inverseur avec un AO 741. Relever les courbes et comparer avec la théorie.',
     'course_id':5,'course':'Circuits Électroniques',
     'teacher':'f.kabila','teacher_name':'Ass. François Kabila',
     'due_date':DUE_PAST(8),'max_score':20,'results_published':True,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':False,'is_group_work':True,'group_formation':'manual',
     'group_size':2,'is_code_assignment':False,'is_mixed_assignment':True,'test_cases':[],
     'files':['devoir_circuits_ao.pdf']},
    {'id':7,'title':'Interrogation — Algèbre linéaire',
     'description':'Résoudre les systèmes linéaires et calculer les valeurs propres et vecteurs propres des matrices données.',
     'course_id':6,'course':'Mathématiques Appliquées',
     'teacher':'s.mwamba','teacher_name':'Prof. Sophie Mwamba',
     'due_date':DUE_PAST(15),'max_score':20,'results_published':True,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':False,'is_group_work':False,'group_formation':'manual',
     'group_size':2,'is_code_assignment':False,'is_mixed_assignment':False,'test_cases':[],
     'files':['devoir_algebre_lineaire.pdf']},
    {'id':8,'title':'TD — Équation de Bernoulli',
     'description':'Appliquer l\'équation de Bernoulli pour résoudre les problèmes d\'écoulement en conduite. Calculer les pertes de charges.',
     'course_id':7,'course':'Mécanique des Fluides',
     'teacher':'p.lumumba','teacher_name':'Prof. Pierre Lumumba',
     'due_date':DUE_PAST(6),'max_score':20,'results_published':True,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':False,'is_group_work':False,'group_formation':'manual',
     'group_size':2,'is_code_assignment':False,'is_mixed_assignment':False,'test_cases':[],
     'files':['devoir_bernoulli.pdf']},
    {'id':9,'title':'Rapport de TP — Jonctions PN',
     'description':'Rédiger un rapport complet sur les mesures effectuées en laboratoire sur les jonctions PN. Inclure courbes I-V, interprétation et conclusions.',
     'course_id':8,'course':'Physique des Semiconducteurs',
     'teacher':'s.mwamba','teacher_name':'Prof. Sophie Mwamba',
     'due_date':DUE_PAST(2),'max_score':20,'results_published':False,'results_release_date':'',
     'auto_correct':False,'plagiarism_check':True,'is_group_work':False,'group_formation':'manual',
     'group_size':2,'is_code_assignment':False,'is_mixed_assignment':False,'test_cases':[],
     'files':[]},
    {'id':10,'title':'Mini-projet — Application Web Flask',
     'description':'Développer une application web Flask avec authentification, base de données SQLite et interface Bootstrap. Déployer sur un serveur local.',
     'course_id':4,'course':'Réseaux Informatiques',
     'teacher':'mc.ngoma','teacher_name':'CT Marie-Claire Ngoma',
     'due_date':DUE_SOON(21),'max_score':20,'results_published':False,'results_release_date':'',
     'auto_correct':True,'plagiarism_check':True,'is_group_work':True,'group_formation':'manual',
     'group_size':2,'is_code_assignment':True,'is_mixed_assignment':False,'test_cases':[],
     'files':[]},
]

# ── Soumissions + Notes ───────────────────────────────────────────────────────
NOTES = [14, 16, 12, 18, 10, 15, 17, 11, 13, 19, 9, 14, 16, 8, 15, 17, 12, 14, 11, 16]
FEEDBACK_POOL = [
    ['Excellent travail, la logique est claire et bien structurée.',
     'Bonne gestion des cas limites.','La complexité algorithmique est correctement analysée.'],
    ['Bon travail dans l\'ensemble.','Quelques commentaires manquants dans le code.',
     'La complexité pourrait être mieux justifiée théoriquement.'],
    ['Travail satisfaisant.','Certains cas de test échouent.','Revoir la gestion des erreurs.'],
    ['Résultat correct mais le code manque de clarté.','Les noms de variables sont trop courts.',
     'Ajouter des docstrings aux fonctions.'],
    ['Devoir incomplet.','La partie théorique est absente.','Revoir le cours avant de resoumettre.'],
    ['Très bonne maîtrise du sujet.','Code propre et bien documenté.','Note maximale méritée.'],
    ['Bonne approche, mais algorithme sous-optimal.','Préférer un tri fusion pour les grands tableaux.'],
    ['Rapport bien rédigé.','Les mesures sont précises.','La conclusion est claire et pertinente.'],
]

submissions_list = []
correction_results_dict = {}
plagiarism_results_dict = {}

sub_id = 1

def add_submission(student_username, assignment_id, filename, score, max_score, feedback_idx,
                   is_code=False, lang='python', plagiarism_pct=0):
    global sub_id
    sub_date = (NOW - timedelta(days=random.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S')
    correction = {
        'score': score, 'max_score': max_score,
        'feedback': FEEDBACK_POOL[feedback_idx % len(FEEDBACK_POOL)],
        'auto_generated': False, 'ai_model': None
    }
    plagiarism = {
        'similarity': plagiarism_pct,
        'sources': [f'Similarité avec soumission précédente ({plagiarism_pct}%)'] if plagiarism_pct > 20 else [],
        'status': 'suspect' if plagiarism_pct > 60 else 'attention' if plagiarism_pct > 30 else 'acceptable',
        'details': {'checked_submissions': 5, 'web_checked': False}
    }
    sub = {
        'id': sub_id, 'student': student_username, 'assignment_id': assignment_id,
        'filename': filename, 'submitted_at': sub_date, 'results_available': True,
        'correction': correction, 'plagiarism': plagiarism,
    }
    if is_code:
        sub['code_submission'] = True
        sub['language'] = lang
        sub['execution_result'] = {'status': 'Exécuté', 'stdout': 'OK', 'stderr': '', 'success': True, 'time': '0.12', 'memory': '1024'}
    correction_results_dict[sub_id] = correction
    plagiarism_results_dict[sub_id] = plagiarism
    submissions_list.append(sub)
    sub_id += 1
    return sub['id']


# ════════════════════════════════════════════════════════════════════════════
# 3.  GÉNÉRATION DES FICHIERS
# ════════════════════════════════════════════════════════════════════════════

print('\n=== Génération des fichiers de cours ===')

# ── Cours 1 : Algorithmique (PDF + PPTX + DOCX) ───────────────────────────────
make_pdf_cours(
    os.path.join(CHAPTERS, 'asd_chapitre1_complexite.pdf'),
    'Algorithmique — Chap. 1 : Complexité', 'Prof. Jean-Baptiste Mukendi',
    [
        ('1. Introduction à la complexité algorithmique', [
            'La complexité algorithmique mesure les ressources nécessaires à l\'exécution d\'un algorithme.',
            'On distingue la complexité temporelle (temps d\'exécution) et spatiale (mémoire utilisée).',
            '• Notation O (grand O) : borne supérieure asymptotique.',
            '• Notation Θ (grand Thêta) : borne asymptotique serrée.',
            '• Notation Ω (grand Oméga) : borne inférieure asymptotique.',
        ]),
        ('2. Complexités usuelles', [
            'Les complexités les plus courantes, classées de la plus efficace à la moins efficace :',
            '• O(1) — temps constant : accès tableau, opérations arithmétiques.',
            '• O(log n) — logarithmique : recherche dichotomique, arbres équilibrés.',
            '• O(n) — linéaire : parcours séquentiel.',
            '• O(n log n) — quasi-linéaire : tri fusion, tri rapide (moyenne).',
            '• O(n²) — quadratique : tri à bulles, tri par insertion (pire cas).',
            '• O(2ⁿ) — exponentielle : problèmes NP-complets, sous-ensembles.',
        ]),
        ('3. Analyse du tri par insertion', [
            'Le tri par insertion parcourt le tableau et insère chaque élément à sa bonne position.',
            'Meilleur cas (tableau trié) : O(n) — une seule passe sans échange.',
            'Pire cas (tableau inversé) : O(n²) — chaque insertion nécessite n comparaisons.',
            'Avantage : efficace sur de petits tableaux et sur des tableaux quasi-triés.',
        ]),
    ]
)

make_ppt_cours(
    os.path.join(CHAPTERS, 'asd_chapitre2_arbres.pptx'),
    'Algorithmique — Chap. 2 : Arbres', 'Prof. Jean-Baptiste Mukendi',
    [
        ('Définition d\'un arbre', [
            'Un arbre est une structure de données hiérarchique non linéaire.',
            'Composé de nœuds reliés par des arêtes.',
            'Un nœud racine, des nœuds internes, des feuilles.',
            'Propriété : pas de cycle.',
        ]),
        ('Arbre Binaire de Recherche (ABR)', [
            'Chaque nœud a au plus deux enfants.',
            'Enfant gauche < nœud < enfant droit.',
            'Recherche, insertion, suppression en O(log n) en moyenne.',
            'Dégénère en O(n) si l\'arbre est déséquilibré.',
        ]),
        ('Parcours d\'un arbre', [
            'Infixe (gauche → racine → droite) → tri croissant pour ABR.',
            'Préfixe (racine → gauche → droite) → copie d\'arbre.',
            'Suffixe (gauche → droite → racine) → suppression.',
            'Largeur (BFS) → niveaux successifs.',
        ]),
        ('Arbres équilibrés', [
            'AVL : différence de hauteur entre sous-arbres ≤ 1.',
            'Rotations simples et doubles pour rééquilibrer.',
            'Arbre rouge-noir : garantit O(log n) dans tous les cas.',
            'Applications : Java TreeMap, C++ std::map.',
        ]),
        ('Implémentation Python', [
            'class Noeud: def __init__(self, val): self.val=val; self.gauche=None; self.droite=None',
            'Insertion récursive : comparer et descendre.',
            'Suppression : 3 cas (feuille, un enfant, deux enfants).',
            'Utiliser une pile pour simuler la récursion.',
        ]),
    ]
)

make_word_cours(
    os.path.join(CHAPTERS, 'asd_chapitre3_graphes.docx'),
    'Algorithmique — Chap. 3 : Graphes', 'Prof. Jean-Baptiste Mukendi',
    [
        ('Définition et représentation', [
            'Un graphe G = (V, E) est composé de sommets V et d\'arêtes E.',
            'Graphe orienté (digraphe) : les arêtes ont une direction.',
            'Graphe pondéré : chaque arête a un poids/coût associé.',
            '• Matrice d\'adjacence : O(V²) en espace, O(1) pour tester une arête.',
            '• Liste d\'adjacence : O(V+E) en espace, plus efficace pour les graphes creux.',
        ]),
        ('Algorithme BFS (Parcours en largeur)', [
            'Utilise une file (FIFO) pour explorer les sommets niveau par niveau.',
            'Complexité : O(V + E).',
            'Applications : plus court chemin dans un graphe non pondéré, détection de cycles.',
            'Initialiser la distance de la source à 0, toutes les autres à l\'infini.',
        ]),
        ('Algorithme DFS (Parcours en profondeur)', [
            'Utilise une pile (LIFO) ou la récursion pour explorer en profondeur.',
            'Complexité : O(V + E).',
            'Applications : tri topologique, composantes connexes, détection de cycles.',
            'Timestamps de découverte et finalisation pour l\'analyse.',
        ]),
        ('Algorithme de Dijkstra', [
            'Trouve le plus court chemin dans un graphe pondéré positivement.',
            'Utilise une file à priorité (tas min).',
            'Complexité : O((V + E) log V) avec un tas binaire.',
            'Ne fonctionne pas avec des poids négatifs (utiliser Bellman-Ford).',
        ]),
    ]
)

# ── Cours 2 : Python (PDF + DOCX TP) ─────────────────────────────────────────
make_pdf_cours(
    os.path.join(CHAPTERS, 'python_chapitre1_bases.pdf'),
    'Programmation Python — Chap. 1 : Bases', 'Prof. Jean-Baptiste Mukendi',
    [
        ('1. Variables et types de données', [
            'Python est un langage à typage dynamique fort.',
            '• int, float, complex : nombres entiers, flottants, complexes.',
            '• str : chaîne de caractères immuable.',
            '• bool : True ou False (sous-classe de int).',
            '• NoneType : valeur None, représente l\'absence de valeur.',
            'Affectation multiple : a, b, c = 1, 2, 3',
        ]),
        ('2. Structures de contrôle', [
            'if / elif / else : exécution conditionnelle.',
            'for i in range(n) : boucle numérique.',
            'for elem in collection : boucle sur un itérable.',
            'while condition : boucle conditionnelle.',
            'break, continue, pass : contrôle de boucle.',
            'Compréhension de liste : [x**2 for x in range(10) if x % 2 == 0]',
        ]),
        ('3. Fonctions', [
            'def ma_fonction(param1, param2=valeur_defaut): ...',
            'Arguments positionnels, nommés, *args, **kwargs.',
            'Fonctions récursives : s\'appeler soi-même avec un cas de base.',
            'Fonctions lambda : lambda x, y: x + y',
            'Portée des variables : LEGB (Local, Enclosing, Global, Built-in).',
        ]),
        ('4. Programmation Orientée Objet', [
            'class MaClasse: : définition d\'une classe.',
            '__init__(self, ...) : constructeur.',
            'self : référence à l\'instance courante.',
            'Héritage : class Fille(Mere): ...',
            'Méthodes spéciales : __str__, __repr__, __len__, __eq__.',
            'Encapsulation : attributs "privés" par convention avec _.',
        ]),
    ]
)

make_word_tp(
    os.path.join(ASSIGN, 'devoir_python_contacts.pdf'),
    'Projet Python — Gestionnaire de contacts', 'Prof. Jean-Baptiste Mukendi',
    [
        'Créer une classe Contact avec les attributs : nom, prénom, téléphone, email. Implémenter __str__ et __repr__.',
        'Créer une classe GestionnaireContacts qui maintient une liste de contacts. Ajouter les méthodes : ajouter(contact), supprimer(nom), rechercher(terme), lister().',
        'Persister les contacts dans un fichier JSON. Charger les contacts au démarrage et sauvegarder après chaque modification.',
        'Implémenter un menu en ligne de commande interactif permettant toutes les opérations.',
        'Ajouter la gestion des doublons : refuser l\'ajout d\'un contact avec un email déjà existant.',
    ]
)

# ── Cours 3 : BDD (PDF) ───────────────────────────────────────────────────────
make_pdf_devoir(
    os.path.join(ASSIGN, 'devoir_sql_avance.pdf'),
    'Devoir SQL — Requêtes avancées', 'CT Marie-Claire Ngoma',
    [
        'Schéma : Étudiant(id, nom, promotion), Cours(id, intitule, credits), Inscription(etudiant_id, cours_id, note).',
        'Question 1 : Lister tous les étudiants avec leur moyenne générale (sur tous les cours).',
        'Question 2 : Trouver les étudiants qui n\'ont pas encore de note pour le cours "Bases de Données".',
        'Question 3 : Calculer le taux de réussite (note ≥ 10) par cours.',
        'Question 4 : Lister les étudiants ayant une moyenne > 14 dans au moins 3 cours.',
        'Question 5 : Créer une vue "bulletin" affichant nom, cours et note pour chaque étudiant.',
    ],
    [['Liste étudiants + moyenne (Q1)', '4 pts'],
     ['Étudiants sans note BDD (Q2)',   '3 pts'],
     ['Taux de réussite par cours (Q3)', '5 pts'],
     ['Étudiants moyenne >14 ≥3 cours (Q4)', '4 pts'],
     ['Vue bulletin (Q5)',               '4 pts']]
)

# ── Cours 5 : Circuits (PDF devoir) ───────────────────────────────────────────
make_pdf_devoir(
    os.path.join(ASSIGN, 'devoir_circuits_ao.pdf'),
    'Labo Circuits — Amplificateur opérationnel', 'Ass. François Kabila',
    [
        'Partie 1 — Théorie : Rappeler les caractéristiques idéales d\'un amplificateur opérationnel (AO).',
        'Partie 2 — Calcul : Calculer le gain en tension du montage inverseur avec R1=10kΩ et R2=100kΩ.',
        'Partie 3 — Calcul : Calculer le gain du montage non-inverseur avec les mêmes résistances.',
        'Partie 4 — Pratique : Monter les circuits sur plaque d\'essai et relever les tensions en entrée/sortie.',
        'Partie 5 — Rapport : Comparer les résultats théoriques et expérimentaux. Analyser les écarts.',
    ],
    [['Théorie AO idéal (P1)', '2 pts'],
     ['Calcul montage inverseur (P2)', '4 pts'],
     ['Calcul montage non-inverseur (P3)', '4 pts'],
     ['Mesures expérimentales (P4)', '6 pts'],
     ['Rapport comparatif (P5)', '4 pts']]
)

# ── Cours 6 : Maths (PDF) ─────────────────────────────────────────────────────
make_pdf_devoir(
    os.path.join(ASSIGN, 'devoir_algebre_lineaire.pdf'),
    'Interrogation — Algèbre linéaire', 'Prof. Sophie Mwamba',
    [
        'Exercice 1 : Résoudre le système linéaire Ax = b où A = [[2,1,-1],[1,3,2],[1,-1,4]] et b = [8,11,3].',
        'Exercice 2 : Calculer les valeurs propres et vecteurs propres de la matrice B = [[4,1],[2,3]].',
        'Exercice 3 : Vérifier si les vecteurs v1=(1,2,3), v2=(4,5,6), v3=(7,8,9) sont linéairement indépendants.',
        'Exercice 4 : Calculer le déterminant et l\'inverse de la matrice C = [[1,2,3],[0,1,4],[5,6,0]].',
    ],
    [['Système linéaire Ax=b (Ex.1)', '5 pts'],
     ['Valeurs/vecteurs propres (Ex.2)', '6 pts'],
     ['Indépendance linéaire (Ex.3)', '4 pts'],
     ['Déterminant + inverse (Ex.4)', '5 pts']]
)

# ── Cours 7 : Mécaflu (PDF) ──────────────────────────────────────────────────
make_pdf_devoir(
    os.path.join(ASSIGN, 'devoir_bernoulli.pdf'),
    'TD — Équation de Bernoulli', 'Prof. Pierre Lumumba',
    [
        'Problème : De l\'eau s\'écoule dans une conduite horizontale. Section 1 : diamètre 20cm, vitesse 2m/s, pression 200kPa. Section 2 : diamètre 10cm.',
        'Question 1 : Calculer la vitesse à la section 2 (équation de continuité).',
        'Question 2 : Calculer la pression à la section 2 (équation de Bernoulli).',
        'Question 3 : Calculer la force exercée sur le convergent.',
        'Question 4 : Calculer le débit volumique Q et le débit massique (ρ=1000 kg/m³).',
    ],
    [['Vitesse section 2 (Q1)', '4 pts'],
     ['Pression section 2 (Q2)', '6 pts'],
     ['Force sur convergent (Q3)', '5 pts'],
     ['Débits volumique et massique (Q4)', '5 pts']]
)

# ── Cours 1 : ASD — énoncé devoir (PDF) ──────────────────────────────────────
make_pdf_devoir(
    os.path.join(ASSIGN, 'devoir_asd_tri.pdf'),
    'TP1 — Tri par insertion et tri rapide', 'Prof. Jean-Baptiste Mukendi',
    [
        'Partie 1 — Implémentation : Coder en Python les fonctions tri_insertion(tab) et tri_rapide(tab).',
        'Partie 2 — Tests : Tester avec des tableaux de tailles 10, 100, 1000, 10000 éléments.',
        'Partie 3 — Mesure : Utiliser time.perf_counter() pour mesurer les temps d\'exécution.',
        'Partie 4 — Analyse : Tracer un graphique comparatif (matplotlib). Commenter les résultats.',
        'Partie 5 — Rapport : Rédiger un rapport de 2 pages avec code, résultats et conclusion.',
    ],
    [['Implémentation correcte des 2 algorithmes (P1)', '6 pts'],
     ['Tests exhaustifs (P2)', '3 pts'],
     ['Mesure des temps (P3)', '4 pts'],
     ['Graphique + analyse (P4)', '4 pts'],
     ['Rapport écrit (P5)', '3 pts']]
)

# ── PowerPoint Cours BDD ──────────────────────────────────────────────────────
make_ppt_cours(
    os.path.join(CHAPTERS, 'bdd_chapitre1_introduction.pptx'),
    'Bases de Données — Introduction', 'CT Marie-Claire Ngoma',
    [
        ('Qu\'est-ce qu\'une base de données ?', [
            'Collection organisée de données structurées.',
            'Géré par un SGBD (Système de Gestion de Bases de Données).',
            'Exemples : MySQL, PostgreSQL, Oracle, SQLite.',
            'Avantage : évite la redondance, assure la cohérence.',
        ]),
        ('Modèle relationnel', [
            'Table = relation = ensemble de n-uplets.',
            'Attribut = colonne = domaine de valeurs.',
            'Clé primaire : identifiant unique d\'une ligne.',
            'Clé étrangère : référence vers une autre table.',
            'Contraintes d\'intégrité référentielle.',
        ]),
        ('Langage SQL', [
            'DDL : CREATE TABLE, ALTER TABLE, DROP TABLE.',
            'DML : INSERT, UPDATE, DELETE, SELECT.',
            'DCL : GRANT, REVOKE.',
            'TCL : COMMIT, ROLLBACK, SAVEPOINT.',
        ]),
        ('Requêtes SELECT avancées', [
            'JOIN : INNER, LEFT, RIGHT, FULL OUTER.',
            'GROUP BY + HAVING : agrégation conditionnelle.',
            'Sous-requêtes corrélées et non corrélées.',
            'Fonctions d\'agrégation : COUNT, SUM, AVG, MIN, MAX.',
            'Fenêtrage : OVER (PARTITION BY ... ORDER BY ...).',
        ]),
        ('Normalisation', [
            '1NF : attributs atomiques, pas de groupes répétés.',
            '2NF : éliminer les dépendances partielles (si clé composée).',
            '3NF : éliminer les dépendances transitives.',
            'BCNF : forme normale de Boyce-Codd (plus stricte).',
        ]),
    ]
)

make_ppt_cours(
    os.path.join(CHAPTERS, 'circuits_chapitre1_ao.pptx'),
    'Circuits Électroniques — Amplificateur opérationnel', 'Ass. François Kabila',
    [
        ('L\'amplificateur opérationnel', [
            'Composant actif à deux entrées différentielles.',
            'Entrée inverseuse (−) et entrée non-inverseuse (+).',
            'Sortie : Vout = A × (V+ − V−) avec A très grand (>100 000).',
            'AO idéal : gain infini, impédance entrée infinie, impédance sortie nulle.',
        ]),
        ('Montage inverseur', [
            'Entrée sur la borne inverseuse via R1.',
            'Rétroaction négative via R2 de la sortie à l\'entrée −.',
            'Gain : Av = −R2/R1.',
            'Impédance d\'entrée : Zin = R1.',
            'Exemple : R1=10kΩ, R2=100kΩ → Av = −10.',
        ]),
        ('Montage non-inverseur', [
            'Signal appliqué à l\'entrée +.',
            'R1 de l\'entrée − à la masse, R2 de la sortie à l\'entrée −.',
            'Gain : Av = 1 + R2/R1.',
            'Impédance d\'entrée très élevée.',
            'Exemple : R1=10kΩ, R2=90kΩ → Av = +10.',
        ]),
        ('Comparateur et Schmitt trigger', [
            'Comparateur : sortie saturée positive ou négative.',
            'Schmitt trigger : hysteresis pour éviter les oscillations.',
            'Seuil haut et seuil bas définis par le pont diviseur.',
            'Application : détection de niveau, mise en forme de signal.',
        ]),
    ]
)

# ── Syllabus (DOCX) ──────────────────────────────────────────────────────────
make_word_cours(
    os.path.join(SYLLABUS, 'syllabus_info_l2_asd.docx'),
    'Syllabus — Algorithmique et Structures de Données', 'Prof. Jean-Baptiste Mukendi',
    [
        ('Description du cours', [
            'Ce cours présente les algorithmes fondamentaux et les structures de données utilisées en informatique.',
            'Prérequis : Programmation Python (INFO-L1-PY), Mathématiques discrètes.',
        ]),
        ('Objectifs pédagogiques', [
            '• Maîtriser l\'analyse de la complexité algorithmique.',
            '• Implémenter et utiliser les principales structures de données.',
            '• Concevoir des algorithmes efficaces pour des problèmes courants.',
            '• Analyser les compromis temps/espace des différentes solutions.',
        ]),
        ('Programme détaillé (14 semaines)', [
            'Semaines 1-2 : Introduction, complexité, notation O.',
            'Semaines 3-4 : Tableaux, listes chaînées, piles, files.',
            'Semaines 5-6 : Algorithmes de tri (insertion, fusion, rapide, tas).',
            'Semaines 7-8 : Arbres binaires, ABR, arbres équilibrés (AVL).',
            'Semaines 9-10 : Tables de hachage, résolution de collisions.',
            'Semaines 11-12 : Graphes, BFS, DFS, tri topologique.',
            'Semaines 13-14 : Plus courts chemins (Dijkstra, Bellman-Ford), révisions.',
        ]),
        ('Évaluation', [
            '• TPs (TP1 + TP2) : 40% de la note finale.',
            '• Examen mi-semestre : 20%.',
            '• Examen final : 40%.',
            'Présence obligatoire aux séances de TP.',
        ]),
        ('Bibliographie', [
            'Introduction to Algorithms — Cormen, Leiserson, Rivest, Stein (MIT Press).',
            'Algorithmique — Cours avec 957 exercices et 158 problèmes — Beauquier, Berstel, Chrétienne.',
            'Data Structures and Algorithms in Python — Goodrich, Tamassia, Goldwasser.',
        ]),
    ]
)

# ════════════════════════════════════════════════════════════════════════════
# 4.  SOUMISSIONS ÉTUDIANTES (fichiers + entrées JSON)
# ════════════════════════════════════════════════════════════════════════════
print('\n=== Génération des soumissions ===')

# Devoir 1 : TP1 Tri — étudiants L2 Info
for (student, score, fb, plag) in [
    ('ruth.nkulu',   17, 5, 0),
    ('joel.kabongo', 14, 1, 0),
    ('deborah.mutombo', 12, 2, 0),
    ('samuel.luboya', 16, 0, 35),  # similarité suspecte
    ('samuel.luboya_copy', None, None, None),  # simulé
]:
    if student == 'samuel.luboya_copy':
        continue
    fname = f"sub_{student}_asgn1_{sub_id:03d}.py"
    fpath = os.path.join(CODE_DIR, fname)
    make_student_code(fpath, student, 'TP1 — Tri', [
        "def tri_insertion(tab):",
        "    for i in range(1, len(tab)):",
        "        cle = tab[i]",
        "        j = i - 1",
        "        while j >= 0 and tab[j] > cle:",
        "            tab[j + 1] = tab[j]",
        "            j -= 1",
        "        tab[j + 1] = cle",
        "    return tab",
        "",
        "def tri_rapide(tab):",
        "    if len(tab) <= 1:",
        "        return tab",
        "    pivot = tab[len(tab) // 2]",
        "    gauche = [x for x in tab if x < pivot]",
        "    milieu = [x for x in tab if x == pivot]",
        "    droite = [x for x in tab if x > pivot]",
        "    return tri_rapide(gauche) + milieu + tri_rapide(droite)",
        "",
        "import time",
        "import random",
        "for n in [10, 100, 1000]:",
        "    tab = [random.randint(0, 10000) for _ in range(n)]",
        "    t0 = time.perf_counter()",
        "    tri_rapide(tab[:])",
        "    print(f'n={n}: {time.perf_counter()-t0:.5f}s')",
    ])
    add_submission(student, 1, fname, score, 20, fb, is_code=True, lang='python', plagiarism_pct=plag)

# Devoir 3 : Projet Python Contacts — étudiants L1
for (student, score, fb, plag) in [
    ('grace.kasongo',    16, 0, 0),
    ('elie.tshisekedi',  14, 1, 0),
    ('willy.tshilombo',  10, 2, 0),
    ('nadege.lukusa',    12, 2, 25),
    ('david.mulamba',    18, 5, 0),
    ('prisca.kalombo',   11, 2, 0),
]:
    fname = f"sub_{student}_asgn3_{sub_id:03d}.py"
    fpath = os.path.join(CODE_DIR, fname)
    make_student_code(fpath, student, 'Projet Python — Gestionnaire de contacts', [
        "import json, os",
        "",
        "class Contact:",
        "    def __init__(self, nom, prenom, telephone, email):",
        "        self.nom = nom",
        "        self.prenom = prenom",
        "        self.telephone = telephone",
        "        self.email = email",
        "",
        "    def to_dict(self):",
        "        return {'nom':self.nom,'prenom':self.prenom,",
        "                'telephone':self.telephone,'email':self.email}",
        "",
        "    def __str__(self):",
        "        return f'{self.prenom} {self.nom} — {self.telephone} — {self.email}'",
        "",
        "class GestionnaireContacts:",
        "    def __init__(self, fichier='contacts.json'):",
        "        self.fichier = fichier",
        "        self.contacts = []",
        "        self._charger()",
        "",
        "    def ajouter(self, contact):",
        "        if any(c.email == contact.email for c in self.contacts):",
        "            raise ValueError('Email déjà existant')",
        "        self.contacts.append(contact)",
        "        self._sauvegarder()",
        "",
        "    def lister(self):",
        "        return self.contacts",
        "",
        "    def _sauvegarder(self):",
        "        with open(self.fichier, 'w') as f:",
        "            json.dump([c.to_dict() for c in self.contacts], f, indent=2)",
        "",
        "    def _charger(self):",
        "        if os.path.exists(self.fichier):",
        "            with open(self.fichier) as f:",
        "                for d in json.load(f):",
        "                    self.contacts.append(Contact(**d))",
    ])
    add_submission(student, 3, fname, score, 20, fb, is_code=True, lang='python', plagiarism_pct=plag)

# Devoir 4 : SQL — étudiants L2 Info
for (student, score, fb, plag) in [
    ('ruth.nkulu',    15, 0, 0),
    ('joel.kabongo',  12, 1, 0),
    ('herve.mukendi', 17, 5, 0),
    ('deborah.mutombo', 11, 2, 70),  # plagiat suspect
    ('samuel.luboya',  9, 4, 72),
]:
    fname = f"sub_{student}_asgn4_{sub_id:03d}.docx"
    fpath = os.path.join(SUBMITS, fname)
    make_student_text(fpath, student, 'Devoir SQL — Requêtes avancées', [
        f'Étudiant : {student}',
        '',
        'Question 1 — Moyenne par étudiant :',
        'SELECT e.nom, AVG(i.note) AS moyenne_generale',
        'FROM Etudiant e JOIN Inscription i ON e.id = i.etudiant_id',
        'GROUP BY e.id, e.nom ORDER BY moyenne_generale DESC;',
        '',
        'Question 2 — Étudiants sans note BDD :',
        'SELECT e.nom FROM Etudiant e',
        'WHERE e.id NOT IN (SELECT i.etudiant_id FROM Inscription i',
        '  JOIN Cours c ON i.cours_id = c.id WHERE c.intitule = \'Bases de Données\');',
        '',
        'Question 3 — Taux de réussite :',
        'SELECT c.intitule, ROUND(100.0 * SUM(CASE WHEN i.note >= 10 THEN 1 ELSE 0 END) / COUNT(*), 2) AS taux_reussite',
        'FROM Cours c JOIN Inscription i ON c.id = i.cours_id',
        'GROUP BY c.id, c.intitule ORDER BY taux_reussite DESC;',
    ])
    add_submission(student, 4, fname, score, 20, fb, is_code=False, plagiarism_pct=plag)

# Devoir 6 : Circuits AO — étudiants L2 Électrique
for (student, score, fb, plag) in [
    ('esther.mwangi',   14, 1, 0),
    ('micheline.ngandu', 16, 0, 0),
    ('christelle.ilunga', 10, 2, 0),
]:
    fname = f"sub_{student}_asgn6_{sub_id:03d}.docx"
    fpath = os.path.join(SUBMITS, fname)
    make_student_text(fpath, student, 'Labo Circuits — Amplificateur opérationnel', [
        f'Rapport de laboratoire — {student}',
        '',
        'Partie 1 — Caractéristiques idéales de l\'AO :',
        'Gain en tension infini (A → ∞), impédance d\'entrée infinie (Zin → ∞),',
        'impédance de sortie nulle (Zout = 0), bande passante infinie, décalage nul.',
        '',
        'Partie 2 — Montage inverseur :',
        'Avec R1 = 10kΩ et R2 = 100kΩ :',
        'Av = -R2/R1 = -100kΩ/10kΩ = -10',
        'Le signal de sortie est amplifié 10 fois et inversé.',
        '',
        'Partie 3 — Montage non-inverseur :',
        'Av = 1 + R2/R1 = 1 + 100k/10k = 11',
        'Le signal de sortie est amplifié 11 fois sans inversion.',
        '',
        'Parties 4 & 5 — Mesures et analyse :',
        'Les mesures expérimentales confirment la théorie à ±3% près.',
        'Les écarts sont dus aux tolérances des résistances (±5%) et à la limitation en courant de l\'AO réel.',
    ])
    add_submission(student, 6, fname, score, 20, fb, is_code=False, plagiarism_pct=plag)

# Devoir 7 : Algèbre — tous promos L1 et L2
for (student, score, fb, plag) in [
    ('grace.kasongo',    13, 2, 0),
    ('elie.tshisekedi',  15, 0, 0),
    ('ruth.nkulu',       18, 5, 0),
    ('joel.kabongo',     12, 1, 0),
    ('herve.mukendi',    16, 0, 0),
    ('prisca.kalombo',    9, 4, 0),
    ('nadege.lukusa',    11, 2, 0),
    ('esther.mwangi',   14, 1, 0),
]:
    fname = f"sub_{student}_asgn7_{sub_id:03d}.docx"
    fpath = os.path.join(SUBMITS, fname)
    make_student_text(fpath, student, 'Interrogation — Algèbre linéaire', [
        f'Étudiant : {student}',
        '',
        'Exercice 1 — Résolution de Ax=b par la méthode de Gauss-Jordan :',
        'Après pivot, on obtient x1=2, x2=3, x3=-1.',
        '',
        'Exercice 2 — Valeurs propres de B :',
        'det(B - λI) = (4-λ)(3-λ) - 2 = λ² - 7λ + 10 = 0',
        'λ1 = 5, λ2 = 2',
        'Vecteur propre pour λ1=5 : v1 = (1, 1)',
        'Vecteur propre pour λ2=2 : v2 = (-1, 2)',
        '',
        'Exercice 3 — Indépendance linéaire :',
        'det([v1,v2,v3]) = det([[1,4,7],[2,5,8],[3,6,9]]) = 0',
        'Les vecteurs sont linéairement dépendants (v3 = 2v2 - v1).',
    ])
    add_submission(student, 7, fname, score, 20, fb, is_code=False, plagiarism_pct=plag)

# Devoir 8 : Bernoulli — étudiants L3 Méca
for (student, score, fb, plag) in [
    ('emmanuel.mbuyi',  14, 1, 0),
    ('patrick.kapumba', 12, 2, 0),
    ('kevin.kabamba',   16, 0, 0),
]:
    fname = f"sub_{student}_asgn8_{sub_id:03d}.docx"
    fpath = os.path.join(SUBMITS, fname)
    make_student_text(fpath, student, 'TD — Équation de Bernoulli', [
        f'Étudiant : {student}',
        '',
        'Q1 — Vitesse section 2 (équation de continuité) :',
        'A1·V1 = A2·V2  →  V2 = A1/A2 × V1 = (D1/D2)² × V1',
        'V2 = (0.20/0.10)² × 2 = 4 × 2 = 8 m/s',
        '',
        'Q2 — Pression section 2 (Bernoulli) :',
        'P1 + ½ρV1² = P2 + ½ρV2²',
        'P2 = P1 + ½ρ(V1² - V2²) = 200000 + ½×1000×(4-64)',
        'P2 = 200000 - 30000 = 170 kPa',
        '',
        'Q3 — Débit volumique :',
        'Q = A1 × V1 = π×(0.10)²×2 = 0.0628 m³/s',
        'Débit massique : ṁ = ρQ = 1000 × 0.0628 = 62.8 kg/s',
    ])
    add_submission(student, 8, fname, score, 20, fb, is_code=False, plagiarism_pct=plag)


# ════════════════════════════════════════════════════════════════════════════
# 5.  ASSEMBLAGE DU JSON FINAL
# ════════════════════════════════════════════════════════════════════════════
print('\n=== Assemblage du fichier JSON ===')

users_dict = {
    'admin': {
        'password':  generate_password_hash('Admin@ULC2024'),
        'role':      'admin',
        'name':      'Administrateur ULC-ICAM',
        'email':     'admin@ulc-icam.cd',
    }
}
for p in PROFS:
    users_dict[p['username']] = p
for e in ETUDIANTS:
    users_dict[e['username']] = e

# Intégrer correction_results et plagiarism_results dans les soumissions
for sub in submissions_list:
    sid = sub['id']
    if sid in correction_results_dict:
        sub['correction']  = correction_results_dict[sid]
    if sid in plagiarism_results_dict:
        sub['plagiarism']  = plagiarism_results_dict[sid]

data_final = {
    'users':               users_dict,
    'admin_courses':       COURSES,
    'course_assignments':  COURSE_ASSIGNMENTS,
    'course_enrollments':  COURSE_ENROLLMENTS,
    'assignments':         ASSIGNMENTS,
    'submissions':         submissions_list,
    'next_course_admin_id': len(COURSES) + 1,
    'next_assignment_id':   len(ASSIGNMENTS) + 1,
}

with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
    json.dump(data_final, f, ensure_ascii=False, indent=2)

print(f'\n✅ ulc_icam_data.json généré')
print(f'   Utilisateurs   : {len(users_dict)} ({len(PROFS)} profs, {len(ETUDIANTS)} étudiants, 1 admin)')
print(f'   Cours          : {len(COURSES)}')
print(f'   Devoirs        : {len(ASSIGNMENTS)}')
print(f'   Soumissions    : {len(submissions_list)}')
print(f'   Inscriptions   : {sum(len(v) for v in COURSE_ENROLLMENTS.values())} (total étudiant×cours)')

# Compter les fichiers générés
total_files = sum(
    len(files) for _, _, files in os.walk(UPLOAD)
)
print(f'   Fichiers cours : {total_files} fichiers dans uploads/')
print('\n📋 Identifiants par défaut :')
print('   Admin     → login: admin        | mdp: Admin@ULC2024')
print('   Profs     → login: jb.mukendi   | mdp: Prof@2024')
print('   Étudiants → login: grace.kasongo | mdp: Etudiant@2024')
