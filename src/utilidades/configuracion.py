import json
import os


def cargar_config():
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)