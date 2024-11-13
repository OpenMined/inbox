import json
import os
import shutil
from pathlib import Path


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
    elif len(api_requests) == 1:
        title = "New API Request"
        subtitle = api_requests[0]
        message = (
            f"A new API request has been received: '{api_requests[0]}'."
            " Please review it and move it to the 'approved' or 'rejected' folder."
        )
    elif len(api_requests) > 1:
        title = "Multiple New API Requests"
        subtitle = f"{api_requests[0]} and {len(api_requests) - 1} more..."
        message = (
            f"You have received {len(api_requests)} new API requests. Please review"
            " them and move each to the 'approved' or 'rejected' folder."
        )
    # os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
    os.system(
        "./terminal-notifier.app/Contents/MacOS/terminal-notifier"
        f" -title '{title}'"
        f" -subtitle '{subtitle}'"
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
    print(f"Watching {inbox_path} for new apps...")

    previous_pending_api_requests = load_inbox_state(appdata_path)[
        "pending_api_requests"
    ]
    current_pending_api_requests = get_pending_api_requests(inbox_path)
    if previous_pending_api_requests != current_pending_api_requests:
        new_api_requests = sorted(
            set(current_pending_api_requests) - set(previous_pending_api_requests)
        )
        if len(new_api_requests) > 0:
            print(f"New API requests: {", ".join(new_api_requests)}")
        save_inbox_state(inbox_path, appdata_path)
        create_api_request_notifications(*new_api_requests, inbox_path=inbox_path)


def start_garbage_collector(trash_path: Path) -> None:
    print(f"Watching {trash_path} for rejected api requests...")
    if not trash_path.exists():
        return
    rejected_apps_list = sorted(
        [d for d in trash_path.iterdir() if is_app(d)], key=lambda d: d.name
    )
    if len(rejected_apps_list) > 0:
        print(
            f"Found {len(rejected_apps_list)} rejected api requests:"
            f" {", ".join([d.name for d in rejected_apps_list])}. Deleting..."
        )
    for item in trash_path.iterdir():
        if os.path.islink(item):
            os.unlink(item)
        elif item.is_dir():
            shutil.rmtree(str(item.absolute()))
        else:
            os.remove(item)
