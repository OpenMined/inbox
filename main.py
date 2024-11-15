from constants import BROADCAST_ENABLED
from pathlib import Path
from syftbox.lib import Client, SyftPermission
from utils import compile_broadcast_app
from utils import create_symlink
from utils import start_broadcast_service
from utils import start_garbage_collector
from utils import start_notification_service

client = Client.load()

my_inbox_path = client.my_datasite / "inbox/"
my_apps_path = client.workspace.apps
api_data_path = client.api_data("inbox")
trash_path = api_data_path / ".trash"

approved_symlink_path = my_inbox_path / "approved"
rejected_symplink_path = my_inbox_path / "rejected"

# Create the necessary directories
client.makedirs(my_inbox_path, trash_path)

# Make the inbox path globally writeable
permission = SyftPermission.mine_with_public_write(email=client.email)
permission.ensure(path=my_inbox_path)

# Create a symlink called "approved" in inbox, pointing to the apps folder
create_symlink(my_apps_path, approved_symlink_path, overwrite=True)

# Create a symlink called "rejected" in inbox, pointing to the trash folder
create_symlink(trash_path, rejected_symplink_path, overwrite=True)

start_notification_service(my_inbox_path, api_data_path)
start_garbage_collector(trash_path, rejected_symplink_path)

if BROADCAST_ENABLED:
    broadcast_dir_path = api_data_path / ".broadcast"
    broadcast_app_path = client.workspace.apps / "broadcast.app"
    app_icon = Path.cwd() / "assets" / "icon.icns"

    # Create the broadcast app at broadcast_dir_path
    client.makedirs(broadcast_dir_path)

    # Compile and add the broadcast app
    if not broadcast_app_path.exists():
        compile_broadcast_app(
            broadcast_app_path,
            my_apps_path,
            client.datasites.absolute(),
            broadcast_dir_path.absolute(),
            app_icon.absolute(),
        )

    start_broadcast_service(
        broadcast_dir_path,
        broadcast_app_path,
        client.datasites,
        client.my_datasite,
    )
