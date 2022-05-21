from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import JSONResponse, FileResponse
import os, sqlite3, json, shutil
from startup import cert_metric_store, client_metric_store
from dependencies import store_metrics

metric = APIRouter(
    dependencies=[Depends(cert_metric_store)],
    prefix="/api/metrics",
    tags = ["metrics"]
)


@metric.post("/metric_upload")
async def offload_metric_files(metric_file: UploadFile):
    contents = await metric_file.read()
    with open(f"{client_metric_store}/{metric_file.filename}", "wb") as f:
        f.write(contents)
        f.close()
    await metric_file.close()
    record = await store_metrics(f"{client_metric_store}/{metric_file.filename}")
    if record == "NR":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'Server Message': f"This device is not registered. Record: {record}"}
        )
    elif record == "ACCEPTED":
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"Server Message": f"Metric Offload Processed Successfully. Record: {record}"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"Server Message": f"Error in subprocess! Record: {record}"}
        )


# async def upload_client_metrics(metric_file: UploadFile = File(...)):
#     contents = await image_file.read()
#     with open(f'{cache_dir}{image_file.filename}', 'wb') as file: #cache the original file
#         file.write(contents)
#         file.close()
#     await image_file.close()
#     ascii_image = await convert_to_ascii(f'{cache_dir}{image_file.filename}') #run the ascii conversion function
#     filename = image_file.filename.replace(".", "_") #standardize the filename
#     with open(f"{cache_dir}{filename}_ascii.txt", "w+") as file: #cache the ascii art
#         file.write(ascii_image)
#         file.close()