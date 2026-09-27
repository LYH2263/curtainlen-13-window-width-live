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
@router.put("/windows/{wid}")
def update_window(wid: int, body: WindowUpdate):
    # 窗宽非正一律拒绝（NaN 也一并挡下）
    if not (body.width > 0):
        raise HTTPException(422, "窗宽必须为正数")
    r = repo.update_width(wid, body.width)
    if not r: raise HTTPException(404)
    return r
