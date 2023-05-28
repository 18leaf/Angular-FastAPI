from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware


SECRET_KEY = "e0a3448975b2fd9a84a2a29a0196d638c8a4bc8b462094043e704e4a449c689f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

db = {
    "tim": {
        "username": "tim",
        "full_name": "Tim Ruscica",
        "email": "tim@gmail.com",
        "hashed_password": "$2b$12$eWWDVdbcwK.cEI9.492ZKubgeiOz5Vz8RKGH8vv60Q3WMMJNjf3ja",
        "disabled": False
    }
}

'''
FOR FRONTEND
in request header include 
'Authorization': 'Bearer ' + token
token stored in client cookies, sent each request

'''


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class NewUser(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    password: str


class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None


class UserInDB(User):
    hashed_password: str


pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


def verify_password(plain_password, hashed_password):
    return pwd_content.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_content.hash(password)


def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        # **user_data = extracts key value pairs and passes as function arg
        return UserInDB(**user_data)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could Not Validate Credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(db=db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")

    return current_user


@app.post('/api/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # print(get_password_hash("tim123"))
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect USername/Password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return JSONResponse(content=str(current_user))


@app.get("/api/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]


@app.post("/api/create_user")
async def create_user(user_info: NewUser, response: Response):
    for user in db:
        if user == user_info.username:
            return JSONResponse(content={"info": "already exists"}, status_code=403)

    db[user_info.username] = {
        "username": user_info.username,
        "full_name": user_info.full_name,
        "email": user_info.email,
        "hashed_password": get_password_hash(user_info.password),
        "disabled": False
    }
    access_token = create_access_token(
        data={"sub": user_info.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES))
    response.set_cookie(key="token", value=access_token,
                        samesite="None", secure=True)
    '''
    response.set_cookie(key="loggedIn", value="true")
    response = JSONResponse(content={"info": "user created"})
    return response
    '''
    response.set_cookie(key="isLoggedIn", value="true",
                        samesite="None", secure=True)

    return {"info": access_token}


'''
CREATE TABLE users(
    unique id
    email
    hashed password
    name
)

db.execute("SELECT id FROM users WHERE email = ?", USER INPUT)

'''
