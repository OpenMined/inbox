import shutil
from pathlib import Path
from syftbox.lib import Client

client = Client.load()
current_dir = Path(__file__).parent


def is_valid_api_request(path: Path) -> bool:
    return path.is_dir() and (path / "run.sh").exists()


def get_ignored_path_patterns(api_request_path: Path) -> list:
    patterns = [
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "*.pyc",
        ".git",
    ]
    gitignore_path = api_request_path / ".gitignore"
    if gitignore_path.exists():
        patterns.extend(
            line.strip()
            for line in gitignore_path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        )
    return patterns


def main():
    valid_api_requests = [d for d in current_dir.iterdir() if is_valid_api_request(d)]

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
            try:
                # Copy the API request to the datasite's inbox/ folder
                target_path = datasite / "inbox" / api_request_path.name

                shutil.copytree(
                    api_request_path,
                    target_path,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(
                        *get_ignored_path_patterns(api_request_path)
                    ),
                )
                print(f"Broadcasted '{api_request_path.name}' to '{datasite.name}'")
            except Exception as e:
                print(
                    f"Failed to broadcast '{api_request_path.name}' to '{datasite.name}': {e}"
                )
        print(
            f"[Done] '{api_request_path.name}' broadcasted to {len(datasites_with_inbox)} datasites."
            " Removing it from the broadcast folder..."
        )
        # Remove the API request from the broadcast folder
        shutil.rmtree(api_request_path)


if __name__ == "__main__":
    main()
