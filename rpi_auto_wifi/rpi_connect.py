import os
import sys
import time
import logging
import logging.handlers

from . import wpa_util


# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


if os.geteuid()==0:
    sh = logging.handlers.SysLogHandler()
else:
    sh = logging.handlers.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)

sh.setLevel(logging.DEBUG)
logger.addHandler(sh)


RETRIES = 10
WAIT = 6


def check_connected():
    logger.debug("Checking connection status")
    ok, status = wpa_util.WifiUtil.conn_status()
    logger.debug("conn_status" + repr([ok, status]))
    if ok and status["wpa_state"] != "DISCONNECTED":
        logger.info("Connected!")
        return True


def try_open():
    logger.debug("Trying to connect to an open network")
    ok, status = wpa_util.WifiUtil.scan_network()
    logger.debug("scan_network" + repr([ok, status]))
    if not ok or not status:
        logger.info("Scan failed, try again")
        return
    for ap in status:
        if ap["flags"].find("WPA") == -1:
            wpa_util.WifiUtil.add_network(ap["ssid"])
            if try_reconnect():
                return True


def try_wps():
    logger.debug("Trying to connect to a wps enabled")
    ok, status = wpa_util.WifiUtil.scan_network()
    logger.debug("scan_network" + repr([ok, status]))
    if not ok or not status:
        logger.info("Scan failed, try again")
        return
    with_wps = [f for f in status if f["flags"].find("WPS-PBC") > -1]
    if not with_wps:
        logger.info("No AP's found with WPS active")
        return
    for ap in sorted(with_wps, key=lambda k: k["signal level"]):
        bssid = ap["bssid"]
        ok, status = wpa_util.WifiUtil.wps_connect(bssid)
        logger.info("wps_connect" + repr([ok, status]))
        if check_connected():
            return True
    return False


def try_reconnect():
    logger.info("Attempting to reconnect")
    ok, status = wpa_util.WifiUtil.reconnect()
    logger.info("reconnect" + repr([ok, status]))
    return check_connected()


def try_connect():
    if check_connected():
        return True
    if try_reconnect():
        return True
    if try_open():
        return True
    if try_wps():
        return True
    return False


if __name__ == '__main__':
    for retries in range(RETRIES):
        if try_connect():
            sys.exit(0)
        time.sleep(WAIT)

    sys.exit(1)
