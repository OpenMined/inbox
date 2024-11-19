import shutil
from pathlib import Path
from syftbox.lib import Client

client = Client.load()
current_dir = Path(__file__).parent


def is_valid_api_request(path: Path) -> bool:
    return path.is_dir() and (path / "run.sh").exists()


valid_api_requests = [d for d in current_dir.iterdir() if is_valid_api_request(d)]


def main():
    if len(valid_api_requests) == 0:
        print(
            f"No new API requests to broadcast. Please drop your API request folder to {current_dir.absolute()}/."
        )
        return

    datasites_with_inbox = [
        d
        for d in client.datasites.iterdir()
        if (d / "inbox").exists() and d != client.my_datasite
    ]

    if len(datasites_with_inbox) == 0:
        print("No datasites with an inbox found.")
        return

    print(
        f"Found {len(valid_api_requests)} new API requests to broadcast to {len(datasites_with_inbox)} datasites."
    )

    for api_request_path in valid_api_requests:
        for datasite in datasites_with_inbox:
            # Copy the API request to the datasite's inbox/ folder
            target_path = datasite / "inbox" / api_request_path.name
            shutil.copytree(api_request_path, target_path, dirs_exist_ok=True)
            print(f"Broadcasted '{api_request_path.name}' to '{datasite.name}'")
        print(
            f"[Done] '{api_request_path.name}' broadcasted to {len(datasites_with_inbox)} datasites."
            " Removing it from the broadcast folder..."
        )
        # Remove the API request from the broadcast folder
        shutil.rmtree(api_request_path)


main()
