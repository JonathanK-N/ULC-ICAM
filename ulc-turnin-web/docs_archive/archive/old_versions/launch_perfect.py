#!/usr/bin/env python3
"""
Lanceur pour ULC-ICAM Turnin Perfect
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("ULC-ICAM TURNIN WEB - VERSION PARFAITE")
    print("=" * 60)
    print("100% conforme a Turnin Web UdeS")
    print("+ Fonctionnalites IA avancees")
    print("Securite renforcee")
    print("Interface optimisee")
    print("")
    print("URL: http://localhost:5000")
    print("Admin: admin / admin123")
    print("Prof: prof001 / prof123")
    print("Etudiant: etu001 / etu123")
    print("=" * 60)
    
    # Lancer l'application
    try:
        subprocess.run([sys.executable, "ulc_turnin_perfect.py"])
    except KeyboardInterrupt:
        print("\nApplication arretee")

if __name__ == "__main__":
    main()