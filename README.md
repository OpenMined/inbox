# Inbox API

The Inbox API is a component for the SyftBox ecosystem designed to send and receive API requests among datasites. The app is compatible with MacOS and Linux.

## Key Features

- Receive and process API requests from others.
- Send API requests to any datasite.
- Broadcast API requests to all datasites.
- Send email and desktop notifications for new API requests.

## Usage

### What constitutes an API?

Any folder containing the `run.sh` entry script is a valid API.

### Sending an API request

To invite datasites to be part of a computation, you need to send your API through the network. This can be done by

1. Manually sending your API to a single datasite.

   This is done by simply copy-pasting your API to the target datasite's `inbox/` folder.

3. Broadcasting your API to all the datasites in the network.

   This is done by copy-pasting your API to `/SyftBox/apis/broadcast/` folder. The system will automatically validate the API and send it to all the datasites that have the **Inbox API** installed.

Once received, the datasite's owner(s) will get a desktop notification and an email on their end. They'll then review the code of your API request, and either **approve** or **reject** it. Your API request starts executing once they approve, given that their syftbox client is running.

#### Accepting/Rejecting an API Request

1. Your datasite's `inbox/` folder comes with two folder symlinks by default: `approved` and a `rejected`.
   - The approved folder is a link to `/SyftBox/apis/` folder, and any valid API present in this folder gets picked up and executed by the SyftBox client.
   - The rejected folder is like a trash bin, where files are stored for 7 days and then purged from the system.
2. Any new API request shows up in the `inbox/` folder, adjacent to the `approved` and `rejected` folders.
3. **Review the API Request**: Check your `inbox` folder for new API requests and thoroughly review it's code.
4. **Take an action**: After review, move the API request folder to either the `approved` or `rejected` folder, as applicable.

#### Uninstalling the Inbox API

The Inbox API is an API in itself and can be uninstalled if needed. To uninstall, simply remove the `/SyftBox/apis/inbox/` directory and its contents.
