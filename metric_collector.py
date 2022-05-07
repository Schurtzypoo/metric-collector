import os, psutil, platform, json, argparse, requests, time
from datetime import datetime, timedelta

def get_cpu_count():
    return psutil.cpu_count()

def get_cpu_usage(percpu):
    return psutil.cpu_percent(interval = 0.1, percpu=percpu)

def get_mem_stats():
    mem = psutil.virtual_memory()
    return {
        "mem_total": mem.total/1024/1024/1024, #GB memory
        "mem_used": mem.used/1024/1024/1024,
        "mem_free": mem.free/1024/1024/1024,
        "mem_available": mem.available/1024/1024/1024,
        "percent_used": mem.percent
    }

def get_disk_stats():
    disks = psutil.disk_partitions(all=False)
    disk_stats = {}
    for d in disks:
        usage = psutil.disk_usage(d.mountpoint)
        disk_stats[d.mountpoint] = {
            "disk_mountpoint": d.mountpoint,
            "disk_fstype": d.fstype,
            "disk_size": usage.total/1024/1024/1024,
            "disk_used": usage.used/1024/1024/1024,
            "disk_free": usage.free/1024/1024/1024,
            "percent_used": usage.percent
        }
    return disk_stats

def get_network_stats():
    network_stats = {}
    nics = psutil.net_if_addrs()
    traffic_stats = psutil.net_io_counters(pernic=True)
    nic_info = psutil.net_if_stats()
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
    with open(file_name, 'w') as f:
        json.dump(data,f,indent=4,default=str)
        f.close()
    return file_name
def connection_manager(mgmt_server, token):
    file_name = main()
    print(datetime.now())



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Launch Metric Collector")
    parser.add_argument('--mgmt_hostname', type=str)
    parser.add_argument('--token', type=str)
    args = parser.parse_args()
    while True:
        connection_manager(args.mgmt_hostname, args.token)
        time.sleep(60)