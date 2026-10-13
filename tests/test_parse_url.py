"""Run: uv run python tests/test_parse_url.py"""
from synology_chat_mcp import _parse_url

assert _parse_url("https://chat.example.com") == ("chat.example.com", "443", True)
assert _parse_url("chat.example.com") == ("chat.example.com", "443", True)
assert _parse_url("https://nas.local:5001") == ("nas.local", "5001", True)
assert _parse_url("http://192.168.1.10:5000/") == ("192.168.1.10", "5000", False)
assert _parse_url("http://nas.local") == ("nas.local", "80", False)
print("ok")
