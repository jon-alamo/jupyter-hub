FROM jupyterhub/jupyterhub:latest

## Copy the JupyterHub configuration in the container
COPY jupyterhub_config.py .

## Install dependencies (for advanced authentication and spawning)
RUN pip install dockerspawner oauthenticator jupyterhub-idle-culler

## Local admin user
RUN useradd --create-home --shell /bin/bash joni -p "$(openssl passwd -1 mysecret12345!)"
