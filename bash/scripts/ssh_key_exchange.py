import os
import platform
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, check=True, capture_output=False, input_text=None):
    try:
        result = subprocess.run(
            command, shell=True, check=check,
            input=input_text, capture_output=capture_output, text=True
        )
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        sys.exit(1)

def generate_ssh_key(private_key):
    print("🔧 Generating SSH key...")
    ssh_dir = private_key.parent
    ssh_dir.mkdir(parents=True, exist_ok=True)
    run_command(f'ssh-keygen -t rsa -b 4096 -f "{private_key}" -N ""')

def check_key_auth(remote_user, remote_host):
    try:
        run_command(
            f'ssh -o BatchMode=yes -o ConnectTimeout=5 -o PasswordAuthentication=no {remote_user}@{remote_host} "echo success"',
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def push_key(remote_user, remote_host, public_key):
    print("📤 Pushing public key to remote host...")
    if shutil.which("ssh-copy-id"):
        run_command(f'ssh-copy-id {remote_user}@{remote_host}')
    else:
        print("🪛 ssh-copy-id not available, using manual method...")
        pubkey_content = public_key.read_text().strip()
        cmd = (
            f'ssh {remote_user}@{remote_host} '
            f'"mkdir -p ~/.ssh && echo \'{pubkey_content}\' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"'
        )
        run_command(cmd)

def copy_path_to_clipboard(path):
    path_str = str(path)
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run('clip', text=True, input=path_str, check=True)
        elif system == "Darwin":
            subprocess.run('pbcopy', text=True, input=path_str, check=True)
        elif shutil.which("xclip"):
            subprocess.run('xclip -selection clipboard', shell=True, input=path_str, text=True, check=True)
        elif shutil.which("xsel"):
            subprocess.run('xsel --clipboard --input', shell=True, input=path_str, text=True, check=True)
        else:
            print("⚠️ Clipboard tool not found (install xclip or xsel on Linux).")
            return
        print(f"📋 Private key path copied to clipboard: {path_str}")
    except Exception as e:
        print(f"⚠️ Could not copy to clipboard: {e}")

def main():
    remote_user = input("🧑 Remote username: ").strip()
    remote_host = input("🌐 Remote host (e.g. 192.168.1.10): ").strip()

    ssh_dir = Path.home() / ".ssh"
    private_key = ssh_dir / "id_rsa"
    public_key = ssh_dir / "id_rsa.pub"

    # Generate key if missing
    if not private_key.exists() or not public_key.exists():
        generate_ssh_key(private_key)

    # Check if key-based auth works
    if check_key_auth(remote_user, remote_host):
        print("✅ Key-based auth already working.")
    else:
        push_key(remote_user, remote_host, public_key)
        if check_key_auth(remote_user, remote_host):
            print("🔐 Key installed successfully.")
        else:
            print("⚠️ Still can't connect with key auth.")

    # Copy private key path to clipboard
    copy_path_to_clipboard(private_key)

    # SSH in
    print("🚀 Connecting to remote host...")
    run_command(f'ssh {remote_user}@{remote_host}', check=False)

if __name__ == "__main__":
    main()
