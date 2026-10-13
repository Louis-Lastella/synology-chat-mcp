"""MCP server for Synology Chat: read channels/posts, find users, send messages and files.

Config via env vars:
  SYNOLOGY_CHAT_URL         e.g. https://chat.example.com or http://192.168.1.10:5000
  SYNOLOGY_CHAT_USER        DSM username
  SYNOLOGY_CHAT_PASS        DSM password
  SYNOLOGY_CHAT_VERIFY_SSL  "false" for self-signed certs (default: true)
"""
import os
from functools import lru_cache
from urllib.parse import urlsplit

from fastmcp import FastMCP
from synology_api import chat

mcp = FastMCP("synology-chat")


def _parse_url(url: str) -> tuple[str, str, bool]:
    """'https://host[:port]' -> (host, port, secure). Bare host means https."""
    parts = urlsplit(url if "://" in url else f"https://{url}")
    secure = parts.scheme == "https"
    return parts.hostname, str(parts.port or (443 if secure else 80)), secure


@lru_cache(maxsize=1)
def _client() -> chat.ChatUser:
    host, port, secure = _parse_url(os.environ["SYNOLOGY_CHAT_URL"])
    return chat.ChatUser(
        ip_address=host,
        port=port,
        username=os.environ["SYNOLOGY_CHAT_USER"],
        password=os.environ["SYNOLOGY_CHAT_PASS"],
        secure=secure,
        cert_verify=os.environ.get("SYNOLOGY_CHAT_VERIFY_SSL", "true").lower() != "false",
        application="Chat",
        debug=False,  # debug prints to stdout and would corrupt the stdio MCP stream
    )


@mcp.tool
def list_channels() -> list[dict]:
    """List all joined chat channels/DMs with id, name, type, last_post_at."""
    chans = _client().channel_list()["data"]["channels"]
    return [
        {
            "channel_id": c["channel_id"],
            "name": c.get("name") or "(DM)",
            "type": c["type"],
            "members": c.get("members"),
            "last_post_at": c.get("last_post_at"),
            "unread": c.get("unread", 0),
        }
        for c in chans
    ]


@mcp.tool
def find_user(name_query: str) -> list[dict]:
    """Find users by (partial, case-insensitive) username, e.g. 'smith'."""
    users = _client().user_list()["data"]["users"]
    q = name_query.lower()
    return [
        {"user_id": u["user_id"], "username": u.get("username", "")}
        for u in users
        if q in u.get("username", "").lower()
    ]


@mcp.tool
def get_recent_posts(channel_id: int, limit: int = 20) -> list[dict]:
    """Read the most recent messages/files in a channel or DM."""
    result = _client().post_search([channel_id], limit=limit)
    posts = result.get("data", {}).get("search_results", [])
    return [
        {
            "post_id": p.get("post_id"),
            "creator_id": p.get("creator_id"),
            "message": p.get("message", ""),
            "type": p.get("type"),
            "file_name": (p.get("file_props") or {}).get("name"),
            "create_at": p.get("create_at"),
        }
        for p in posts
    ]


@mcp.tool
def dm_channel_for_user(user_id: int) -> int | None:
    """Find (or None if none exists yet) the 1:1 DM channel_id for a given user_id."""
    for c in _client().channel_list()["data"]["channels"]:
        members = c.get("members") or []
        # Synology Chat calls 1:1 DMs "anonymous" channels
        if c.get("type") == "anonymous" and user_id in members and len(members) == 2:
            return c["channel_id"]
    return None


@mcp.tool
def send_message(channel_id: int, message: str) -> dict:
    """Post a text message to a channel/DM."""
    return _client().post_create(channel_id, message)


@mcp.tool
def send_file(channel_id: int, file_path: str, message: str = "") -> dict:
    """Upload a file to a channel/DM, optionally followed by a text message."""
    upload_result = _client().post_file_upload(channel_id, file_path)
    if message:
        _client().post_create(channel_id, message)
    return upload_result


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
