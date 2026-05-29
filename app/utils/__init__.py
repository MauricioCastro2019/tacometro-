import json
from datetime import datetime, timezone, timedelta


def esta_abierto(horario_json):
    """Checks if a place is currently open.
    Accepts raw JSON string or parsed dict. Returns True/False/None (None = no data).
    """
    if not horario_json:
        return None
    try:
        horario = json.loads(horario_json) if isinstance(horario_json, str) else horario_json
    except (ValueError, TypeError):
        return None

    # León, Guanajuato observes CDT (UTC-5) roughly April–October, CST (UTC-6) rest
    now_utc = datetime.now(timezone.utc)
    offset = -5 if 4 <= now_utc.month <= 10 else -6
    now = now_utc.astimezone(timezone(timedelta(hours=offset)))

    day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    day_info = horario.get(day_names[now.weekday()])
    if not day_info:
        return False

    try:
        ah, am = map(int, day_info['abre'].split(':'))
        ch, cm = map(int, day_info['cierra'].split(':'))
        now_m = now.hour * 60 + now.minute
        abre_m = ah * 60 + am
        cierra_m = ch * 60 + cm
        if cierra_m <= abre_m:  # overnight: e.g. 18:00–02:00
            return now_m >= abre_m or now_m <= cierra_m
        return abre_m <= now_m <= cierra_m
    except (ValueError, KeyError, AttributeError):
        return None
