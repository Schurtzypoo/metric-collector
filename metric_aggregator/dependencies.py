import os, platform, sqlalchemy, secrets, datetime, json, sqlite3
from datetime import datetime, timedelta
from dateutil import parser
from ownca import CertificateAuthority
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from startup import Base, wkdir, data_store, client_metric_store, system_metrics, disk_metrics, nic_metrics, registered_client


async def validate_token(token):
    # return True
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
    metric_engine = create_engine(f"{data_store}")
    Base.metadata.bind = metric_engine
    DBsession = sessionmaker()
    DBsession.bind = metric_engine
    session = DBsession()
    registered = session.query(registered_client).filter_by(system_name=f"{metric['system_name']}").first()
    if registered is None:
        return "NR"
    else: #(operating_system, cpu_count, cpu_usage, mem_total, mem_used, mem_free 
    #mem_available, mem_percent_used, polling_interval, upload_date)
        try:
            system = system_metrics()
            system.system_name = metric["system_name"]
            system.operating_system = metric["operating_system"]
            system.cpu_count = metric["cpu_count"]
            system.cpu_usage = metric["cpu_usage"]
            system.mem_total = metric["memory_stats"]["mem_total"]
            system.mem_used = metric["memory_stats"]["mem_used"]
            system.mem_free = metric["memory_stats"]["mem_free"]
            system.mem_available = metric["memory_stats"]["mem_available"]
            system.mem_percent_used = metric["memory_stats"]["percent_used"]
            system.polling_interval = metric["polling_interval"]
            system.datetime = parser.parse(metric["datetime"])
            session.add(system)
            session.commit()
        except:
            return "SYS_METRIC_ERROR"
        try:
            nics = metric["network_stats"]
            for nic, data in nics.items():
                system_nic = nic_metrics()
                system_nic.system_name = metric["system_name"]
                system_nic.interface = data["interface"]
                system_nic.address = data["address"]
                system_nic.address_family = data["address_family"]
                system_nic.speed = data["speed"]
                system_nic.mtu = data["MTU"]
                system_nic.duplex = data["duplex"]
                system_nic.packets_in = data["packets_in"]
                system_nic.packets_out = data["packets_out"]
                system_nic.bytes_in = data["bytes_in"]
                system_nic.bytes_out = data["bytes_out"]
                system_nic.datetime = parser.parse(metric["datetime"])
                session.add(system_nic)
                session.commit()
        except:
            return "NIC_ERROR"
        try:
            disks = metric["disk_stats"]
            for disk, data in disks.items():
                system_disk = disk_metrics()
                system_disk.system_name = metric["system_name"]
                system_disk.disk_device = data["disk_device"]
                system_disk.disk_mountpoint = data["disk_mountpoint"]
                system_disk.disk_fstype = data["disk_fstype"]
                system_disk.disk_size = data["disk_size"]
                system_disk.disk_used = data["disk_used"]
                system_disk.disk_free = data["disk_free"]
                system_disk.disk_percent_used = data["percent_used"]
                system_disk.datetime = parser.parse(metric["datetime"])
                session.add(system_disk)
                session.commit()
        except:
            return "DISK_ERROR"
        session.close()
        return "ACCEPTED"


