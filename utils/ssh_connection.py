from os import getenv, path
from paramiko import SSHClient, AutoAddPolicy, RSAKey


CONNECTION_TIMEOUT = float(getenv("SSH_TIMEOUT", 10))  
HOSTNAME = getenv("SSH_HOSTNAME", "localhost")
PASSWORD = getenv("SSH_PASSWORD", None)
PORT = int(getenv("SSH_PORT", 22))
PRIVATE_KEY_PASSPHRASE = getenv("SSH_PRIVATE_KEY_PASSPHRASE", None)
PRIVATE_KEY_PATH = path.expanduser(getenv("SSH_PRIVATE_KEY_PATH", "~/.ssh/id_rsa"))
USERNAME = getenv("SSH_USERNAME", "root")

def getSSHConnection() -> SSHClient:
    """Establishes an SSH connection using Paramiko."""
    try:
        key = RSAKey.from_private_key_file(PRIVATE_KEY_PATH)
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(
            hostname=HOSTNAME,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            pkey=key,
            passphrase=PRIVATE_KEY_PASSPHRASE,
            timeout=CONNECTION_TIMEOUT,
        )
        print(f"[INFO] Connected to {USERNAME}@{HOSTNAME} via SSH.")
        return ssh
    except Exception as e:
        print(f"[WARNING] Connection to {USERNAME}@{HOSTNAME} failed: {e}")
        return False
