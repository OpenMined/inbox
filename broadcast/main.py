import shutil
import logging
from pathlib import Path
from syft_core import Client
from emails import EmailService


# Set up SyftBox client
client = Client.load()
current_dir = Path(__file__).parent
api_name = client.api_request_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"{api_name}:{Path(__file__).name}")

# Constants
IGNORED_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "*.pyc",
    ".git",
]


def is_valid_api_request(path: Path) -> bool:
    return path.is_dir() and (path / "run.sh").exists()


def get_ignored_path_patterns(api_request_path: Path) -> list[str]:
    patterns = IGNORED_PATTERNS.copy()
    gitignore_path = api_request_path / ".gitignore"
    try:
        if gitignore_path.exists():
            patterns.extend(
                line.strip()
                for line in gitignore_path.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            )
    except Exception as e:
        logger.warning(f"Failed to read .gitignore: {str(e)}")
    return patterns


def broadcast_api_requests() -> None:
    try:
        valid_api_requests = [
            d for d in current_dir.iterdir() if is_valid_api_request(d)
        ]

        if not valid_api_requests:
            logger.info(
                f"No new API requests to broadcast. Drop your API request folder to {current_dir.absolute()}/."
            )
            return

        datasites_with_inbox = [
            d
            for d in client.datasites.iterdir()
            if (d / "inbox").exists() and d != client.my_datasite
        ]

        if len(datasites_with_inbox) == 0:
            logger.info("No datasites with an inbox found.")
            return

        logger.info(
            f"Found {len(valid_api_requests)} new API requests to broadcast to {len(datasites_with_inbox)} datasites."
        )

        for api_request_path in valid_api_requests:
            successful_broadcasts = 0
            for datasite in datasites_with_inbox:
                try:
                    target_path = datasite / "inbox" / api_request_path.name
                    shutil.copytree(
                        api_request_path,
                        target_path,
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(
                            *get_ignored_path_patterns(api_request_path)
                        ),
                    )
                    successful_broadcasts += 1
                    logger.info(
                        f"Broadcasted '{api_request_path.name}' to '{datasite.name}'"
                    )
                    EmailService.add_to_email_queue(
                        datasite.name, api_request_path.name, client.my_datasite.name
                    )
                except Exception as e:
                    logger.error(f"Failed to broadcast to '{datasite.name}': {str(e)}")

            if successful_broadcasts > 0:
                logger.info(
                    f"'{api_request_path.name}' broadcasted to {successful_broadcasts} datasites. Cleaning up..."
                )
                shutil.rmtree(api_request_path)
            else:
                logger.error(
                    f"Failed to broadcast '{api_request_path.name}' to any datasite"
                )

    except Exception as e:
        logger.error(f"Broadcasting failed: {str(e)}")


def main():
    broadcast_api_requests()
    EmailService.process_email_queue()


if __name__ == "__main__":
    main()
