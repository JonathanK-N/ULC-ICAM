#!/usr/bin/env python3
"""
Générateur PDF Simple pour ULC-ICAM Turnin System
Utilise le navigateur pour générer le PDF
"""

import os
import webbrowser
import time
from pathlib import Path

def create_print_ready_html():
    """Crée une version HTML optimisée pour l'impression"""
    
    # Lire le contenu Markdown
    md_file = Path("presentation_detaillee.md")
    if not md_file.exists():
        print("❌ Fichier presentation_detaillee.md non trouvé")
        return None
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convertir le Markdown basique en HTML
    html_content = convert_markdown_to_html(content)
    
    # Template HTML pour impression
    html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>ULC-ICAM Turnin System - Présentation</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 12pt;
        }}
        
        .cover-page {{
            text-align: center;
            padding: 50px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
            page-break-after: always;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            background: #4facfe;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 24px;
            margin: 20px;
        }}
        
        h1 {{
            color: #4facfe;
            border-bottom: 2px solid #4facfe;
            padding-bottom: 10px;
            page-break-before: always;
            font-size: 18pt;
        }}
        
        h1:first-of-type {{
            page-break-before: auto;
        }}
        
        h2 {{
            color: #667eea;
            border-left: 4px solid #667eea;
            padding-left: 15px;
            font-size: 16pt;
        }}
        
        h3 {{
            color: #f093fb;
            font-size: 14pt;
        }}
        
        h4 {{
            color: #43e97b;
            font-size: 12pt;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            font-size: 10pt;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10pt;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #4facfe;
            color: white;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        ul, ol {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        blockquote {{
            border-left: 4px solid #4facfe;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        .footer {{
            position: fixed;
            bottom: 1cm;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 10pt;
            color: #666;
        }}
        
        @media print {{
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="logo">ULC</div>
        <h1 style="color: white; border: none; margin: 20px 0;">ULC-ICAM TURNIN SYSTEM</h1>
        <h2 style="color: white; border: none; font-size: 16pt;">Système de Gestion de Devoirs et Soumissions de Code</h2>
        <p style="font-size: 14pt;">Université Loyola du Congo - Institut Catholique d'Arts et Métiers</p>
        <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; margin: 30px auto; max-width: 500px;">
            <h3 style="margin: 0; color: white; border: none;">ULC-ICAM Turnin System</h3>
            <h2 style="color: white; border: none; margin: 10px 0;">Jonathan Kakesa Nayaba</h2>
            <p>Ingénieur Logiciel & Développeur Full-Stack</p>
            <p>📧 jkakesa9@gmail.com | 📱 +243 438 529 907</p>
            <p style="margin-top: 15px;"><strong>Décembre 2024 - Version 1.0 Production Ready</strong></p>
        </div>
    </div>
    
    {html_content}
    
    <div class="page-break"></div>
    <div class="cover-page">
        <h2 style="color: white; border: none;">Merci pour votre Attention</h2>
        <h3 style="color: white; border: none;">Jonathan Kakesa Nayaba</h3>
        <p><strong>Développeur Principal</strong></p>
        <p>📧 jkakesa9@gmail.com | 📱 +243 438 529 907</p>
        <p style="margin-top: 20px; font-size: 16pt;"><strong>Questions & Démonstration Live</strong></p>
    </div>
    
    <div class="footer no-print">
        ULC-ICAM Turnin System - Présentation par Jonathan Kakesa Nayaba
    </div>
</body>
</html>
    """
    
    # Sauvegarder le fichier HTML
    html_file = Path("ULC_ICAM_Presentation_Print.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return html_file

def convert_markdown_to_html(md_content):
    """Convertit le Markdown en HTML basique"""
    html = md_content
    
    # Titres
    html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1) if '# ' in html else html
    html = html.replace('## ', '<h2>').replace('\n', '</h2>\n') if '## ' in html else html
    html = html.replace('### ', '<h3>').replace('\n', '</h3>\n') if '### ' in html else html
    html = html.replace('#### ', '<h4>').replace('\n', '</h4>\n') if '#### ' in html else html
    
    # Gras et italique
    import re
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Code inline
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Blocs de code
    html = re.sub(r'```(.*?)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Listes
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    # Paragraphes
    html = '\n'.join(result_lines)
    paragraphs = html.split('\n\n')
    html_paragraphs = []
    
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            html_paragraphs.append(f'<p>{p}</p>')
        else:
            html_paragraphs.append(p)
    
    return '\n\n'.join(html_paragraphs)

def main():
    print("🎓 Générateur PDF Simple - ULC-ICAM Turnin System")
    print("=" * 55)
    
    # Créer le fichier HTML pour impression
    print("📄 Création du fichier HTML pour impression...")
    html_file = create_print_ready_html()
    
    if not html_file:
        return False
    
    print(f"✅ Fichier HTML créé: {html_file}")
    
    # Ouvrir dans le navigateur
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
    print("   - Inclure les arrière-plans")
    print("5. 💾 Enregistrez sous: 'ULC-ICAM_Turnin_System_Presentation.pdf'")
    print("\n🎉 Votre présentation PDF sera prête!")
    
    # Attendre un peu puis nettoyer
    print(f"\n⏳ Fichier HTML disponible: {html_file}")
    print("💡 Vous pouvez supprimer le fichier HTML après avoir généré le PDF")
    
    return True

if __name__ == "__main__":
    main()
