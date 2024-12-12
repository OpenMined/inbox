import shutil
from pathlib import Path

from syftbox.lib import Client, SyftPermission

from constants import BROADCAST_ENABLED
from utils import create_symlink, start_garbage_collector, start_notification_service

client = Client.load()

my_inbox_path = client.my_datasite / "inbox"
my_apps_path = client.workspace.apps
api_data_path = client.api_data("inbox")
trash_path = api_data_path / ".trash"

approved_symlink_path = my_inbox_path / "approved"
rejected_symplink_path = my_inbox_path / "rejected"

# Create the necessary directories
client.makedirs(my_inbox_path, trash_path)

# Make the inbox path globally writeable
permission = SyftPermission.mine_with_public_write(
    email=client.email,
    filepath=my_inbox_path.relative_to(client.workspace.datasites),
)
permission.ensure(path=my_inbox_path)

# Create a symlink called "approved" in inbox, pointing to the apps folder
create_symlink(my_apps_path, approved_symlink_path, overwrite=True)

# Create a symlink called "rejected" in inbox, pointing to the trash folder
create_symlink(trash_path, rejected_symplink_path, overwrite=True)

start_notification_service(my_inbox_path, api_data_path)
start_garbage_collector(trash_path, rejected_symplink_path)

if BROADCAST_ENABLED:
    try:
        broadcast_app_src = Path(__file__).parent / "broadcast"
        broadcast_app_dst = my_apps_path / "broadcast"

        # Ensure source directory exists
        if not broadcast_app_src.exists():
            raise FileNotFoundError(
                f"Broadcast source directory not found: {broadcast_app_src}"
            )

        # Compare versions only if both files exist
        needs_update = True
        if broadcast_app_dst.exists():
            try:
                src_version = (broadcast_app_src / "version").read_text().strip()
                dst_version = (broadcast_app_dst / "version").read_text().strip()
                needs_update = src_version != dst_version
            except (FileNotFoundError, IOError) as e:
                print(f"Warning: Broadcast app version check failed - {e}")

        if needs_update:
            print("Updating broadcast app")
            shutil.copytree(
                broadcast_app_src,
                broadcast_app_dst,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    ".pytest_cache",
                    ".venv",
                    "*.pyc",
                    ".git",
                ),
            )
            print("Broadcast app updated successfully")

    except Exception as e:
        print(f"Error updating broadcast app: {e}")
