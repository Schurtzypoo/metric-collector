#!/bin/sh
yum install python3 -y
pip3 install venv
mkdir /opt/metric_collector
python3 -m venv /opt/metric_collector/venv
source /opt/metric_collector/venv/bin/activate
pip3 install psutil platform json argparse requests datetime os
cp requirements/metric_collector.py /opt/metric_collector/
cp requirements/metric_collector.service /etc/systemd/system/metric_collector.service
chmod 0664 /etc/systemd/system/metric_collector.service
systemctl daemon-reload
systemctl start metric_collector
systemctl enable metric_collector
systemctl metric_collector status