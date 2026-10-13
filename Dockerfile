FROM python:3.12-slim
LABEL io.modelcontextprotocol.server.name="io.github.Louis-Lastella/synology-chat-mcp" \
      org.opencontainers.image.source="https://github.com/Louis-Lastella/synology-chat-mcp" \
      org.opencontainers.image.description="MCP server for Synology Chat" \
      org.opencontainers.image.licenses="MIT"
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && rm -rf /app
ENTRYPOINT ["synology-chat-mcp"]
