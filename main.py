from syftbox.lib import Client
from syftbox.lib import SyftPermission

client_config = Client.load()

inbox_path = client_config.datasites / client_config.email / "public/inbox/"
apps_path = client_config.workspace.apps

# Create the inbox folder
inbox_path.mkdir(parents=True, exist_ok=True)

# Make it globally writeable
permission = SyftPermission.mine_with_public_write(email=client_config.email)
permission.save(path=inbox_path)

# Create a symlink called "approved" pointing to the apps folder
apps_path.symlink_to(inbox_path / "approved")
