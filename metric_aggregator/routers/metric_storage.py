from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import JSONResponse, FileResponse
import os, sqlite3, json, shutil
import dependencies

metric = APIRouter(
    dependencies=[Depends(dependencies.cert_metric_store)],
    prefix="/api/metrics",
    tags = ["metrics"]
)

@metric.post("/metric_upload")
async def offload_metric_files(metric_file: UploadFile):
    contents = await metric_file.read()
    with open(f"{dependencies.client_metric_store}/{metric_file.filename}", "wb") as f:
        f.write(contents)
        f.close()
    await metric_file.close()
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message":"offload accepted"}
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