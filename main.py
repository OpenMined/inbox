from constants import BROADCAST_ENABLED
from pathlib import Path
from syftbox.lib import Client, SyftPermission
from utils import compile_broadcast_app
from utils import create_symlink
from utils import start_broadcast_service
from utils import start_garbage_collector
from utils import start_notification_service

client_config = Client.load()

my_inbox_path = client_config.my_datasite / "inbox/"
my_apps_path = client_config.workspace.apps
appdata_path = client_config.api_data("inbox")
trash_path = appdata_path / ".trash"

approved_symlink_path = my_inbox_path / "approved"
rejected_symplink_path = my_inbox_path / "rejected"

# Create the necessary directories
client_config.makedirs(my_inbox_path, trash_path)

# Make the inbox path globally writeable
permission = SyftPermission.mine_with_public_write(email=client_config.email)
permission.ensure(path=my_inbox_path)

# Create a symlink called "approved" in inbox, pointing to the apps folder
create_symlink(my_apps_path, approved_symlink_path, overwrite=True)

# Create a symlink called "rejected" in inbox, pointing to the trash folder
create_symlink(trash_path, rejected_symplink_path, overwrite=True)

start_notification_service(my_inbox_path, appdata_path)
start_garbage_collector(trash_path, rejected_symplink_path)

if BROADCAST_ENABLED:
    broadcast_dir_path = appdata_path / ".broadcast"
    broadcast_app_path = client_config.workspace.apps / "broadcast.app"
    app_icon = Path.cwd() / "icon.icns"

    # Create the broadcast app at broadcast_dir_path
    client_config.makedirs(broadcast_dir_path)

    # Compile and add the broadcast app
    if not broadcast_app_path.exists():
        compile_broadcast_app(
            broadcast_app_path,
            my_apps_path,
            client_config.datasites.absolute(),
            broadcast_dir_path.absolute(),
            app_icon.absolute(),
        )

    start_broadcast_service(
        broadcast_dir_path,
        broadcast_app_path,
        client_config.datasites,
        client_config.my_datasite,
    )
