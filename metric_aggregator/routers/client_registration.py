from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import JSONResponse, FileResponse
import os, json, shutil, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from startup import cert_metric_store, Base, client_metric_store, data_store, ca_file_path, ca_name, CertificateAuthority, registered_client
from dependencies import generate_client_token, validate_token

curr_token = ()
regis = APIRouter(
    dependencies=[Depends(cert_metric_store)],
    prefix="/api/registration",
    tags = ["Client Registration"]
    )

@regis.put("/generate_registration_token")
async def generate_regst_token():
    token = await generate_client_token()
    curr_token = token
    return {
        "Token": token[0],
        "Expiration": token[1]
    }

async def issue_client_cert(filename):
    f = open(f"{client_metric_store}/{filename}")
    jfile = json.load(f)
    f.close()
    metric_engine = create_engine(f"{data_store}")
    Base.metadata.bind = metric_engine
    DBsession = sessionmaker()
    DBsession.bind = metric_engine
    session = DBsession()
    registered = session.query(registered_client).filter_by(system_name=f"{jfile['system_name']}").first()
    if registered is None:
        client = registered_client()
        client.system_name = jfile["system_name"]
        client.date_registered = datetime.now()
        session.add(client)
        session.commit()
    else:
        registered.date_registered = datetime.now()
        session.commit()
    session.close()
    cert_path = f"{ca_file_path}/certs/{jfile['system_name']}"
    zfilename = f"{jfile['system_name']}"
    if not os.path.exists(cert_path):
        ca = CertificateAuthority(ca_storage = ca_file_path, common_name=ca_name)
        ca.issue_certificate(hostname=jfile["system_name"])
        with open(f'{cert_path}/bundle.crt', 'wb') as bundle:
            ca_cert = open(f'{ca_file_path}/ca.crt', 'rb')
            client_cert = open(f"{cert_path}/{jfile['system_name']}.crt", "rb")
            data = ca_cert.read()
            data2 = client_cert.read()
            bundle.write(data2)
            bundle.write(data)
            ca_cert.close()
            client_cert.close()
            bundle.close()
        shutil.make_archive(f'{cert_path}/{zfilename}', 'tar', cert_path)
    return [f'{cert_path}/{zfilename}.tar', f'{zfilename}.tar']


@regis.post("/register_client")
async def register_client(token: str, metric_file: UploadFile):
    if not await validate_token(token):
        return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content = {'message': "Token Not Authorized"}
        )
    else:
        contents = await metric_file.read()
        with open(f"{client_metric_store}/{metric_file.filename}", "wb") as f:
            f.write(contents)
            f.close()
        await metric_file.close()
        host_cert = await issue_client_cert(metric_file.filename)
        return FileResponse(host_cert[0], status_code=201, filename=host_cert[1])
