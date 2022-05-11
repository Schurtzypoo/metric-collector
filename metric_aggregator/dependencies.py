import os, platform, ownca, sqlite3, secrets, datetime, json
from datetime import datetime, timedelta
from dateutil import parser
from ownca import CertificateAuthority
ca_name = platform.node()
wkdir = os.path.dirname(os.path.abspath(__file__))
ca_file_path = f"{wkdir}/certificate_store"
data_store = f"{wkdir}/data_store"
client_metric_store = f"{wkdir}/metric_store"

async def cert_metric_store():
    if not os.path.exists(ca_file_path):
        os.mkdir(ca_file_path)
        ca = CertificateAuthority(ca_storage = ca_file_path, common_name=ca_name, dns_names = [ca_name, "192.168.1.23"])
    else:
        ca = CertificateAuthority(ca_storage = ca_file_path, common_name=ca_name, dns_names = [ca_name, "192.168.1.23"])
    if not os.path.exists(data_store):
        os.mkdir(data_store)
    if not os.path.exists(f'{data_store}/clients.db'):
        clients_con = sqlite3.connect(f"{data_store}/clients.db")
        clients_con.close()
    if not os.path.exists(f'{client_metric_store}'):
        os.mkdir(f"{client_metric_store}")

async def user_store():
    if not os.path.exists(f'{data_store}/users.db'):
        user_con = sqlite3.connect(f"{data_store}/users.db")
        user_cur =user_con.cursor()
        user_cur.execute('''CREATE TABLE users (username, hpass, email, last_access_date)''')
        user_cur.execute(f'INSERT INTO users VALUES ("admin", "password", "None", "None")')
        user_con.commit()
        user_con.close()

async def validate_token(token):
    if not os.path.exists(f"{wkdir}/token.json"):
        return False
    else:
        f = open(f"{wkdir}/token.json")
        data = json.load(f)
        f.close()
    if token == data["token"]:
        if datetime.now() > parser.parse(data["expiration"]):
            return False
        else:
            return True
    else:
        return False

async def generate_client_token():
    token = secrets.token_urlsafe(32)
    delta = datetime.now() + timedelta(hours=1)
    with open(f'{wkdir}/token.json', 'w') as f:
        data = {
            "token": f"{token}",
            "expiration": delta
        }
        json.dump(data,f,indent=4,default=str)
        f.close()
    return (token, delta)


