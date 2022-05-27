from fastapi import FastAPI, Depends
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from startup import cert_metric_store, ca_file_path #user_store
from routers import authentication, metric_storage, client_registration
 
config = Config()
config.certfile = f"{ca_file_path}/ca.crt"
config.keyfile = f"{ca_file_path}/private/ca_key.pem"
config.bind = ["0.0.0.0:443"]

agg = FastAPI(dependencies=[Depends(cert_metric_store)])#, Depends(user_store)])
# agg.include_router(authentication.auth)
agg.include_router(client_registration.regis)
agg.include_router(metric_storage.metric)
@agg.on_event("startup")
async def startup():
    await cert_metric_store()
    # await user_store()

if __name__ == "__main__":
    asyncio.run(serve(agg, config), debug=True)
    # asyncio.run(serve(reg, config2))