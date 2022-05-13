from atexit import register
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
        clients_cur = clients_con.cursor()
        clients_cur.execute('''CREATE TABLE registered_clients (hostname, date_registered)''')
        clients_cur.execute('''CREATE TABLE system_metrics (hostname, operating_system, cpu_count, cpu_usage, mem_total, mem_used, mem_free, mem_available, mem_percent_used, polling_interval, upload_date)''')
        clients_cur.execute('''CREATE TABLE nic_metrics (hostname, interface, address, address_family, speed, MTU, duplex, packets_in, packets_out, bytes_in, bytes_out, upload_date)''')
        clients_cur.execute('''CREATE TABLE disk_metrics (hostname, disk_device, disk_mount_point, disk_fstype, disk_size, disk_used, disk_free, percent_used, upload_date)''')
        clients_con.commit()
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

async def store_metrics(metric_file_path):
    f = open(f"{metric_file_path}")
    metric = json.load(f)
    f.close()
    clients_con = sqlite3.connect(f"{data_store}/clients.db")
    cur = clients_con.cursor()
    registered_clients = cur.execute(f'''SELECT * FROM registered_clients WHERE hostname=?''', (metric["system_name"],)).fetchone()
    if registered_clients == None:
        return "NR"
    else: #(operating_system, cpu_count, cpu_usage, mem_total, mem_used, mem_free 
    #mem_available, mem_percent_used, polling_interval, upload_date)
        try:
            cur.execute(f'''INSERT INTO system_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                metric["system_name"],
                metric["operating_system"],
                metric["cpu_count"], 
                metric["cpu_usage"], 
                metric["memory_stats"]["mem_total"],
                metric["memory_stats"]["mem_used"],
                metric["memory_stats"]["mem_free"],
                metric["memory_stats"]["mem_available"],
                metric["memory_stats"]["percent_used"],
                metric["polling_interval"],
                metric["datetime"]
            ))
            clients_con.commit()
        except:
            return "MEM_ERROR"
        try:
            nics = metric["network_stats"]
            for nic, data in nics.items():
                cur.execute(f'''INSERT INTO nic_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    metric["system_name"],
                    data["interface"],
                    data["address"],
                    data["address_family"],
                    data["speed"],
                    data["MTU"],
                    data["duplex"],
                    data["packets_in"],
                    data["packets_out"],
                    data["bytes_in"],
                    data["bytes_out"],
                    metric["datetime"]
                ))
                clients_con.commit()
        except:
            return "NIC_ERROR"
        try:
            disks = metric["disk_stats"]
            for disk, data in disks.items():
                cur.execute(f'''INSERT INTO disk_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    metric["system_name"],
                    data["disk_device"],
                    data["disk_mountpoint"],
                    data["disk_fstype"],
                    data["disk_size"],
                    data["disk_used"],
                    data["disk_free"],
                    data["percent_used"],
                    metric["datetime"]
                ))
                clients_con.commit()
        except:
            return "DISK_ERROR"
        clients_con.close()
        return "ACCEPTED"


