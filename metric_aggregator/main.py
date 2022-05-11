from fastapi import FastAPI, status, File, UploadFile, HTTPException, Depends
from fastapi.responses import Response, FileResponse, JSONResponse
import sqlite3, time, os, hypercorn, ownca, platform, datetime, asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from datetime import datetime
from typing import Optional
from ownca import CertificateAuthority
from dependencies import cert_metric_store, user_store, ca_file_path
from routers import authentication, metric_storage, client_registration
 
config = Config()
config.certfile = f"{ca_file_path}/ca.crt"
config.keyfile = f"{ca_file_path}/private/ca_key.pem"
config.bind = ["192.168.1.23:443"]

agg = FastAPI(dependencies=[Depends(cert_metric_store), Depends(user_store)])
agg.include_router(authentication.auth)
agg.include_router(client_registration.regis)
@agg.on_event("startup")
async def startup():
    await cert_metric_store()
    await user_store()

if __name__ == "__main__":
    asyncio.run(serve(agg, config), debug=True)
    # asyncio.run(serve(reg, config2))