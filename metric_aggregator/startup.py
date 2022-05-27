import os, platform
from ownca import CertificateAuthority
from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

ca_name = platform.node()
wkdir = os.path.dirname(os.path.abspath(__file__))
ca_file_path = f"{wkdir}/certificate_store"
data_store = f"sqlite:///{wkdir}/data_store/metrics.db"
users_store = f"sqlite:///{wkdir}/data_storeusers.db"
client_metric_store = f"{wkdir}/metric_store"

Base = declarative_base()
class registered_client(Base):
    __tablename__ = "registered_clients"
    id = Column(Integer, primary_key = True)
    system_name = Column(String)
    date_registered = Column(DateTime, unique = False)
    system_metric = relationship("system_metrics", backref="registered_clients")
    nic_metrics = relationship("nic_metrics", backref="registered_clients")
    disk_metrics = relationship("disk_metrics", backref="registered_clients")

class system_metrics(Base):
    __tablename__ = "system_metrics"
    id = Column(Integer, primary_key = True)
    system_name = Column(String, ForeignKey('registered_clients.system_name'), unique = False)
    operating_system = Column(String)
    cpu_count = Column(Integer, unique = False)
    cpu_usage = Column(Float, unique = False)
    mem_total = Column(Float, unique = False)
    mem_used = Column(Float, unique = False)
    mem_free = Column(Float, unique = False)
    mem_available = Column(Float, unique = False)
    mem_percent_used = Column(Float, unique = False)
    polling_interval = Column(Integer, unique = False)
    datetime = Column(DateTime, unique = False)

class nic_metrics(Base):
    __tablename__ = "nic_metrics"
    id = Column(Integer, primary_key = True)
    system_name = Column(String, ForeignKey('registered_clients.system_name'), unique = False)
    interface = Column(String, unique = False)
    address = Column(String, unique = False)
    address_family = Column(String, unique = False)
    speed = Column(Integer, unique = False)
    mtu = Column(Integer, unique = False)
    duplex = Column(String, unique = False)
    packets_in = Column(Integer, unique = False)
    packets_out = Column(Integer, unique = False)
    bytes_in = Column(Integer, unique = False)
    bytes_out = Column(Integer, unique = False)
    datetime = Column(DateTime, unique = False)

class disk_metrics(Base):
    __tablename__ = "disk_metrics"
    id = Column(Integer, primary_key = True)
    system_name = Column(String, ForeignKey('registered_clients.system_name'), unique = False)
    disk_device = Column(String, unique = False)
    disk_mountpoint = Column(String, unique = False)
    disk_fstype = Column(String, unique = False)
    disk_size = Column(Float, unique = False)
    disk_used = Column(Float, unique = False)
    disk_free = Column(Float, unique = False)
    disk_percent_used = Column(Float, unique = False)
    datetime = Column(DateTime, unique = False)

async def cert_metric_store():
    if not os.path.exists(ca_file_path):
        os.mkdir(ca_file_path)
        ca = CertificateAuthority(ca_storage = ca_file_path, common_name=ca_name, dns_names = [ca_name, "192.168.1.23"])
    else:
        ca = CertificateAuthority(ca_storage = ca_file_path, common_name=ca_name, dns_names = [ca_name, "192.168.1.23"])
    if not os.path.exists(f'{wkdir}/data_store'):
        os.mkdir(f'{wkdir}/data_store')
    if not os.path.exists(f'{data_store}'):
        metric_engine = create_engine(f'{data_store}')
        Base.metadata.create_all(metric_engine)
    if not os.path.exists(f'{client_metric_store}'):
        os.mkdir(f"{client_metric_store}")

# async def user_store():
#     if not os.path.exists(f'{data_store}/users.db'):
#         user_con = sqlite3.connect(f"{data_store}/users.db")
#         user_cur =user_con.cursor()
#         user_cur.execute('''CREATE TABLE users (username, hpass, email, last_access_date)''')
#         user_cur.execute(f'INSERT INTO users VALUES ("admin", "password", "None", "None")')
#         user_con.commit()
#         user_con.close()