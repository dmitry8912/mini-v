import os

import docker


class MiniVContainerManager:
    __containers = dict()
    __instance = None
    __client = None
    __image_name = 'miniv-gw'

    @staticmethod
    def get_instance():
        if MiniVContainerManager.__instance is None:
            MiniVContainerManager.__instance = MiniVContainerManager()
        return MiniVContainerManager.__instance

    def __int__(self):
        self.__client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    def build_image(self):
        return self.__client.images.build(path='../build', tag=MiniVContainerManager.__image_name)

    def get_image(self):
        self.__client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        return self.__client.images.get(MiniVContainerManager.__image_name)

    def run_container(self, client_id: str, external_port: int, ssh_username: str, ssh_password: str,
                      tunnel_destination: str):
        self.__client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        img = self.get_image()
        container = self.__client.containers.run(img,
                                                 detach=True,
                                                 remove=True,
                                                 environment={
                                                     "SSH_USER": ssh_username,
                                                     "SSH_PASS": ssh_password,
                                                     "TO_HOST": tunnel_destination
                                                 },
                                                 ports={'22/tcp': external_port})
        self.__containers[client_id] = container

    def stop_container(self, client_id: str):
        self.__containers[client_id].stop()
