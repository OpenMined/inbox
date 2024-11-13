from syftbox.lib import Client, SyftPermission
from utils import create_symlink
from utils import start_notification_service

client_config = Client.load()

my_inbox_path = client_config.my_datasite / "public/inbox/"
my_apps_path = client_config.workspace.apps
appdata_path = client_config.appdata("inbox")
trash_path = appdata_path / ".trash"

approved_symlink_path = my_inbox_path / "approved"
rejected_symplink_path = my_inbox_path / "rejected"

# Create the necessary directories
client_config.makedirs(my_inbox_path, trash_path)

# Make the inbox path globally writeable
permission = SyftPermission.mine_with_public_write(email=client_config.email)
permission.ensure(path=my_inbox_path)

# Create a symlink called "approved" pointing to the apps folder
create_symlink(my_apps_path, approved_symlink_path, overwrite=True)

# Create a symlink called "rejected" pointing to the trash folder
create_symlink(trash_path, rejected_symplink_path, overwrite=True)

# TODO periodically clean trash directory

start_notification_service(my_inbox_path, appdata_path)
