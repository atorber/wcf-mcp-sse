# WCF-MCP

[![smithery badge](https://smithery.ai/badge/@sidharthrajaram/mcp-sse)](https://smithery.ai/server/@sidharthrajaram/mcp-sse)

WeChatFerry的MCP封装，使用MCP客户端发送消息

- 基于[wcf-http](https://github.com/yuxiaoli/wcf-http)的MCP

- 基于原生[WCF python客户端](https://github.com/atorber/WeChatFerryNext/tree/master/clients/python)的MCP

## MCP配置

```
tbd
```

## 使用方法

**注意**：请确保在 `.env` 文件或环境变量中提供 `ANTHROPIC_API_KEY`。

```
uv run weather.py

uv run client.py http://0.0.0.0:8080/sse
```

```
Initialized SSE client...
Listing tools...

Connected to server with tools: ['get_alerts', 'get_forecast']

MCP Client Started!
Type your queries or 'quit' to exit.

Query: whats the weather like in Spokane?

I can help you check the weather forecast for Spokane, Washington. I'll use the get_forecast function, but I'll need to use Spokane's latitude and longitude coordinates.

Spokane, WA is located at approximately 47.6587° N, 117.4260° W.
[Calling tool get_forecast with args {'latitude': 47.6587, 'longitude': -117.426}]
Based on the current forecast for Spokane:

Right now it's sunny and cold with a temperature of 37°F and ...
```

## 为什么选择这种方式？

这意味着 MCP 服务器现在可以作为一个运行中的进程，代理（客户端）可以随时随地连接、使用并断开连接。换句话说，基于 SSE 的服务器和客户端可以是解耦的进程（甚至可能在解耦的节点上）。这与基于 STDIO 的模式不同，在 STDIO 模式中客户端本身会将服务器作为子进程启动。这种方式更适合"云原生"的使用场景。

### 通过 Smithery 安装

要通过 [Smithery](https://smithery.ai/server/@sidharthrajaram/mcp-sse) 自动安装用于 Claude Desktop 的基于 SSE 的服务器和客户端：

```bash
npx -y @smithery/cli install @sidharthrajaram/mcp-sse --client claude
```

### 服务器

`weather.py` 是一个基于 SSE 的 MCP 服务器，它提供了一些基于国家气象服务 API 的工具。改编自 MCP 文档中的[示例 STDIO 服务器实现](https://modelcontextprotocol.io/quickstart/server)。

默认情况下，服务器运行在 0.0.0.0:8080，但可以通过命令行参数进行配置：

```
uv run weather.py --host <your host> --port <your port>
```

### 客户端

`client.py` 是一个 MCP 客户端，可以连接并使用基于 SSE 的 MCP 服务器提供的工具。改编自 MCP 文档中的[示例 STDIO 客户端实现](https://modelcontextprotocol.io/quickstart/client)。

默认情况下，客户端连接到命令行参数中提供的 SSE 端点：

```
uv run client.py http://0.0.0.0:8080/sse
```
