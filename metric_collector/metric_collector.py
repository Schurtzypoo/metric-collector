import os, psutil, platform, json, argparse, requests, time, logging, systemd
from datetime import datetime, timedelta
from systemd.journal import JournaldLogHandler

logger = logging.getLogger(__name__)
journald_handler = JournaldLogHandler()
journald_handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(message)s'
))
logger.setLevel(logging.INFO)
logger.addHandler(journald_handler)
def get_cpu_count():
    try:
        cpu_count = psutil.cpu_count()
        logger.info("Successfully collected system cpu count!")
        return cpu_count
    except:
        logger.warning("Failed to collect cpu count! Error in func get_cpu_count in metric_collector.py")
        return 'Error'

def get_cpu_usage(percpu):
    try:
        cpu_percent = psutil.cpu_percent(interval = 0.1, percpu=percpu)
        logger.info("Successfully collected system cpu usage!")
        return cpu_percent
    except:
        logger.warning("Failed to collect cpu usage! Error in func get_cpu_usage in metric_collector.py")
        return 'Error'

def get_mem_stats():
    try:
        mem = psutil.virtual_memory()
        logger.info("Successfully collected system memory usage!")
        return {
            "mem_total": mem.total/1024/1024/1024, #GB memory
            "mem_used": mem.used/1024/1024/1024,
            "mem_free": mem.free/1024/1024/1024,
            "mem_available": mem.available/1024/1024/1024,
            "percent_used": mem.percent
        }
    except:
        logger.warning("Failed to collect memory statistics! Error in func get_mem_stats in metric_collector.py")
        return 'Error'

def get_disk_stats():
    try:
        disks = psutil.disk_partitions(all=False)
        logger.info("Successfully gathered System Disk/Partition info!")
    except:
        logger.warning("Failed to collect disk/partition info! Error in func get_disk_stats in metric_collector.py")
        return 'Error'
    disk_stats = {}
    for d in disks:
        try:
            usage = psutil.disk_usage(d.mountpoint)
            disk_stats[d.mountpoint] = {
                "disk_mountpoint": d.mountpoint,
                "disk_fstype": d.fstype,
                "disk_size": usage.total/1024/1024/1024,
                "disk_used": usage.used/1024/1024/1024,
                "disk_free": usage.free/1024/1024/1024,
                "percent_used": usage.percent
            }
        except:
            logger.warning(f'Failed to collect disk: {d} detailed information. Error in func get_disk_stats in metric_collector.py')
            disk_stats[d.mountpoint] = f"Error in disk: {d} stats collection."
    return disk_stats

def get_network_stats():
    network_stats = {}
    try:
        nics = psutil.net_if_addrs()
        traffic_stats = psutil.net_io_counters(pernic=True)
        nic_info = psutil.net_if_stats()
    except:
        logger.warning("Failed to collect Nic info! Error in func get_network_stats in metric_collector.py")
        return 'Error'
    for nic in nics:
        addresses = [a.address for a in nics[nic]]
        families = [f.family for f in nics[nic]]
        network_stats[nic] = {
            "interface": nic,
            "addresses": addresses,
            "address_families": families,
            "speed": nic_info[nic].speed,
            "MTU": nic_info[nic].speed,
            "duplex": nic_info[nic].duplex,
            "packets_in": traffic_stats[nic].packets_recv,
            "packets_out": traffic_stats[nic].packets_sent,
            "bytes_in": traffic_stats[nic].bytes_recv,
            "bytes_out": traffic_stats[nic].bytes_sent
        }
    return network_stats

def main():
    operating_system = platform.platform()
    system_name = platform.node()
    cpu_count = get_cpu_count()
    cpu_usage = get_cpu_usage(percpu=False)
    memory_stats = get_mem_stats()
    disk_stats = get_disk_stats()
    network_stats = get_network_stats()
    data  = {
        "system_name": system_name,
        "operating_system": operating_system,
        "cpu_count": cpu_count,
        "cpu_usage": cpu_usage,
        "memory_stats": memory_stats,
        "disk_stats": disk_stats,
        "network_stats": network_stats,
        "datetime": datetime.now()
    }
    file_name = f"{system_name}_metrics.json"
    if not os.path.exists("./metric_data"):
        try:
            os.mkdir("./metric_data")
        except:
            logger.warning("Failed to create metric_data directory. Please verify permissions.")
    with open(f'./metric_data/{file_name}', 'w') as f:
        json.dump(data,f,indent=4,default=str)
        f.close()
    logger.info(f"{file_name} created in metric_data. Pending offload.")
    return file_name
def connection_manager(mgmt_server, token):
    logger.info("Connection to mgmt_server initiated...")
    file_name = main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Launch Metric Collector")
    parser.add_argument('--mgmt_hostname', type=str)
    parser.add_argument('--token', type=str)
    args = parser.parse_args()
    while True:
        logger.info("Metric Collector Started!")
        connection_manager(args.mgmt_hostname, args.token)
        time.sleep(60)