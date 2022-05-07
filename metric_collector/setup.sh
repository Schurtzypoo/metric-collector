#!/usr/bin/env bash
yum install python3 python3-pip gcc python3-devel systemd-devel -y
mkdir /opt/metric_collector
python3 -m venv /opt/metric_collector/venv
source /opt/metric_collector/venv/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install psutil argparse requests datetime systemd
cp metric_collector.py /opt/metric_collector/
cp requirements/metric_collector.service /etc/systemd/system/metric_collector.service
chmod 0664 /etc/systemd/system/metric_collector.service
systemctl daemon-reload
systemctl start metric_collector
systemctl enable metric_collector
systemctl status metric_collector