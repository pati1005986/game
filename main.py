import os
import sys

# Añadir el directorio del juego al path
game_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(game_dir)

# Importar el juego
from Index.World.level_1 import main

if __name__ == "__main__":
    main()