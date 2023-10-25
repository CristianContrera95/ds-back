from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.auth_schema import Account, Token, TokenData
from settings import config as cfg


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


def get_account(username: str):
    for user in cfg.USERS:
        if username == user["username"]:
            return Account(username=user["username"])
    return False


def authenticate_account(email: str, password: str):
    for user in cfg.USERS:
        if email == user["username"] and password == user["password"]:
            return Account(username=user["username"])
    else:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1.)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, cfg.SECRET_KEY,
                             algorithm=cfg.ALGORITHM)
    return encoded_jwt


async def get_current_account(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    account = get_account(username=token_data.username)
    if account is None:
        raise credentials_exception
    return account


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''OAuth2PasswordRequestForm requires username field, this represent email field in front panel'''
    account = authenticate_account(form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/actual_token")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.get("/actual_account")
async def read_accounts_me(current_account = Depends(get_current_account)):
    return current_account
