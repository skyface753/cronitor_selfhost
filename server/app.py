from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from server.prisma.prisma import prisma
# from pymongo import MongoClient
from server.jobs import Jobs as JobsClass
newJobs = JobsClass()



import server.config.config as config
    
    
docs_url = "/api/v1/docs" if config.SHOW_DOCS else None
redoc_url = "/api/v1/redocs" if config.SHOW_DOCS else None
openapi_url = "/api/v1/openapi.json" if config.SHOW_DOCS else None
app = FastAPI(
    title="Cronitor Selfhost API",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

origins = [
    config.CLIENT_URL,
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup_db_client():
    await prisma.connect()
    print("Connected to the Prisma database!")
    if config.DEV:
        print("Loaded jobs from file to DB")
        print("Creating dummy data")
        await newJobs.create_dummy_data()
    else:
        await newJobs.load_jobs_from_file_to_db() 
        

@app.on_event("shutdown")
async def shutdown_db_client():
    # app.mongodb_client.close()
    await prisma.disconnect()
    
apiPrefix = "/api/v1"

from server.routes.jobs import jobsRouter
app.include_router(jobsRouter, prefix="/api/v1/jobs")

def run():
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    uvicorn.run("server.app:app", host="127.0.0.1" if config.DEV else "0.0.0.0", port=8000, reload=True)
    
