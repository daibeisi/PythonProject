import docker

client = docker.DockerClient(base_url='tcp://192.168.253.142:2375')
print(client.info())

client.images.build(path='.', tag='test')
