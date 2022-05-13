from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import JSONResponse, FileResponse
import os, sqlite3, json, shutil, datetime
from datetime import datetime
import dependencies

curr_token = ()
regis = APIRouter(
    dependencies=[Depends(dependencies.cert_metric_store)],
    prefix="/api/registration",
    tags = ["Client Registration"]
    )

@regis.put("/generate_registration_token")
async def generate_regst_token():
    token = await dependencies.generate_client_token()
    curr_token = token
    return {
        "Token": token[0],
        "Expiration": token[1]
    }

async def issue_client_cert(filename):
    f = open(f"{dependencies.client_metric_store}/{filename}")
    jfile = json.load(f)
    f.close()
    clients_con = sqlite3.connect(f"{dependencies.data_store}/clients.db")
    cur = clients_con.cursor()
    registered_clients = cur.execute(f'''SELECT * FROM registered_clients WHERE hostname=?''', (jfile["system_name"],)).fetchone()
    if registered_clients == None:
        cur.execute(f'''INSERT INTO registered_clients VALUES (?, ?)''', (jfile["system_name"], datetime.now()))
    else:
        cur.execute(f'''UPDATE registered_clients SET date_registered=? WHERE hostname=?''', (datetime.now(), jfile["system_name"]))
    clients_con.commit()
    clients_con.close()
    cert_path = f"{dependencies.ca_file_path}/certs/{jfile['system_name']}"
    zfilename = f"{jfile['system_name']}"
    if not os.path.exists(cert_path):
        ca = dependencies.CertificateAuthority(ca_storage = dependencies.ca_file_path, common_name=dependencies.ca_name)
        ca.issue_certificate(hostname=jfile["system_name"])
        with open(f'{cert_path}/bundle.crt', 'wb') as bundle:
            ca_cert = open(f'{dependencies.ca_file_path}/ca.crt', 'rb')
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
    if not await dependencies.validate_token(token):
        return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content = {'message': "Token Not Authorized"}
        )
    else:
        contents = await metric_file.read()
        with open(f"{dependencies.client_metric_store}/{metric_file.filename}", "wb") as f:
            f.write(contents)
            f.close()
        await metric_file.close()
        host_cert = await issue_client_cert(metric_file.filename)
        return FileResponse(host_cert[0], status_code=201, filename=host_cert[1])
