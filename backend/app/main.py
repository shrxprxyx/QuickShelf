from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from fastapi.staticfiles import StaticFiles
from app.routers import auth, books



app = FastAPI(title="Smart Library API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    
    return {"status": "ok"}

app.include_router(auth.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(books.categories_router)
