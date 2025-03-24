from os import path, getenv
import re
from scp import SCPClient
from threading import Thread


def check_remote_directory(ssh, remote_path: str = "~/recordings") -> bool:
    """Check if a remote directory exists, and create it if it doesn't."""
    remote_path = getenv("REMOTE_WRITE_DIR", remote_path)
    try:
        stdin, stdout, stderr = ssh.exec_command(f"ls {remote_path}")
        if not stdout.read().decode().strip():
            print(f"[INFO] Creating directory {remote_path} on Raspberry Pi.")
            ssh.exec_command(f"mkdir -p {remote_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to check/create remote directory: {e}")
        return False


def async_upload(
    scp_client: SCPClient,
    local_path: str,
    remote_dir: str = "~/recordings"
) -> None:
    """Uploads a file asynchronously to the Raspberry Pi."""
    remote_dir = getenv("REMOTE_WRITE_DIR", remote_dir)
    remote_file_path = path.join(remote_dir, path.basename(local_path)).replace("\\", "/")
    
    def upload():
        try:
            print(f"[INFO] Uploading {local_path} to {remote_dir}...")
            scp_client.put(local_path, remote_path=remote_file_path)
            print(f"[INFO] Video uploaded to Raspberry Pi: {remote_file_path}")
        except FileNotFoundError:
            print(f"[ERROR] File not found: {local_path}. Check if the file exists.")
        except PermissionError:
            print(f"[ERROR] Permission denied: {local_path}. Check your permissions.")
        except re.error:
            print(f"[ERROR] Invalid regex pattern in {local_path}. Check your regex.")
        except TimeoutError:
            print(f"[ERROR] Timeout error while uploading {local_path}. Check your connection.")
        except ConnectionError:
            print(f"[ERROR] Connection error while uploading {local_path}. Check your connection.")
        except Exception as e:
            print(f"[ERROR] Failed to upload {local_path}: {e}")
    
    upload_thread = Thread(target=upload)
    upload_thread.start()
    