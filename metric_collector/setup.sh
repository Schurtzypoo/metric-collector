#!/usr/bin/env bash
function usage() {
    cat <<USAGE

    Usage: $0 [-m mgmt server hostname or ip] [-p polling intervale in seconds] [-t registration token] [-h help]

    Options:
        -m:            Hostname or IP Address of Management Server (for metric offload)
        -p:            Polling Interval (offload frequency) in seconds. Default: 60
        -t:            Client Registration Token
        -h:            Display this prompt (help)
USAGE
    exit 1
}
HOST=""
TOKEN=""
POLL=60
if [ $# -eq 0 ]; then
    usage
    exit 1
fi
while getopts m:t:p: flag 
do
    case "${flag}" in
    m)
        HOST=${OPTARG}
        ;;
    t)
        TOKEN=${OPTARG}
        ;;
    p)
        POLL=${OPTARG}
        ;;
    h | --help)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
    esac
done
if [[ HOST == "" ]]; then
    echo "You must provide a Hostname";
    exit 1;
fi
if [[ TOKEN == "" ]]; then
    echo "You must provide a Registration Token";
    exit 1;
fi
yum install python3 python3-pip gcc python3-devel systemd-devel -y
mkdir /opt/metric_collector
python3 -m venv /opt/metric_collector/venv
source /opt/metric_collector/venv/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install psutil argparse requests datetime systemd python-multipart
cp metric_collector.py /opt/metric_collector/
cp registration.py /opt/metric_collector
python3 /opt/metric_collector/registration.py --mgmt_hostname="$HOST" --poll_int=$POLL --token="$TOKEN"
cp requirements/metric_collector.service /etc/systemd/system/metric_collector.service
sed -i "s/MGMTSERVER/$HOST/" /etc/systemd/system/metric_collector.service
sed -i "s/POLL_INT/$POLL/" /etc/systemd/system/metric_collector.service
chmod 0664 /etc/systemd/system/metric_collector.service
systemctl daemon-reload
systemctl start metric_collector
systemctl enable metric_collector
systemctl status metric_collector