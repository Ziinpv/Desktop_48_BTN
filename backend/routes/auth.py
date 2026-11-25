from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.entities import User
from backend.routes.schemas import LoginIn, PasswordIn, UserIn, user_out
from backend.services.audit import write_audit
from backend.services.auth_service import authenticate, create_access_token, get_current_user, require_admin
from backend.utils.security import hash_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = authenticate(db, payload.username.strip(), payload.password)
    if not user:
        raise HTTPException(401, "Sai tài khoản hoặc mật khẩu")
    token = create_access_token(user.username, user.role)
    write_audit(db, user.username, "LOGIN", "User", user.username, "Đăng nhập hệ thống")
    return {"token": token, "user": user_out(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)


@router.get("/users")
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [user_out(u) for u in db.query(User).order_by(User.id.asc()).all()]


@router.post("/users")
def create_user(payload: UserIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, "Tên đăng nhập đã tồn tại")
    if payload.role not in ("admin", "staff"):
        raise HTTPException(400, "Vai trò không hợp lệ")
    user = User(
        username=payload.username.strip(),
        full_name=payload.fullName,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=payload.isActive,
    )
    db.add(user)
    db.commit()
    write_audit(db, admin.username, "CREATE", "User", user.username, f"Tạo tài khoản {payload.role}")
    return user_out(user)


@router.patch("/users/{user_id}")
def update_user(user_id: int, payload: dict, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Không tìm thấy người dùng")
    if "fullName" in payload:
        user.full_name = payload["fullName"]
    if "role" in payload and payload["role"] in ("admin", "staff"):
        user.role = payload["role"]
    if "isActive" in payload:
        user.is_active = bool(payload["isActive"])
    if payload.get("password"):
        user.password_hash = hash_password(payload["password"])
    db.commit()
    write_audit(db, admin.username, "UPDATE", "User", user.username, "Cập nhật tài khoản")
    return user_out(user)


@router.post("/change-password")
def change_password(payload: PasswordIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.password_hash = hash_password(payload.password)
    db.commit()
    write_audit(db, user.username, "UPDATE", "User", user.username, "Đổi mật khẩu")
    return {"ok": True}
