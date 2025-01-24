from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import engine, Base
from routers import user, recommend, videos

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user.router)
app.include_router(recommend.router)
app.include_router(videos.router)

# Serve static files
app.mount(
    "/static",
    StaticFiles(directory="C:/Users/Admin/.vscode/test/project_root_compressed/fastapi/static/build"),
    name="static",
)

# Serve Svelte index.html
@app.get("/")
async def serve_index():
    return FileResponse("C:/Users/Admin/.vscode/test/project_root_compressed/fastapi/static/build/index.html")
