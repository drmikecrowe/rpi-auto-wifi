import unittest
from unittest.mock import patch
import subprocess

from rpi_auto_wifi import rpi_connect
from rpi_auto_wifi.wpa_util import WpaHelper

def generic_command(cmds: list):
    connected = False
    def response(cmd):
        for i in range(len(cmds)):
            if not cmds[i].startswith(f"{cmd}-"):
                continue
            print(f"For CMD={cmd}, POPPED ", cmds[i])
            stdout = open(f"tests/fixtures/{cmds[i]}").read()
            del cmds[i]
            if stdout.find("wpa_state=COMPLETED") > -1:
                connected = True
            return stdout
        print(f"For CMD={cmd}, returning default")
        if cmd == "ping":
            return "PONG"
        if cmd == "scan_results":
            return open(f"tests/fixtures/scan_results-empty.txt").read()
        if cmd == "conn_status":
            if connected:
                return open(f"tests/fixtures/conn_status-connected.txt").read()
            else:
                return open(f"tests/fixtures/conn_status-disconnected.txt").read()
        return "OK"

    def cmd(cmd, *args, ifname=None):
        status = True
        r = subprocess.CompletedProcess(args, 0, response(cmd), None)
        return status, r
    return cmd



class TestAlreadyConnected(unittest.TestCase):

    @patch.object(rpi_connect.wpa_util.WpaHelper, 'command', generic_command(cmds = [
        "status-connected.txt",
    ]))
    def test_already_connected(self):
        self.assertTrue(rpi_connect.check_connected())


    @patch.object(rpi_connect.wpa_util.WpaHelper, 'command', generic_command(cmds = [
    ]))
    def test_reconnect_connected(self):
        self.assertFalse(rpi_connect.check_connected())


    @patch.object(rpi_connect.wpa_util.WpaHelper, 'command', generic_command(cmds = [
        "scan_results-empty.txt",
    ]))
    def test_open_no_networks_fail(self):
        self.assertFalse(rpi_connect.try_open())


    @patch.object(rpi_connect.wpa_util.WpaHelper, 'command', generic_command(cmds = [
        "scan_results-open.txt",
        "status-connected.txt",
    ]))
    def test_open_pass(self):
        self.assertTrue(rpi_connect.try_open())


    @patch.object(rpi_connect.wpa_util.WpaHelper, 'command', generic_command(cmds = [
        "scan_results-aes_wps_off.txt",
    ]))
    def test_wpa_wps_off_failed(self):
        self.assertFalse(rpi_connect.try_wps())


    @patch.object(rpi_connect.wpa_util.WpaHelper, 'command', generic_command(cmds = [
        "scan_results-aes_wps_on.txt",
        "status-connected.txt",
    ]))
    def test_wpa_wps_on_pass(self):
        self.assertTrue(rpi_connect.try_wps())



if __name__ == '__main__':
    unittest.main()


