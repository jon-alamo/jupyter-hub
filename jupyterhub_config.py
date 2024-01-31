import os
import sys
from oauthenticator.google import LocalGoogleOAuthenticator
from oauthenticator.generic import GenericOAuthenticator


env_types= [str | int | float | bool | None]

def parse_bool(value: env_types) -> bool:
    if value.lower() in ('true', 'yes', '1'):
        return True
    return False


def get_env(
        name: str, default: env_types = None, var_type: type = str
) -> env_types:
    if name not in os.environ and default is None:
        raise EnvironmentError('Missing environment variable: ' + name)
    var_type = parse_bool if var_type is bool else var_type
    try:
        return var_type(get_env(name, default=default))
    except ValueError:
        raise EnvironmentError(
            'Invalid value for environment variable: ' + name
        )


c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = get_env('DOCKER_JUPYTER_IMAGE')
c.DockerSpawner.network_name = get_env('DOCKER_NETWORK_NAME')
c.JupyterHub.hub_ip = get_env('HUB_IP')

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
        get_env('CLIENT_ID')
        and get_env('CLIENT_SECRET')
):
    c.JupyterHub.authenticator_class = GenericOAuthenticator
    c.JupyterHub.authenticator_class.login_service = 'Jaguar in the Jupyter'
    c.JupyterHub.authenticator_class.create_system_users = True
    c.JupyterHub.authenticator_class.hosted_domain = get_env('HOSTED_DOMAINS').split(',')

    c.JupyterHub.authenticator_class.client_id = get_env('CLIENT_ID')
    c.JupyterHub.authenticator_class.client_secret = get_env('CLIENT_SECRET')

    c.JupyterHub.authenticator_class.oauth_callback_url = get_env('REDIRECT_URL')
    c.JupyterHub.authenticator_class.authorize_url = get_env('AUTHORIZE_URL')
    c.JupyterHub.authenticator_class.token_url = get_env('TOKEN_URL')
    c.JupyterHub.authenticator_class.userdata_url = get_env('USERDATA_URL')
    c.JupyterHub.authenticator_class.username_claim = get_env('USERNAME_CLAIM')
    c.JupyterHub.authenticator_class.scope = get_env('SCOPE').split(',')

    c.Authenticator.add_user_cmd = ['adduser', '-q', '--gecos', '""', '--disabled-password', '--force-badname']
    c.Authenticator.whitelist = set(get_env('AUTHORIZED_USERS').split(','))
    c.Authenticator.admin_users = set(get_env('ADMIN_USERS').split(','))

elif (
        get_env('GOOGLE_CLIENT_ID')
        and get_env('GOOGLE_SECRET')
):
    c.JupyterHub.authenticator_class = LocalGoogleOAuthenticator
    c.JupyterHub.authenticator_class.login_service = 'Jaguar in the Jupyter'
    c.JupyterHub.authenticator_class.create_system_users = True
    c.JupyterHub.authenticator_class.hosted_domain = get_env('HOSTED_DOMAINS').split(',')

    c.LocalGoogleOAuthenticator.create_system_users = True
    c.LocalGoogleOAuthenticator.hosted_domain = ['jupyter.jaguarintheloop.live', 'gmail.com']
    c.LocalGoogleOAuthenticator.login_service = 'Jaguar in the Jupyter'

    c.LocalGoogleOAuthenticator.oauth_callback_url = get_env('GOOGLE_OAUTH_CALLBACK')
    c.LocalGoogleOAuthenticator.client_id = get_env('GOOGLE_CLIENT_ID')
    c.LocalGoogleOAuthenticator.client_secret = get_env('GOOGLE_SECRET')

    c.Authenticator.add_user_cmd = ['adduser', '-q', '--gecos', '""', '--disabled-password', '--force-badname']
    c.Authenticator.whitelist = set(get_env('AUTHORIZED_USERS').split(','))
    c.Authenticator.admin_users = set(get_env('ADMIN_USERS').split(','))


else:
    # Admin users
    c.Authenticator.admin_users = set(get_env('ADMIN_USERS').split(','))


notebook_dir = '/home/jovyan'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {
    f'{get_env("USER_BASE_DIR")}-{{username}}': "/home/jovyan/work",
    get_env('SHARED_DIR'): "/home/jovyan/public",
}

c.DockerSpawner.environment = {
    'PYTHONUSERBASE': '/home/jovyan/python_lib',
}

def pre_spawn_hook(spawner):
    username = spawner.user.name

# c.Spawner.pre_spawn_hook = pre_spawn_hook
