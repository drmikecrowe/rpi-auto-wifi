import os
import sys
import json
import time


if os.getcwd() not in sys.path:
    # TODO: remove
    sys.path.insert(0, os.getcwd())

from wpa_util import wpa_util


def try_open():
    ok, status = wpa_util.WifiUtil.scan_network()
    print("scan_network", ok, json.dumps(status, indent=4))
    if not ok or not status:
        print("Scan failed, try again")
        return
    # for ap in status:
    #   if ap


def try_wps():
    ok, status = wpa_util.WifiUtil.scan_network()
    print("scan_network", ok, json.dumps(status, indent=4))
    if not ok or not status:
        print("Scan failed, try again")
        return
    with_wps = [f for f in status if f["flags"].find("WPS-PBC") > -1]
    if not with_wps:
        print("No AP's found with WPS active")
        return
    for ap in sorted(with_wps, key=lambda k: k["signal level"]):
        bssid = ap["bssid"]
        ok, status = wpa_util.WifiUtil.wps_connect(bssid)
        print("wps_connect", ok, json.dumps(status, indent=4))
        if ok:
            print("Connected via WPS!")
            sys.exit(0)


def check_connected():
    ok, status = wpa_util.WifiUtil.conn_status()
    print("conn_status", ok, json.dumps(status, indent=4))
    if ok and status["wpa_state"] != "DISCONNECTED":
        print("Connected!")
        sys.exit(0)


def check_reconnect():
    ok, status = wpa_util.WifiUtil.reconnect()
    print("reconnect", ok, status)


for retries in range(10):
    check_connected()
    check_reconnect()
    check_connected()
    try_open()
    try_wps()
    break
    time.sleep(6)

print("Will shutdown now!")
# os.system("shutdown -r now")
