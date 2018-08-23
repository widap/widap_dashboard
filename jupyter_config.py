import os
from oauthenticator.google import GoogleOAuthenticator
c.JupyterHub.authenticator_class = GoogleOAuthenticator
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.JupyterHub.hub_ip = '0.0.0.0'
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = { '/home/ubuntu/widap_dashboard': notebook_dir }
c.DockerSpawner.remove_containers = True
c.DockerSpawner.debug = True
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
c.Spawner.args = ['--NotebookApp.default_url=/notebooks/WIDAP_Dashboard.ipynb']
