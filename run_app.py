import flet as ft
import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

from src.app.main import main

if __name__ == "__main__":
    print("🚀 Starting Flow AI v4.0...")
    ft.run(main)
