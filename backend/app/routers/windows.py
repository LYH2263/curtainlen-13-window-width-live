from fastapi import APIRouter, HTTPException
from app.repositories import windows as repo
from app.schemas.window import WindowUpdate
router = APIRouter()
@router.get("/windows")
def list_windows(): return {"items": repo.list_windows()}
@router.get("/windows/{wid}")
def get_window(wid: int):
    r = repo.get_window(wid)
    if not r: raise HTTPException(404)
    return r
@router.patch("/windows/{wid}")
def update_window(wid: int, body: WindowUpdate):
    try:
        r = repo.update_width(wid, body.width)
    except ValueError as e:
        raise HTTPException(422, str(e))
    if r is None:
        raise HTTPException(404, "window not found")
    return r
