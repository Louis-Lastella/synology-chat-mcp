# synology-chat-mcp

MCP server for [Synology Chat](https://www.synology.com/dsm/feature/chat). Works with any self-hosted Synology Chat instance: list channels, read recent posts, find users, send messages and upload files from any MCP client (Claude Desktop, Claude Code, Hermes, ...).

It logs in as a normal DSM user through the Synology Web API, so it sees exactly what that user sees in Chat (channels and DMs), no bot or webhook setup needed.

## Tools

| Tool | What it does |
|---|---|
| `list_channels()` | Joined channels and DMs (id, name, type, members, unread) |
| `find_user(name_query)` | Find users by partial username |
| `get_recent_posts(channel_id, limit=20)` | Most recent messages/files in a channel or DM |
| `dm_channel_for_user(user_id)` | 1:1 DM channel id for a user, or `null` if none exists yet |
| `send_message(channel_id, message)` | Post a text message |
| `send_file(channel_id, file_path, message="")` | Upload a local file, optionally followed by a message |

## Configuration

All config comes from environment variables, set them in your MCP client config:

| Variable | Required | Example |
|---|---|---|
| `SYNOLOGY_CHAT_URL` | yes | `https://chat.example.com`, `https://nas.local:5001`, `http://192.168.1.10:5000` |
| `SYNOLOGY_CHAT_USER` | yes | DSM username |
| `SYNOLOGY_CHAT_PASS` | yes | DSM password |
| `SYNOLOGY_CHAT_VERIFY_SSL` | no | `false` for self-signed certificates (default `true`) |

A URL without scheme means `https`, without port it uses 443 (https) or 80 (http).

## Install

Needs [uv](https://docs.astral.sh/uv/). No clone required, `uvx` runs it straight from GitHub.

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "synology-chat": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Louis-Lastella/synology-chat-mcp", "synology-chat-mcp"],
      "env": {
        "SYNOLOGY_CHAT_URL": "https://chat.example.com",
        "SYNOLOGY_CHAT_USER": "your-username",
        "SYNOLOGY_CHAT_PASS": "your-password"
      }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add synology-chat \
  -e SYNOLOGY_CHAT_URL=https://chat.example.com \
  -e SYNOLOGY_CHAT_USER=your-username \
  -e SYNOLOGY_CHAT_PASS=your-password \
  -- uvx --from git+https://github.com/Louis-Lastella/synology-chat-mcp synology-chat-mcp
```

**Hermes** (`~/.hermes/config.yaml`):

```yaml
mcp_servers:
  synology-chat:
    command: uvx
    args: [--from, git+https://github.com/Louis-Lastella/synology-chat-mcp, synology-chat-mcp]
    env:
      SYNOLOGY_CHAT_URL: https://chat.example.com
      SYNOLOGY_CHAT_USER: your-username
      SYNOLOGY_CHAT_PASS: your-password
```

From a local clone instead: `git clone`, `uv sync`, then use `uv` with args `--directory /path/to/synology-chat-mcp run synology-chat-mcp`.

## Notes

- Accounts with 2-factor authentication are not supported (the Web API wants a fresh OTP per login). Use an account without 2FA.
- DMs show up with type `anonymous`, that is Synology's name for 1:1 conversations.
- `find_user` only matches the `username`, not display names.
- Downloading attachments is not a tool yet. The session is available via `synology_chat_mcp._client().session`; call `GET /webapi/entry.cgi?api=SYNO.Chat.Post.File&method=get&version=2&post_id=<id>&_sid=<sid>` with the header `X-SYNO-TOKEN: <session.syno_token>`.

## Development

```bash
uv sync
uv run python tests/test_parse_url.py
```

## License

MIT
