from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.app.api import sessions, workstations
from shared.constants import API_PREFIX

app = FastAPI(title="IDB Bali PC Rental API", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix=API_PREFIX, tags=["sessions"])
app.include_router(workstations.router, prefix=API_PREFIX, tags=["workstations"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
