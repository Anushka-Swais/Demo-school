import os
from dotenv import load_dotenv

# 1. THIS MUST BE AT THE VERY TOP! Load the .env file first.
load_dotenv()

# 2. NOW import FastAPI, your routes, and your Database Config.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db_config import engine, Base  # <-- NEW: Import your DB engine and Base class

# Import Routes
from routes.student_routes import router as student_router
from routes.admin_routes import router as admin_router
from routes.Faculty_routes import router as faculty_router 
from routes.hm_routes import router as hm_router
from routes.Parent_routes import router as parent_router

# 3. Create Database Tables automatically on startup
Base.metadata.create_all(bind=engine)      # <-- NEW: Automatically binds and creates your Postgres tables!

app = FastAPI(
    title="Demo School AI Service",
    description="AI Microservice for Demo School Dashboards",
    version="1.0.0"
)

# Configure CORS for dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(student_router, prefix="/api/v1/student", tags=["Student Dashboard"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin Dashboard"])
app.include_router(faculty_router, prefix="/api/v1/faculty", tags=["Faculty Dashboard"])
app.include_router(hm_router, prefix="/api/v1/hm", tags=["HM Dashboard"])
app.include_router(parent_router, prefix="/api/v1/parent", tags=["Parent Dashboard"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7008))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)