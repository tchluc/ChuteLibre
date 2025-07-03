"""Point d'entrée principal pour la simulation moderne"""

import sys
import os
import asyncio
import platform

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Menu principal pour choisir le type de simulation"""
    print(" Simulation de Chute Libre - Menu Principal")
    print("=" * 50)
    print("1. Simulation avec  pygame")
    print("0. Quitter")

    choice = input("\nChoisissez une option (0-4): ").strip()

    try:
        if choice == "1":
            from examples.modern_simulation import main as modern_main
            if platform.system() == "Emscripten":
                asyncio.ensure_future(modern_main())
            else:
                asyncio.run(modern_main())

        else:
            print("❌ Option invalide")
            main()

    except KeyboardInterrupt:
        print("\n👋 Simulation interrompue par l'utilisateur")
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()