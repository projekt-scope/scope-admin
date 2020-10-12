""" scope_admin class

"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List

import docker

from services.scope_external_service import ScopeExternalService
from services.scope_service import ScopeService

LOGGER = logging.getLogger("scope-admin")

SOCKET_DOCKER = Path("/run/docker.sock")
# print(os.environ["DOCKER_HOST"])


class ScopeAdmin:
    """ Class to control and watch the services
    """

    def __init__(self):
        try:
            self.client: docker.DockerClient = docker.DockerClient(
                base_url="unix:/{}".format(str(SOCKET_DOCKER)),
                version="auto",
                timeout=900,
            )
        except docker.errors.DockerException as e:
            LOGGER.warning(
                f"It looks like you are running scope-admin not on a linux\
                system. Be careful, I will try to find the docker\
                client somewhere else. Docker Error: {e}"
            )
            try:
                self.client = docker.from_env()
            except docker.errors.DockerException as e:
                LOGGER.error(
                    f"I could not found the docker client from env. {e}"
                )

        try:
            # LOGGER.info(
            str(self.client.info())
            # )
        except Exception as e:
            LOGGER.error(
                f"It looks like Docker is not running at your System.\
                Please start Docker and restart the service. {e}"
            )

        self.config_path = os.path.join("services", "services_config.json")
        self.services = []
        self.external_services = []
        with open(self.config_path) as self.config_file:
            self.config = json.load(self.config_file)
        for result in self.internal_service_tags_and_folder:
            service = ScopeService(
                result["tag"], result["folder"], self.client
            )
            # LOGGER.debug(service.config)
            if service.config:
                self.services.append(service)

    @property
    def internal_service_tags_and_folder(self) -> List:
        """internal_service_tags_and_folder

        Returns:
            List: List of folder
            and tags for all services which are internal
        """
        result = []
        for service in self.config["internal"]:
            result.append(
                {
                    "folder": service,
                    "tag": self.config["internal"][service]["tag"],
                }
            )
        return result

    @property
    def registered_internal_service_tags(self) -> List[str]:
        """registered_internal_service_tags

        Returns:
            List[str]: tag of all registerd services
        """
        return [service.tag for service in self.services]

    @property
    def external_service_infos(self) -> str:
        """external_service_infos

        Returns:
            str: information about external services
        """
        ScopeExternalService.getExtServiceFromDict(self.config["external"])
        return self.config["external"]

    def register_service(self, folder: str, tag: str) -> bool:
        """register_service Register a service with a folder and tag

        Args:
            folder (str): folder in which the service is located
            tag (str): unique tag for the service

        Returns:
            bool: True if registration was successfull and False if something
                  went wrong
        """
        if not self.check_if_services_is_already_registered(tag):
            try:
                config_file = open(self.config_path, "r")
                config = json.load(config_file)
                config["internal"].update(
                    {folder: {"core-service": "false", "tag": tag}}
                )
                config_file.close()
                new_config_file = open(self.config_path, "w")
                json.dump(config, new_config_file, indent=2)
                new_config_file.close()
                self.services.append(ScopeService(tag, folder, self.client))
                return True
            except Exception as e:
                LOGGER.error(e)
                return False
        return False

    def check_if_services_is_already_registered(self, tag: str) -> bool:
        """check_if_services_is_already_registered

        Args:
            tag (str): tag of service

        Returns:
            bool: True if service is already registered, False if not
        """
        if self.config.get(tag):
            return True
        return False

    def check_status_of_services(self) -> Dict[str, List[str]]:
        """check_status_of_services

        Returns:
            Dict[str, List[str]]: Dict of service tags and
            corresponding status, description and name of the service as a list
        """
        status_dict = dict()
        for service in self.services:
            status_dict.update(
                {
                    service.tag: [
                        service.running,
                        service.config["description"],
                        service.name,
                    ]
                }
            )
        return status_dict

    def get_service_with_tag(self, tag: str) -> ScopeService:
        """get_service_with_tag

        Args:
            tag (str): tag of service

        Returns:
            ScopeService: Instance of the service
        """
        for service in self.services:
            if tag == service.tag:
                return service
        return None

    def get_ext_service_with_tag(self, tag: str) -> ScopeExternalService:
        """get_ext_service_with_tag

        Args:
            tag (str): tag of service

        Returns:
            ScopeExternalService: Instance of the external service
        """
        for ext_service in self.external_services:
            if tag == ext_service.tag:
                return ext_service
        return None
