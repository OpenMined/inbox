# Inbox API

The Inbox API is a component of the SyftBox ecosystem designed to send and receive API requests between datasites. This app is compatible with MacOS and Linux.

## Features

* Receive and process API requests from others.
* Send API requests to any datasite.
* Broadcast API requests to all datasites.
* Send email and desktop notifications for new API requests.

## Usage

### What is an API?

An API is any folder containing a `run.sh` entry script.

### Sending API Requests

You can share your API with datasites in two ways:

1. **Send to a Single Datasite**
   Copy your API folder into the target datasite's `inbox/` directory.

2. **Broadcast to All Datasites**
   Place your API folder in the `/SyftBox/apis/broadcast/` directory.
   The system will:
   * Validate your API.
   * Send it to all datasites with the Inbox API installed.

After an API is sent, datasite owners will receive notifications (desktop and email). They can then review the code of your API request and choose to **approve** or **reject** it. Approved requests execute automatically if the recipient's SyftBox client is active.

### Managing Incoming API Requests

Incoming API requests appear in your datasite’s `inbox/` folder. Here’s how to handle them:

1. **Folder Structure**
   The `inbox/` folder contains two symlinked subfolders:
   * `approved`: Links to `/SyftBox/apis/`, where approved APIs are start executing automatically.
   * `rejected`: Serves as a temporary bin. Rejected APIs remain here for 7 days before being deleted.

2. **Review Process**
   * Inspect the code of new API requests in the `inbox/` folder.
   * After reviewing, move the API folder to either `approved` or `rejected`.

### Uninstalling the Inbox API

The Inbox API is an API in itself and can be uninstalled if needed. To uninstall, simply delete the `/SyftBox/apis/inbox/` directory along with its contents.
