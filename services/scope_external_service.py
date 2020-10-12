# FIXME this class is not done yet
import logging
import platform
import subprocess


LOGGER = logging.getLogger("scope-admin")


class ScopeExternalService:
    def __init__(self, tag, paramsDict):
        self._tag = tag
        self._name = paramsDict["name"]
        self._description = paramsDict["description"]
        self._adress = paramsDict["adress"]
        self._port = paramsDict["port"]

    @property
    def tag(self):
        return self._tag

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def adress(self):
        return self._adress

    @property
    def port(self):
        return self._port

    @staticmethod
    def getExtServiceFromDict(dictionary):
        for tag, params in dictionary.items():
            ScopeExternalService(tag, params)

    def ping(self, host):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        # Option for the number of packets as a function of
        param = "-n" if platform.system().lower() == "windows" else "-c"

        # Building the command. Ex: "ping -c 1 google.com"
        command = ["ping", param, "1", host]

        return subprocess.call(command) == 0