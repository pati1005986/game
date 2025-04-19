import os
import sys

# Obtener el directorio absoluto del script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Añadir el directorio base al path de Python
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from Index.World.level_1 import main
    main()
except ImportError as e:
    print(f"Error importando el módulo: {e}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    input("Presiona Enter para salir...")