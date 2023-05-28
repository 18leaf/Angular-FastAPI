from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
   
class Login(BaseModel):
    username: str
    password: str

@app.get("/api/get")
async def get_test():
    return "get"
    

@app.post("/api/post")
async def post_test(request: Login):
    print('running code...')
    username = request.username
    password = request.password
    unique_id = 18
    return JSONResponse(content={"info": f"{username}", "id": unique_id})


