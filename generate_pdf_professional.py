#!/usr/bin/env python3
"""
Générateur PDF Professionnel pour ULC-ICAM Turnin System
"""

import os
import webbrowser
from pathlib import Path

def create_professional_html():
    """Crée une version HTML professionnelle optimisée"""
    
    md_file = Path("presentation_detaillee.md")
    if not md_file.exists():
        print("❌ Fichier presentation_detaillee.md non trouvé")
        return None
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    html_content = convert_markdown_to_html(content)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>ULC-ICAM Turnin System - Présentation Professionnelle</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            font-size: 11pt;
            margin: 0;
            padding: 0;
            background: #ffffff;
        }}
        
        .cover-page {{
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 40px;
            page-break-after: always;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .logo-container {{
            margin: 30px 0;
        }}
        
        .logo {{
            width: 120px;
            height: 120px;
            background: white;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            padding: 10px;
        }}
        
        .logo img {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
        }}
        
        .main-title {{
            font-size: 28pt;
            font-weight: 700;
            margin: 30px 0 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            letter-spacing: 1px;
        }}
        
        .subtitle {{
            font-size: 16pt;
            font-weight: 300;
            margin: 20px 0;
            opacity: 0.95;
        }}
        
        .university {{
            font-size: 14pt;
            margin: 25px 0;
            font-weight: 400;
        }}
        
        .developer-info {{
            background: rgba(255,255,255,0.15);
            padding: 30px;
            border-radius: 12px;
            margin: 40px auto;
            max-width: 600px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .developer-name {{
            font-size: 24pt;
            font-weight: 600;
            margin: 15px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }}
        
        .developer-title {{
            font-size: 13pt;
            margin: 10px 0;
            opacity: 0.9;
        }}
        
        .contact-info {{
            font-size: 12pt;
            margin: 15px 0;
            font-weight: 400;
        }}
        
        .version-info {{
            font-size: 12pt;
            margin-top: 25px;
            font-weight: 500;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            page-break-before: always;
            font-size: 20pt;
            font-weight: 600;
            margin: 40px 0 25px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        h1:first-of-type {{
            page-break-before: auto;
        }}
        
        h2 {{
            color: #34495e;
            border-left: 5px solid #e74c3c;
            padding-left: 20px;
            font-size: 16pt;
            font-weight: 600;
            margin: 30px 0 20px;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
        }}
        
        h3 {{
            color: #8e44ad;
            font-size: 14pt;
            font-weight: 600;
            margin: 25px 0 15px;
            border-bottom: 1px solid #e8e8e8;
            padding-bottom: 8px;
        }}
        
        h4 {{
            color: #27ae60;
            font-size: 12pt;
            font-weight: 600;
            margin: 20px 0 10px;
        }}
        
        p {{
            margin: 12px 0;
            text-align: justify;
            line-height: 1.8;
        }}
        
        code {{
            background-color: #f1f2f6;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            color: #e74c3c;
            border: 1px solid #ddd;
        }}
        
        pre {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            font-size: 9pt;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        pre code {{
            background: none;
            border: none;
            padding: 0;
            color: #2c3e50;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 10pt;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tr:hover {{
            background-color: #e3f2fd;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        
        blockquote {{
            border-left: 5px solid #3498db;
            margin: 25px 0;
            padding: 20px 25px;
            background: linear-gradient(135deg, #ebf3fd 0%, #f8fbff 100%);
            font-style: italic;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid #f39c12;
            border-radius: 10px;
            padding: 20px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(243,156,18,0.2);
        }}
        
        .success-box {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #27ae60;
            border-radius: 10px;
            padding: 20px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(39,174,96,0.2);
        }}
        
        .info-box {{
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border: 2px solid #17a2b8;
            border-radius: 10px;
            padding: 20px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(23,162,184,0.2);
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(102,126,234,0.3);
        }}
        
        .stat-number {{
            font-size: 32pt;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .footer-section {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin-top: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .toc {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .toc h2 {{
            margin-top: 0;
            color: #2c3e50;
            text-align: center;
        }}
        
        @media print {{
            .no-print {{
                display: none;
            }}
            
            body {{
                font-size: 10pt;
            }}
            
            .cover-page {{
                margin-bottom: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="logo-container">
            <div class="logo">
                <img src="static/images/ulc-icam-logo.png" alt="ULC-ICAM Logo">
            </div>
        </div>
        
        <h1 class="main-title">ULC-ICAM TURNIN SYSTEM</h1>
        <p class="subtitle">Système de Gestion de Devoirs et Soumissions de Code</p>
        <p class="university">Université Loyola du Congo - Institut Catholique d'Arts et Métiers</p>
        
        <div class="developer-info">
            <h3 style="margin-top: 0; color: white; border: none;">Développé par</h3>
            <h2 class="developer-name">Jonathan Kakesa Nayaba</h2>
            <p class="developer-title">Ingénieur Logiciel & Développeur Full-Stack</p>
            <p class="contact-info">📧 jkakesa9@gmail.com | 📱 +1 (438)-529-9073</p>
            <p class="version-info">Décembre 2024 - Version 1.0 Production Ready</p>
        </div>
    </div>
    
    {html_content}
    
    <div class="page-break"></div>
    <div class="footer-section">
        <div class="logo-container">
            <div class="logo">
                <img src="static/images/ulc-icam-logo.png" alt="ULC-ICAM Logo">
            </div>
        </div>
        <h2 style="color: white; border: none; margin: 20px 0;">Merci pour votre Attention</h2>
        <h3 style="color: white; border: none;">Jonathan Kakesa Nayaba</h3>
        <p class="developer-title">Développeur Principal</p>
        <p class="contact-info">📧 jkakesa9@gmail.com | 📱 +1 (438)-529-9073</p>
        <p style="margin-top: 30px; font-size: 16pt; font-weight: 600;">Questions & Démonstration Live</p>
    </div>
</body>
</html>
    """
    
    html_file = Path("ULC_ICAM_Presentation_Professional.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return html_file

def convert_markdown_to_html(md_content):
    """Convertit le Markdown en HTML avec mise en forme avancée"""
    import re
    
    html = md_content
    
    # Titres avec ancres
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Formatage
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Blocs de code avec langage
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Citations
    html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Tableaux basiques
    lines = html.split('\n')
    result_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        if '|' in line and not in_table:
            # Début de tableau
            headers = [cell.strip() for cell in line.split('|')[1:-1]]
            result_lines.append('<table>')
            result_lines.append('<thead><tr>')
            for header in headers:
                result_lines.append(f'<th>{header}</th>')
            result_lines.append('</tr></thead><tbody>')
            in_table = True
        elif '|' in line and in_table and not line.strip().startswith('|---'):
            # Ligne de données
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            result_lines.append('<tr>')
            for cell in cells:
                result_lines.append(f'<td>{cell}</td>')
            result_lines.append('</tr>')
        elif in_table and '|' not in line:
            # Fin de tableau
            result_lines.append('</tbody></table>')
            result_lines.append(line)
            in_table = False
        elif not (in_table and line.strip().startswith('|---')):
            result_lines.append(line)
    
    if in_table:
        result_lines.append('</tbody></table>')
    
    # Listes
    html = '\n'.join(result_lines)
    lines = html.split('\n')
    result_lines = []
    in_list = False
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'<li>{line.strip()[2:]}</li>')
        elif line.strip().startswith('1. ') or re.match(r'^\d+\. ', line.strip()):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
            content = re.sub(r'^\d+\. ', '', line.strip())
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                result_lines.append('</ul>' if '- ' in str(result_lines[-2:]) else '</ol>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    # Paragraphes
    html = '\n'.join(result_lines)
    paragraphs = re.split(r'\n\s*\n', html)
    html_paragraphs = []
    
    for p in paragraphs:
        p = p.strip()
        if p and not re.match(r'^<[^>]+>', p):
            html_paragraphs.append(f'<p>{p}</p>')
        else:
            html_paragraphs.append(p)
    
    return '\n\n'.join(html_paragraphs)

def main():
    print("🎓 Générateur PDF Professionnel - ULC-ICAM Turnin System")
    print("=" * 60)
    
    print("📄 Création du fichier HTML professionnel...")
    html_file = create_professional_html()
    
    if not html_file:
        return False
    
    print(f"✅ Fichier HTML créé: {html_file}")
    
    print("\n🌐 Ouverture dans le navigateur...")
    file_url = f"file:///{html_file.absolute()}"
    webbrowser.open(file_url)
    
    print("\n📋 INSTRUCTIONS POUR GÉNÉRER LE PDF:")
    print("=" * 50)
    print("1. ✅ Le fichier s'ouvre dans votre navigateur")
    print("2. 🖨️  Appuyez sur Ctrl+P (ou Cmd+P sur Mac)")
    print("3. 📄 Sélectionnez 'Enregistrer au format PDF'")
    print("4. ⚙️  Configurez les options:")
    print("   - Format: A4")
    print("   - Marges: Normales")
    print("   - Inclure les arrière-plans: OUI")
    print("   - Échelle: 100%")
    print("5. 💾 Enregistrez sous: 'ULC-ICAM_Turnin_System_Presentation.pdf'")
    print("\n🎉 Votre présentation PDF professionnelle sera prête!")
    
    return True

if __name__ == "__main__":
    main()