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
    c = connect()
    try:
        cur = c.execute("UPDATE windows SET width=? WHERE id=?", (float(width), wid))
        c.commit()
        if cur.rowcount == 0:
            return None
    finally:
        c.close()
    # 与列表/测算走同一个读口径，直接回读落库行
    return get_window(wid)
