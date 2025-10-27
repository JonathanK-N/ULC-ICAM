#!/usr/bin/env python3
"""
Générateur de PDF pour la présentation ULC-ICAM Turnin System
Auteur: Jonathan Kakesa Nayaba
Date: Décembre 2024
"""

import os
import sys
from pathlib import Path

def install_requirements():
    """Installe les dépendances nécessaires pour la génération PDF"""
    try:
        import markdown
        import pdfkit
        import weasyprint
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("\n📦 Installation des dépendances...")
        
        # Installation via pip
        packages = [
            "markdown",
            "pdfkit", 
            "weasyprint",
            "markdown-extensions"
        ]
        
        for package in packages:
            os.system(f"pip install {package}")
        
        print("✅ Installation terminée")
        return True

def markdown_to_html(md_file, html_file):
    """Convertit le fichier Markdown en HTML avec style"""
    try:
        import markdown
        
        # Lire le fichier Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Configuration Markdown avec extensions
        md = markdown.Markdown(extensions=[
            'toc',
            'tables', 
            'fenced_code',
            'codehilite',
            'attr_list'
        ])
        
        # Convertir en HTML
        html_content = md.convert(md_content)
        
        # Template HTML avec styles
        html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULC-ICAM Turnin System - Présentation</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @top-center {{
                content: "ULC-ICAM Turnin System - Présentation";
                font-size: 10pt;
                color: #666;
            }}
            @bottom-center {{
                content: "Page " counter(page) " sur " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #4facfe;
            border-bottom: 3px solid #4facfe;
            padding-bottom: 10px;
            page-break-before: always;
        }}
        
        h1:first-child {{
            page-break-before: auto;
        }}
        
        h2 {{
            color: #667eea;
            border-left: 4px solid #667eea;
            padding-left: 15px;
            margin-top: 30px;
        }}
        
        h3 {{
            color: #f093fb;
            margin-top: 25px;
        }}
        
        h4 {{
            color: #43e97b;
            margin-top: 20px;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            font-size: 0.85em;
        }}
        
        blockquote {{
            border-left: 4px solid #4facfe;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #4facfe;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 20px;
            margin: 30px 0;
        }}
        
        .toc h2 {{
            margin-top: 0;
            color: #4facfe;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .success {{
            background-color: #d4edda;
            border: 1px solid #28a745;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .info {{
            background-color: #d1ecf1;
            border: 1px solid #17a2b8;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        .no-break {{
            page-break-inside: avoid;
        }}
        
        .center {{
            text-align: center;
        }}
        
        .logo {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
            margin: 0 10px;
        }}
        
        .header-section {{
            text-align: center;
            margin: 40px 0;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        @media print {{
            body {{
                font-size: 11pt;
            }}
            
            h1 {{
                font-size: 18pt;
            }}
            
            h2 {{
                font-size: 16pt;
            }}
            
            h3 {{
                font-size: 14pt;
            }}
            
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="header-section">
        <div class="logo">ULC</div>
        <h1 style="margin: 20px 0; border: none; color: white;">ULC-ICAM TURNIN SYSTEM</h1>
        <h2 style="margin: 10px 0; border: none; color: white; font-size: 1.2em;">Système de Gestion de Devoirs et Soumissions de Code</h2>
        <p style="font-size: 1.1em; margin: 20px 0;">Université Loyola du Congo - Institut Catholique d'Arts et Métiers</p>
        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin-top: 20px;">
            <h3 style="margin: 0; color: white; border: none;">ULC-ICAM Turnin System</h3>
            <p style="margin: 5px 0;">Ingénieur Logiciel & Développeur Full-Stack</p>
            <p style="margin: 5px 0;">Décembre 2024 - Version 1.0 Production Ready</p>
        </div>
    </div>
    
    {html_content}
    
    <div class="page-break"></div>
    <div class="header-section">
        <h2 style="margin-top: 0; color: white; border: none;">Merci pour votre Attention</h2>
        <h3 style="color: white; border: none;">Jonathan Kakesa Nayaba</h3>
        <p><strong>Développeur Principal</strong></p>
        <p>📧 jkakesa9@gmail.com | 📱 +243 438 529 907</p>
        <p style="margin-top: 20px; font-size: 1.1em;"><strong>Questions & Démonstration Live</strong></p>
    </div>
</body>
</html>
        """
        
        # Sauvegarder le HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ HTML généré: {html_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la conversion MD->HTML: {e}")
        return False

def html_to_pdf_weasyprint(html_file, pdf_file):
    """Convertit HTML en PDF avec WeasyPrint"""
    try:
        from weasyprint import HTML, CSS
        
        # CSS supplémentaire pour l'impression
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
            
            h1 {
                page-break-before: always;
            }
            
            h1:first-child {
                page-break-before: auto;
            }
            
            .page-break {
                page-break-before: always;
            }
            
            .no-break {
                page-break-inside: avoid;
            }
        ''')
        
        # Générer le PDF
        HTML(filename=html_file).write_pdf(pdf_file, stylesheets=[css])
        print(f"✅ PDF généré avec WeasyPrint: {pdf_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur WeasyPrint: {e}")
        return False

def html_to_pdf_pdfkit(html_file, pdf_file):
    """Convertit HTML en PDF avec pdfkit (wkhtmltopdf)"""
    try:
        import pdfkit
        
        options = {
            'page-size': 'A4',
            'margin-top': '2cm',
            'margin-right': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdfkit.from_file(html_file, pdf_file, options=options)
        print(f"✅ PDF généré avec pdfkit: {pdf_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur pdfkit: {e}")
        print("💡 Astuce: Installez wkhtmltopdf depuis https://wkhtmltopdf.org/downloads.html")
        return False

def main():
    """Fonction principale"""
    print("🎓 Générateur PDF - ULC-ICAM Turnin System")
    print("=" * 50)
    
    # Chemins des fichiers
    base_dir = Path(__file__).parent
    md_file = base_dir / "presentation_detaillee.md"
    html_file = base_dir / "presentation_detaillee.html"
    pdf_file = base_dir / "ULC-ICAM_Turnin_System_Presentation.pdf"
    
    # Vérifier que le fichier Markdown existe
    if not md_file.exists():
        print(f"❌ Fichier Markdown non trouvé: {md_file}")
        return False
    
    # Installer les dépendances
    if not install_requirements():
        return False
    
    # Convertir MD -> HTML
    print("\n📄 Conversion Markdown -> HTML...")
    if not markdown_to_html(md_file, html_file):
        return False
    
    # Convertir HTML -> PDF
    print("\n📑 Conversion HTML -> PDF...")
    
    # Essayer WeasyPrint en premier
    if html_to_pdf_weasyprint(html_file, pdf_file):
        success = True
    # Fallback vers pdfkit
    elif html_to_pdf_pdfkit(html_file, pdf_file):
        success = True
    else:
        print("❌ Impossible de générer le PDF avec les outils disponibles")
        success = False
    
    if success:
        print(f"\n🎉 Présentation PDF générée avec succès!")
        print(f"📁 Fichier: {pdf_file}")
        print(f"📊 Taille: {pdf_file.stat().st_size / 1024:.1f} KB")
        
        # Ouvrir le PDF automatiquement
        try:
            os.startfile(str(pdf_file))  # Windows
        except:
            try:
                os.system(f"open '{pdf_file}'")  # macOS
            except:
                os.system(f"xdg-open '{pdf_file}'")  # Linux
    
    # Nettoyer le fichier HTML temporaire
    if html_file.exists():
        html_file.unlink()
        print("🧹 Fichier HTML temporaire supprimé")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
