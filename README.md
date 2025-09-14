# AI News Bot

This project is a stateless MCP server that provides tools for fetching Cisco news and interacting with Webex. It can be used as a backend for an AI agent that needs to perform these actions.

## Features

*   **Get Cisco News:** Fetches recent news articles related to Cisco from the last 7 days via a Google News RSS feed.
*   **Send Webex Message:** Sends a text or markdown message to a Webex user via their email address.
*   **Send Webex News Card:** Sends a pre-formatted news bulletin as an Adaptive Card to a Webex user.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ai-news-bot
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -e .
    ```

## Configuration

This project uses a `.env` file for environment variables. Create a file named `.env` in the root of the project and add the following:

```
WEBEX_ACCESS_TOKEN=<your-webex-access-token>
```

Replace `<your-webex-access-token>` with your actual Webex access token.

## Usage

To run the server, use the following command:

```bash
python mcp_server.py
```

The server will start on `http://127.0.0.1:3000` by default. You can change the host and port using the `--host` and `--port` options.
