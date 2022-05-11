from metric_collector import main as mcm
import requests, os, argparse, shutil
parser = argparse.ArgumentParser()
parser.add_argument('--mgmt_hostname', type=str, default='https://localhost')
parser.add_argument("--poll_int", type=int, default=60)
parser.add_argument("--token", type=str, default="6oQWDrvk-FTAjMUe3WXl46-TptNJzzSaMdbfCDCFcBk")
args = parser.parse_args()
file_name = mcm(args.poll_int)[0]
wkdir = os.path.dirname(os.path.abspath(__file__))
filepath = f"{wkdir}/metric_data/{file_name}"

headers = {'accept':'application/json'}
metric_file = {'metric_file': open(filepath, 'rb')}
x = requests.post(f"{args.mgmt_hostname}/api/registration/register_client?token={args.token}", files=metric_file, headers=headers, verify=False)
try:
    os.mkdir(f'{wkdir}/certificates')
except FileExistsError:
    pass
open(f"{wkdir}/certificates/certs.tar", "wb").write(x.content)
# with zipfile.ZipFile(f"{wkdir}/certificates/certs.zip", 'r') as uzip:
#     uzip.extractall(f"{wkdir}/certificates")
shutil.unpack_archive(f"{wkdir}/certificates/certs.tar", f"{wkdir}/certificates/", "tar")
