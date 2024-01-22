import os
import sys
from oauthenticator.google import LocalGoogleOAuthenticator
from oauthenticator.generic import GenericOAuthenticator

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_IMAGE']
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.JupyterHub.hub_ip = os.environ['HUB_IP']

# Redirect to JupyterLab, instead of the plain Jupyter notebook
c.Spawner.default_url = '/lab'

c.JupyterHub.load_roles = [
    {
        "name": "jupyterhub-idle-culler-role",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:servers",
            "delete:servers",
            # "admin:users", # if using --cull-users
        ],
        # assignment of role's permissions to:
        "services": ["jupyterhub-idle-culler-service"],
    }
]

c.JupyterHub.services = [
    {
        "name": "jupyterhub-idle-culler-service",
        "command": [
            sys.executable,
            "-m", "jupyterhub_idle_culler",
            "--timeout=3600",
        ],
    }
]

# c.JupyterHub.services = [
#     {
#         'name': 'cull_idle',
#         'admin': True,
#         'command': 'python /srv/jupyterhub/cull_idle_servers.py --timeout=3600'.split(),
#     },
# ]

if (
        os.getenv('CLIENT_ID')
        and os.getenv('CLIENT_SECRET')
):
    c.JupyterHub.authenticator_class = GenericOAuthenticator
    c.JupyterHub.authenticator_class.login_service = 'Jaguar in the Jupyter'
    c.JupyterHub.authenticator_class.create_system_users = True
    c.JupyterHub.authenticator_class.hosted_domain = os.getenv('HOSTED_DOMAINS').split(',')

    c.JupyterHub.authenticator_class.client_id = os.getenv('CLIENT_ID')
    c.JupyterHub.authenticator_class.client_secret = os.getenv('CLIENT_SECRET')

    c.JupyterHub.authenticator_class.oauth_callback_url = os.getenv('REDIRECT_URL')
    c.JupyterHub.authenticator_class.authorize_url = os.getenv('AUTHORIZE_URL')
    c.JupyterHub.authenticator_class.token_url = os.getenv('TOKEN_URL')
    c.JupyterHub.authenticator_class.userdata_url = os.getenv('USERDATA_URL')
    c.JupyterHub.authenticator_class.username_claim = os.getenv('USERNAME_CLAIM')
    c.JupyterHub.authenticator_class.scope = os.getenv('SCOPE').split(',')

    c.Authenticator.add_user_cmd = ['adduser', '-q', '--gecos', '""', '--disabled-password', '--force-badname']
    c.Authenticator.whitelist = set(os.getenv('AUTHORIZED_USERS').split(','))
    c.Authenticator.admin_users = set(os.getenv('ADMIN_USERS').split(','))

elif (
        os.getenv('GOOGLE_CLIENT_ID')
        and os.getenv('GOOGLE_SECRET')
):
    c.JupyterHub.authenticator_class = LocalGoogleOAuthenticator
    c.JupyterHub.authenticator_class.login_service = 'Jaguar in the Jupyter'
    c.JupyterHub.authenticator_class.create_system_users = True
    c.JupyterHub.authenticator_class.hosted_domain = os.getenv('HOSTED_DOMAINS').split(',')

    c.LocalGoogleOAuthenticator.create_system_users = True
    c.LocalGoogleOAuthenticator.hosted_domain = ['jupyter.jaguarintheloop.live', 'gmail.com']
    c.LocalGoogleOAuthenticator.login_service = 'Jaguar in the Jupyter'

    c.LocalGoogleOAuthenticator.oauth_callback_url = os.getenv('GOOGLE_OAUTH_CALLBACK')
    c.LocalGoogleOAuthenticator.client_id = os.getenv('GOOGLE_CLIENT_ID')
    c.LocalGoogleOAuthenticator.client_secret = os.getenv('GOOGLE_SECRET')

    c.Authenticator.add_user_cmd = ['adduser', '-q', '--gecos', '""', '--disabled-password', '--force-badname']
    c.Authenticator.whitelist = set(os.getenv('AUTHORIZED_USERS').split(','))
    c.Authenticator.admin_users = set(os.getenv('ADMIN_USERS').split(','))


else:
    # Admin users
    c.Authenticator.admin_users = set(os.getenv('ADMIN_USERS').split(','))


notebook_dir = '/home/jovyan'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {
    f'{os.getenv("USER_BASE_DIR")}-{{username}}': "/home/jovyan/work",
    os.getenv('SHARED_DIR'): "/home/jovyan/public",
}

c.DockerSpawner.environment = {
    'PYTHONUSERBASE': '/home/jovyan/python_lib',
}

def pre_spawn_hook(spawner):
    username = spawner.user.name

# c.Spawner.pre_spawn_hook = pre_spawn_hook
