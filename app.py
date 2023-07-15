from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import user
from routes.personalDocument import document
from routes.carInformation import carInfo
from routes.process import process
from routes.profile import profileRouter
from routes.bank import bankRouter
from routes.systemConfig import system
from routes.loans import loanRouter

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user)
app.include_router(document)
app.include_router(carInfo)
app.include_router(process)
app.include_router(profileRouter)
app.include_router(bankRouter)
app.include_router(system)
app.include_router(loanRouter)
