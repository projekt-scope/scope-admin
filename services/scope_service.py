""" scope_service class

"""


from typing import Tuple
import logging
import os
import json
import docker


LOGGER = logging.getLogger("scope-admin")


class ScopeService:
    """ scope_service class

    """

    def __init__(self, tag, folder, client):

        self.tag = tag
        self.client = client
        self.folder = folder
        self.config_path = os.path.join(self.path, "config.json")

    @property
    def image(self) -> docker.models.images.Image:
        """image

        Returns:
            Docker.Image: Image of service
        """

        if self.config["docker-hub"] == "False":
            return self.client.images.get(self.tag)
        return self.client.images.get(
            self.config["docker-hub-image"] + ":" + self.config["version"]
        )

    @property
    def name(self) -> str:
        """name

        Returns:
            str: name of service
        """
        return self.config["name"]

    @property
    def container(self) -> docker.models.containers.Container:
        """container

        Returns:
            Docker.Container: container instance of service
        """
        if self.check_if_container_exists():
            container = self.client.containers.get(self.tag)
            return container
        return False

    @property
    def logs(self) -> str:
        """logs

        Returns:
            str: logs from container
        """
        if self.check_if_container_exists():
            return self.container.logs()
        return False

    @property
    def path(self) -> str:
        """path

        Returns:
            str: path/folder of service
        """
        return os.path.join("services", self.folder)

    @property
    def ports(self) -> str:
        """ports

        Returns:
            str: Ports for docker building process
        """
        return self.config["ports"]

    @property
    def volumes(self) -> str:
        """volumes

        Returns:
            str: Volume for docker building process
        """
        return self.config["volumes"]

    @property
    def config(self) -> str:
        """config

        Returns:
            str: config of service
        """
        # everytime the config is needed the current config file is reloaded
        if os.path.exists(self.config_path):
            with open(self.config_path) as config_file:
                config = json.load(config_file)
            return config
        return ""

    @property
    def running(self) -> bool:
        """running

        Returns:
            bool: True if container is runnning, False if not
        """
        try:
            docker_container = self.client.containers.get(self.tag)
        except docker.errors.DockerException as e:
            LOGGER.error(e)
            return False
        # container is not running
        if docker_container.status != "running":
            return False

        return True

    def check_if_container_exists(self) -> bool:
        """check_if_container_exists

        Raises:
            Exception: Container not found

        Returns:
            bool: True if container exists, False if not
        """
        try:
            self.client.containers.get(self.tag)
            return True
        except docker.errors.DockerException as e:
            LOGGER.error(f"Container not found: {e}")
            raise Exception(f"Container not found: {e}")

    def change_config(self, option: str, data: dict) -> bool:
        """change_config

        Args:
            option (str): which part of the config should change
            data (dict): new data

        Returns:
            bool: True if changing was sucessfull, False if not
        """
        try:
            config_file = open(self.config_path, "r")
            config = json.load(config_file)
            config[option] = data
            config_file.close()

            new_config_file = open(self.config_path, "w")
            json.dump(config, new_config_file, indent=2)
            new_config_file.close()
            return True
        except Exception as e:
            LOGGER.debug.error(e)
            return False

    def run(self) -> bool:
        """run docker

        Raises:
            Exception: Error during running process

        Returns:
            bool: True if running started sucessful
        """
        try:
            # Host(`scope.localhost`) &&
            imagetag = self.tag + ":latest"
            if self.config["docker-hub"] == "True":
                imagetag = (
                    self.config["docker-hub-image"]
                    + ":"
                    + self.config["version"]
                )
            if os.environ["MODE"] == "PRODUCTION":
                labels = {
                    "traefik.enable": "true",
                    "traefik.http.routers."
                    + self.tag
                    + ".rule": "Host(`"
                    + os.environ["DOMAIN"]
                    + "`) && PathPrefix(`/"
                    + self.tag
                    + "`)",
                    "traefik.http.routers."
                    + self.tag
                    + ".entrypoints": "websecure,web",
                    "traefik.http.routers." + self.tag + ".tls": "true",
                    "traefik.http.routers."
                    + self.tag
                    + ".tls.certresolver": "myresolver",
                    "traefik.http.routers."
                    + self.tag
                    + ".middlewares": self.tag
                    + ",scope-auth@file",
                    "traefik.http.middlewares."
                    + self.tag
                    + ".stripprefix.prefixes": "/"
                    + self.tag,
                }
            else:
                labels = {
                    "traefik.enable": "true",
                    "traefik.http.routers."
                    + self.tag
                    + ".rule": "PathPrefix(`/"
                    + self.tag
                    + "`)",
                    "traefik.http.routers."
                    + self.tag
                    + ".middlewares": self.tag
                    + ",scope-auth@file",
                    "traefik.http.middlewares."
                    + self.tag
                    + ".stripprefix.prefixes": "/"
                    + self.tag,
                }
            self.client.containers.run(
                imagetag,
                detach=True,
                name=self.tag,
                # hostname=self.tag,
                environment=self.environment,
                ports=self.ports,
                volumes=self.volumes,
                network="scope-net",
                labels=labels,
            )
            return True
        except Exception as e:
            LOGGER.error(e)
            raise Exception(f"Could not start containter. {str(e)}")

    def restart(self) -> bool:
        """restart container

        Raises:
            Exception: DockerException

        Returns:
            bool: True if restarting worked, Exception if not
        """
        try:
            self.container.restart()
            return True
        except Exception as e:
            raise Exception(f"Could not start container. {str(e)}")

    def stop(self) -> bool:
        """stop container

        Raises:
            Exception: DockerException

        Returns:
            bool: True if stopping worked, Exception if not
        """
        try:
            self.container.stop()
            return True
        except Exception as e:
            raise Exception(f"Could not stop container. {str(e)}")

    def build(self) -> Tuple[bool, str]:
        """build

        Raises:
            Exception:  DockerException


        Returns:
            Tuple[bool, str]: Status, information of the building process.
        """
        LOGGER.debug("Building Docker-Image")
        try:
            if self.config["docker-hub"] == "False":
                tag = self.config["tag"]
                # TODO get build args from config file
                args = {
                    "path": str(self.path),
                    "tag": f"{tag}:latest",
                    "pull": True,
                    "forcerm": True,
                    "buildargs": {"BUILD_FROM": "test"},
                    "network_mode": "scope-net",
                }
                image = self.client.images.build(**args)
                LOGGER.info("Build %s done.", image)
                # LOGGER.debug(
                #     f"image id : {image.id}, image labels: {image.labels},\
                #     image short_id: {image.short_id}, image tags: {image.tags}"
                # )
                return (
                    True,
                    f"The image {tag}:latest has been successful build",
                )
            return (self.pull(), "The image has been successful pulled")
        except docker.errors.DockerException as e:
            raise Exception(f"Could not build container. {e}")

    def pull(self) -> bool:
        """pull

        Returns:
            bool: True if pulling from docker-hub worked, False if not
        """
        LOGGER.debug("Pulling from Docker-Hub")
        try:
            image = self.client.images.pull(
                self.config["docker-hub-image"] + ":" + self.config["version"]
            )
        except docker.errors.DockerException as e:
            LOGGER.error(e)
            return False
        LOGGER.info(image)
        return True

    def uninstall(self) -> None:
        """uninstall image
        """
        self.client.images.remove(self.tag)

    def remove_container(self) -> None:
        """remove_container
        """
        self.stop()
        self.container.remove()

    @property
    def environment(self):
        """Return environment for the Service"""
        service_env = {}

        for key, value in self.config["environment"].items():
            if isinstance(value, (int, str)):
                service_env[key] = value
            else:
                LOGGER.warning(
                    "Can not set nested option %s as Docker env", key
                )
        # LOGGER.debug(service_env)
        return {**service_env}
