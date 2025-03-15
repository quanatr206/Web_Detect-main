from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import json

from ..database import get_db, SessionLocal
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, Token
from ..utils.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
)
from ..services.system_info import SystemInfoService
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký người dùng mới và thu thập thông tin hệ thống
    """
    # Kiểm tra người dùng đã tồn tại
    existing_user = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên người dùng hoặc email đã tồn tại",
        )

    # Thu thập thông tin hệ thống
    system_info = SystemInfoService.get_system_info()

    # Mã hóa mật khẩu
    hashed_password = get_password_hash(user_data.password)

    # Tạo người dùng mới
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        system_info=json.dumps(system_info),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Đăng nhập và lấy token truy cập
    """
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Tạo token truy cập
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng hiện tại
    """
    return current_user


@router.get("/system-info")
def get_system_info(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Lấy thông tin hệ thống của người dùng hiện tại
    """
    if not current_user.system_info:
        # Nếu chưa có thông tin hệ thống, thu thập mới
        system_info = SystemInfoService.get_system_info()
        current_user.system_info = json.dumps(system_info)
        db.commit()
        return system_info

    # Nếu đã có thông tin, chuyển đổi từ JSON sang dict
    return json.loads(current_user.system_info)


@router.put("/update-system-info")
def update_system_info(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin hệ thống của người dùng hiện tại
    """
    system_info = SystemInfoService.get_system_info()
    current_user.system_info = json.dumps(system_info)
    db.commit()

    return system_info
