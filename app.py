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
from routes.adminDocuments import adminDocument
from routes.payment import payment

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:5173",
#     "http://localhost:3000",
#     "http://localhost:8000",
# ]
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check():
    # Aquí puedes incluir cualquier lógica adicional para verificar el estado de tu aplicación
    # Por ejemplo, puedes comprobar conexiones a bases de datos, servicios externos, etc.

    # Si todo está bien, devolvemos un mensaje de éxito

    return {"status": "ok"}

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "ok"}

app.include_router(user)
app.include_router(document)
app.include_router(carInfo)
app.include_router(process)
app.include_router(profileRouter)
app.include_router(bankRouter)
app.include_router(system)
app.include_router(loanRouter)
app.include_router(adminDocument)
app.include_router(payment)