from constants import TRASH_RETENTION_DAYS
from datetime import datetime
from datetime import timedelta
import json
import os
from pathlib import Path
import shutil


def human_friendly_join(
    items: list[str], sep: str = ", ", last_sep: str = " and "
) -> str:
    """Joins a list of strings into a single string with specified separators.

    This function concatenates the elements of a list into a single string.
    Elements are separated by `sep`, except for the last two elements which
    are separated by `last_sep`.

    Parameters
    ----------
    items : list[str]
        The list of strings to join.
    sep : str, optional
        The separator between all elements except the last two, by default ", "
    last_sep : str, optional
        The separator between the last two elements, by default " and "

    Returns
    -------
    str
        The concatenated string.

    Examples
    --------
    >>> human_friendly_join(["apple", "banana", "cherry"])
    'apple, banana and cherry'
    >>> human_friendly_join(["red", "yellow", "green]), sep="; ", last_sep=" or ")
    'red; yellow or green'
    >>> human_friendly_join(["one"])
    'one'
    >>> human_friendly_join([])
    ''
    """
    if not items:
        return ""
    elif len(items) == 1:
        return items[0]
    else:
        return sep.join(items[:-1]) + last_sep + items[-1]


def create_symlink(target_path: Path, symlink_path: Path, overwrite=False) -> None:
    if overwrite and symlink_path.exists():
        if os.path.islink(symlink_path):
            os.unlink(symlink_path)
        else:
            shutil.rmtree(symlink_path)
    symlink_path.symlink_to(target_path)


def is_app(path: Path) -> bool:
    return path.is_dir() and "run.sh" in [f.name for f in path.iterdir()]


def create_api_request_notifications(*api_requests: Path, inbox_path: Path) -> None:
    if len(api_requests) == 0:
        return

    for api_request in api_requests:
        title = "New API Request"
        message = (
            f"A new API request has been received: '{api_request}'."
            " Please review the code and move it to the 'approved' or 'rejected' folder."
        )
        os.system(
            "./terminal-notifier.app/Contents/MacOS/terminal-notifier"
            f" -title '{title}'"
            f" -subtitle '{api_request}'"
            f" -message '{message}'"
            f" -contentImage './icon.png'"
            f" -open file://{inbox_path.absolute()}"
            " -ignoreDnd"
        )


def get_pending_api_requests(inbox_path: Path) -> list:
    ignore = [".DS_Store", "rejected", "_.syftperm", "approved"]
    pending_api_requests = [
        d.name for d in inbox_path.iterdir() if d.name not in ignore and is_app(d)
    ]
    return pending_api_requests


def load_inbox_state(appdata_path: Path) -> dict:
    state_json_path = appdata_path / "state.json"
    if state_json_path.exists():
        with open(state_json_path, "r") as f:
            return json.load(f)
    return {"pending_api_requests": []}


def save_inbox_state(inbox_path: Path, appdata_path: Path) -> None:
    state_json_path = appdata_path / "state.json"
    print(f"Writing to {state_json_path}")

    state = {"pending_api_requests": get_pending_api_requests(inbox_path)}

    state_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_json_path, "w") as f:
        json.dump(state, f)


def start_notification_service(inbox_path: Path, appdata_path: Path) -> None:
    print(f"Watching {inbox_path} for new API requests...")

    previous_pending_api_requests = load_inbox_state(appdata_path)[
        "pending_api_requests"
    ]
    current_pending_api_requests = get_pending_api_requests(inbox_path)
    if previous_pending_api_requests != current_pending_api_requests:
        new_api_requests = sorted(
            set(current_pending_api_requests) - set(previous_pending_api_requests)
        )
        if len(new_api_requests) > 0:
            print(f"New API requests received: {human_friendly_join(new_api_requests)}")
        save_inbox_state(inbox_path, appdata_path)
        create_api_request_notifications(*new_api_requests, inbox_path=inbox_path)


def start_garbage_collector(trash_path: Path, trash_symlink_path: Path) -> None:
    print(f"Watching {trash_symlink_path} for rejected API requests...")
    if not trash_path.exists():
        return
    seven_days_ago = datetime.now() - timedelta(days=TRASH_RETENTION_DAYS)
    apps_to_delete = sorted(
        [
            d
            for d in trash_path.iterdir()
            if is_app(d) and d.stat().st_ctime < seven_days_ago.timestamp()
        ],
        key=lambda d: d.name,
    )

    if len(apps_to_delete) > 0:
        name_of_apps_to_delete = human_friendly_join([d.name for d in apps_to_delete])
        print(
            f"Found {len(apps_to_delete)} rejected API requests older than {TRASH_RETENTION_DAYS} days:"
            f" {name_of_apps_to_delete}. Deleting..."
        )

    for item in apps_to_delete:
        if os.path.islink(item):
            os.unlink(item)
        elif item.is_dir():
            shutil.rmtree(str(item.absolute()))
        else:
            os.remove(item)


def compile_broadcast_app(
    output_path: Path, datasite_path: Path, broadcast_dir_path: Path, icon_path: Path
) -> None:
    script_template_path = Path(__file__).parent / "broadcast.scpt.template"
    with open(script_template_path, "r") as f:
        apple_script = f.read()
    apple_script = apple_script.replace("{{DATASITE_PATH}}", str(datasite_path))
    apple_script = apple_script.replace(
        "{{BROADCAST_DIR_PATH}}", str(broadcast_dir_path)
    )

    with open("broadcast.scpt", "w") as f:
        f.write(apple_script)

    compile_command = (
        f"osacompile -o {output_path} broadcast.scpt > /dev/null 2>&1"
        f' && echo "Broadcast app compiled to {output_path}"'
        f' || echo "Failed to compile broadcast app to {output_path}" >&2'
    )
    os.system(compile_command)
    os.remove("broadcast.scpt")
    os.system(f"cp {icon_path} {output_path/'Contents/Resources/droplet.icns'}")
    (output_path / "run.sh").touch()


def start_broadcast_service(
    broadcast_dir_path: Path,
    broadcast_app_path: Path,
    datasites_path: Path,
    my_datasite_path: Path,
) -> None:
    valid_api_requests = [d for d in broadcast_dir_path.iterdir() if is_app(d)]

    if len(valid_api_requests) == 0:
        print(
            f"No new API requests to broadcast. Please drop your API request folder to {broadcast_app_path}."
        )
        return

    datasites_with_inbox = [
        d
        for d in datasites_path.iterdir()
        if (d / "inbox").exists() and d != my_datasite_path
    ]
    if len(datasites_with_inbox) == 0:
        print("No datasites with an inbox found.")
        return

    print(
        f"Found {len(valid_api_requests)} new API requests to broadcast to {len(datasites_with_inbox)} datasites."
    )

    for api_request in valid_api_requests:
        for datasite in datasites_with_inbox:
            # Copy the api_request to the datasite's inbox
            target_path = datasite / "inbox" / api_request.name
            shutil.copytree(api_request, target_path, dirs_exist_ok=True)
            print(f"Broadcasted '{api_request.name}' to '{datasite.name}'")
        # Remove the api_request from the broadcast folder
        shutil.rmtree(api_request)
