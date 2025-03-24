from os import getenv, path
from paramiko import SSHClient, AutoAddPolicy, RSAKey


def getSSHConnection(
    hostname: str = "localhost",
    port: int = 22,
    username: str = "root",
    private_key_path: str = "~/.ssh/id_rsa"
) -> SSHClient:
    """Establishes an SSH connection using Paramiko."""
    hostname = getenv("SSH_HOSTNAME", hostname)
    port = int(getenv("SSH_PORT", port))
    username = getenv("SSH_USERNAME", username)
    private_key_path = path.expanduser(getenv("SSH_PRIVATE_KEY_PATH", private_key_path))
    try:
        key = RSAKey.from_private_key_file(private_key_path)
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            pkey=key
        )
        print(f"[INFO] Connected to {username}@{hostname} via SSH.")
        return ssh
    except Exception as e:
        print(f"[WARNING] Connection to {username}@{hostname} failed: {e}")
        return False
