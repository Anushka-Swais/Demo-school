import os
from dotenv import load_dotenv

# 1. THIS MUST BE AT THE VERY TOP! Load the .env file first.
load_dotenv()

# 2. NOW import FastAPI and your routes, so they can use the keys.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.admin_route import router as admin_router

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

# Register Admin Routes
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin Dashboard"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7008))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)