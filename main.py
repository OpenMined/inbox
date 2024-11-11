import os

from syftbox.lib import Client, SyftPermission

client_config = Client.load()

inbox_path = client_config.datasites / client_config.email / "public/inbox/"
apps_path = client_config.workspace.apps

# Create the inbox folder
inbox_path.mkdir(parents=True, exist_ok=True)

# Make it globally writeable
permission = SyftPermission.mine_with_public_write(email=client_config.email)
permission.ensure(path=inbox_path)

# Create a symlink called "approved" pointing to the apps folder, overwriting it if it already exists
symlink_path = inbox_path / "approved"
if not symlink_path.exists() or not os.path.islink(symlink_path):
    if symlink_path.exists():
        os.unlink(symlink_path)
    symlink_path.symlink_to(apps_path)
