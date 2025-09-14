"""
A stateless MCP server providing tools for fetching Cisco news and interacting with Webex.
"""

import json
import logging
import os
import sys
from typing import Dict, Any

import click
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from webexteamssdk import WebexTeamsAPI
from webexteamssdk.exceptions import ApiError

# --- Constants ---
CISCO_NEWS_RSS_URL = "https://news.google.com/rss/search?q=intitle:CISCO+when:7d&hl=fr&gl=FR&ceid=FR:fr"

# --- Configuration & Initialization ---
# Load environment variables from a .env file for local development
load_dotenv()

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# --- Helper Functions ---

def get_webex_api_client() -> WebexTeamsAPI | None:
    """
    Retrieves the Webex API access token from environment variables and initializes the API client.

    Returns:
        An initialized WebexTeamsAPI client instance, or None if the token is missing.
    """
    access_token = os.getenv("WEBEX_ACCESS_TOKEN")
    if not access_token:
        logger.error("WEBEX_ACCESS_TOKEN environment variable not set. Webex tools will fail.")
        return None
    return WebexTeamsAPI(access_token=access_token)


def create_adaptive_card_from_template(
    title: str,
    description: str,
    source_link: str,
    source_name: str,
    source_date: str
) -> Dict[str, Any]:
    """
    Loads an Adaptive Card template from a JSON file and populates it with dynamic data.

    Returns:
        A dictionary representing the populated Adaptive Card, or an empty dictionary on error.
    """
    try:
        with open('adaptive_card.json', 'r', encoding='utf-8') as f:
            card_template_str = f.read()

        # Replace placeholders with actual data.
        card_str = card_template_str.replace('${title}', title)
        card_str = card_str.replace('${description}', description)
        card_str = card_str.replace('${source_link}', source_link)
        card_str = card_str.replace('${source_name}', source_name)
        card_str = card_str.replace('${source_date}', source_date)

        return json.loads(card_str)

    except FileNotFoundError:
        logger.error("Critical error: 'adaptive_card.json' template not found.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Critical error: Failed to parse 'adaptive_card.json'. Details: {e}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred in create_adaptive_card_from_template: {e}")
        return {}


# --- CLI Command ---

@click.command()
@click.option(
    "--host",
    default=os.getenv("HOST", "127.0.0.1"),
    help="Server host address.",
    show_default=True,
)
@click.option(
    "--port",
    default=int(os.getenv("PORT", 3000)),
    help="Server port number.",
    show_default=True,
)
@click.option(
    "--log-level",
    default=os.getenv("LOG_LEVEL", "INFO"),
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    help="Set the logging level.",
    show_default=True,
)
def main(host: str, port: int, log_level: str) -> None:
    """Entry point for launching the MCP server with Webex tools."""
    logger.setLevel(log_level.upper())
    logger.info("🚀 Launching MCP Server with Webex Tools...")

    # --- Server and Tool Registration ---
    mcp = FastMCP(
        "Stateless Server with Webex Tools",
        host=host,
        port=port,
        stateless_http=True,
    )

    @mcp.tool(
        title="Get Cisco News (Last 7 Days)",
        description="Fetches recent news articles related to Cisco from the last 7 days via a Google News RSS feed.",
    )
    def get_cisco_last_week_news() -> str:
        """Fetches Cisco news from a Google News RSS feed."""
        try:
            response = requests.get(CISCO_NEWS_RSS_URL, timeout=10)
            response.raise_for_status()
            logger.debug("Successfully fetched Cisco news RSS feed.")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch news feed: {e}")
            return f"An error occurred while fetching the news feed: {e}"

    @mcp.tool(
        title="Send Webex Message",
        description="Sends a text or markdown message to a Webex user via their email address.",
    )
    def send_webex_message(recipient_email: str, message_text: str) -> Dict[str, Any]:
        """Sends a message to a Webex user."""
        api = get_webex_api_client()
        if not api:
            return {"success": False, "error": "Webex API client not configured."}

        try:
            api.messages.create(toPersonEmail=recipient_email, markdown=message_text)
            logger.info(f"Message successfully sent to {recipient_email}.")
            return {"success": True, "status": "Message sent successfully."}
        except ApiError as e:
            logger.error(f"Webex API error while sending message: {e}")
            return {"success": False, "error": f"Webex API error: {e}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending message: {e}")
            return {"success": False, "error": f"An unexpected error occurred: {e}"}

    @mcp.tool(
        title="Send Webex News Card",
        description="Sends a pre-formatted news bulletin as an Adaptive Card to a Webex user.",
    )
    def send_webex_adaptive_card(
        recipient_email: str,
        news_title: str,
        news_description: str,
        source_link: str,
        source_name: str,
        source_date: str,
    ) -> Dict[str, Any]:
        """Sends a Webex Adaptive Card with dynamic news content."""
        api = get_webex_api_client()
        if not api:
            return {"success": False, "error": "Webex API client not configured."}

        card_content = create_adaptive_card_from_template(
            title=news_title,
            description=news_description,
            source_link=source_link,
            source_name=source_name,
            source_date=source_date,
        )

        if not card_content:
            error_msg = "Failed to create adaptive card. Check server logs for details."
            return {"success": False, "status_message": error_msg}

        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card_content,
        }

        try:
            api.messages.create(
                toPersonEmail=recipient_email,
                text=f"News Update: {news_title}",
                attachments=[attachment],
            )
            status = f"Adaptive card sent successfully to {recipient_email}."
            logger.info(status)
            return {"success": True, "status_message": status}
        except ApiError as e:
            status = f"Webex API error while sending card: {e}"
            logger.error(status)
            return {"success": False, "status_message": status}
        except Exception as e:
            status = f"An unexpected error occurred while sending card: {e}"
            logger.error(status)
            return {"success": False, "status_message": status}

    # --- Run the Server ---
    try:
        logger.info(f"🌍 Server starting on http://{host}:{port}")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("\n🛑 Server shutting down gracefully...")
    except Exception as e:
        logger.critical(f"❌ A critical error occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("✅ Server exited.")


if __name__ == "__main__":
    main()

