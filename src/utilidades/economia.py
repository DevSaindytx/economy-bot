import json
import os
from datetime import datetime, timezone

from utilidades.configuracion import cargar_config


def _ruta_datos():
    directorio = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(directorio, "datos", "economy.json")


def _ruta_registros():
    directorio = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(directorio, "datos", "registros_staff.json")


def cargar_economia():
    ruta = _ruta_datos()
    if not os.path.exists(ruta):
        return {"usuarios": {}, "cooldowns": {}, "estadisticas": {}}
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_economia(datos):
    ruta = _ruta_datos()
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def cargar_registros():
    ruta = _ruta_registros()
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_registros(datos):
    ruta = _ruta_registros()
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def registrar_accion_staff(autor_id, usuario_id, accion, cantidad, detalle):
    registros = cargar_registros()
    registros.append({
        "autor": str(autor_id),
        "usuario": str(usuario_id),
        "accion": accion,
        "cantidad": cantidad,
        "detalle": detalle,
        "fecha": datetime.now(timezone.utc).isoformat(),
    })
    guardar_registros(registros)


def inicializar_usuario(datos, uid, config):
    uid = str(uid)
    if "usuarios" not in datos:
        datos["usuarios"] = {}
    if uid not in datos["usuarios"]:
        datos["usuarios"][uid] = {
            "bolsillo": config["economia"]["dinero_inicial"],
            "banco": 0,
            "cooldowns": {},
            "estadisticas": {
                "ganado": 0,
                "gastado": 0,
                "robos": 0,
                "ruleta": 0,
                "trabajos": 0,
                "diarios": 0,
            },
        }
    return datos["usuarios"][uid]


def _usuario(datos, uid):
    uid = str(uid)
    return datos.get("usuarios", {}).get(uid, {"bolsillo": 0, "banco": 0, "cooldowns": {}, "estadisticas": {"ganado": 0, "gastado": 0, "robos": 0, "ruleta": 0, "trabajos": 0, "diarios": 0}})


def obtener_bolsillo(datos, uid):
    return _usuario(datos, uid).get("bolsillo", 0)


def obtener_banco(datos, uid):
    return _usuario(datos, uid).get("banco", 0)


def establecer_bolsillo(datos, uid, cantidad):
    uid = str(uid)
    usuario = datos.setdefault("usuarios", {}).setdefault(uid, {"bolsillo": 0, "banco": 0, "cooldowns": {}, "estadisticas": {"ganado": 0, "gastado": 0, "robos": 0, "ruleta": 0, "trabajos": 0, "diarios": 0}})
    usuario["bolsillo"] = cantidad


def establecer_banco(datos, uid, cantidad):
    uid = str(uid)
    usuario = datos.setdefault("usuarios", {}).setdefault(uid, {"bolsillo": 0, "banco": 0, "cooldowns": {}, "estadisticas": {"ganado": 0, "gastado": 0, "robos": 0, "ruleta": 0, "trabajos": 0, "diarios": 0}})
    usuario["banco"] = cantidad


def sumar_dinero(datos, uid, cantidad):
    uid = str(uid)
    usuario = datos.setdefault("usuarios", {}).setdefault(uid, {"bolsillo": 0, "banco": 0, "cooldowns": {}, "estadisticas": {"ganado": 0, "gastado": 0, "robos": 0, "ruleta": 0, "trabajos": 0, "diarios": 0}})
    usuario["bolsillo"] = usuario.get("bolsillo", 0) + cantidad
    return usuario["bolsillo"]


def restar_dinero(datos, uid, cantidad):
    uid = str(uid)
    usuario = datos.setdefault("usuarios", {}).setdefault(uid, {"bolsillo": 0, "banco": 0, "cooldowns": {}, "estadisticas": {"ganado": 0, "gastado": 0, "robos": 0, "ruleta": 0, "trabajos": 0, "diarios": 0}})
    actual = usuario.get("bolsillo", 0)
    nuevo = max(0, actual - cantidad)
    usuario["bolsillo"] = nuevo
    return actual - nuevo