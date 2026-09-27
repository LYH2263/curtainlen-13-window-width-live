import math
from app.db import connect

def list_windows():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM windows ORDER BY id").fetchall()]
    finally:
        c.close()

def get_window(wid: int):
    c = connect()
    try:
        r = c.execute("SELECT * FROM windows WHERE id=?", (wid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_width(wid: int, width: float):
    if isinstance(width, bool) or not isinstance(width, (int, float)) \
            or not math.isfinite(width) or width <= 0:
        raise ValueError("width must be a positive finite number")
    c = connect()
    try:
        cur = c.execute("UPDATE windows SET width=? WHERE id=?", (float(width), wid))
        c.commit()
        if cur.rowcount == 0:
            return None
        r = c.execute("SELECT * FROM windows WHERE id=?", (wid,)).fetchone()
        return dict(r)
    finally:
        c.close()
