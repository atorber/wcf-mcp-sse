from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import re
import json

# Initialize FastMCP server for Weather tools (SSE)
mcp = FastMCP("wcf-bot-http-sse")

# Constants
# BASE_URL = "http://127.0.0.1:9999"
BASE_URL = "http://10.211.55.13:9999"
USER_AGENT = "wcf-bot/1.0"

# 获取好友列表
async def get_friends_request() -> dict[str, Any] | None:
    url = f"{BASE_URL}/friends"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error finding contact: {e}")
            return e

# 查询指定好友
async def get_friend_by_name(name: str) -> dict[str, Any] | None:
    friends_res = await get_friends_request()
    if friends_res is None:
        return f"没有找到好友 {name}"
    print("Debug - friends_res:", friends_res)  # 添加调试打印
    if isinstance(friends_res, Exception):
        return f"获取好友列表失败: {str(friends_res)}"
    if not isinstance(friends_res, dict) or "data" not in friends_res:
        return f"好友列表数据格式错误: {str(friends_res)}"
    friends = friends_res['data']['friends']
    print("Debug - friends:", friends)  # 添加调试打印
    friend_list = []
    for friend in friends:
        # 正则匹配friend["name"]包含name
        if isinstance(friend, dict) and "name" in friend and re.search(name, friend["name"]):
            friend_list.append(friend)
    return json.dumps(friend_list, ensure_ascii=False)

# 查询完整通讯录
async def get_contacts_request() -> dict[str, Any] | None:
    url = f"{BASE_URL}/contacts"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error finding full contact: {e}")
            return e
        
# 查询指定联系人或群组
async def get_contact_by_name(name: str) -> dict[str, Any] | None:
    contacts_res = await get_contacts_request()
    if contacts_res is None:
        return f"没有找到联系人 {name}"
    contacts = contacts_res['data']['contacts']
    contact_list = []
    for contact in contacts:
        # 正则匹配
        if re.search(name, contact["name"]):
            contact_list.append(contact)
    return json.dumps(contact_list, ensure_ascii=False)

# 发送文本消息请求
async def send_text_message_request(
        msg: str,
        receiver: str,
        aters: str
        ) -> dict[str, Any] | None:
    url = f"{BASE_URL}/text"
    data = {
        "msg": msg,
        "receiver": receiver,
        "aters": aters
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending text message: {e}")
            return e
        
# 发送图片消息请求
async def send_image_message_request(
        path: str,
        receiver: str
        ) -> dict[str, Any] | None:
    url = f"{BASE_URL}/image"
    data = {
        "path": path,
        "receiver": receiver
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending image message: {e}")
            return e
        
# 发送文件消息请求
async def send_file_message_request(
        path: str,
        receiver: str
        ) -> dict[str, Any] | None:
    url = f"{BASE_URL}/file"
    data = {
        "path": path,
        "receiver": receiver
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending file message: {e}")
            return e

@mcp.tool()
async def get_friends() -> str:
    """获取好友列表.

    Returns:
        str: 好友列表
    """
    data = await get_friends_request()

    if not data:
        return "没有找到好友."

    return data

@mcp.tool()
async def get_contacts() -> str:
    """获取完整通讯录.

    Args:
        name: 联系人名称
    """
    data = await get_contacts_request()

    if not data:
        return "没有找到通讯录."

    return data

@mcp.tool()
async def get_friend_by_name(name: str) -> str:
    """通过名称查找好友.

    Args:
        name: 好友名称
    """
    data = await get_friend_by_name(name)

    if not data:
        return "没有找到好友."

    return data

@mcp.tool()
async def get_room_by_name(name: str) -> str:
    """通过名称查找群组.

    Args:
        name: 群组名称
    """
    data = await get_contact_by_name(name)

    if not data:
        return "没有找到群组."

    return data

@mcp.tool()
async def send_text_message_by_nickname(
        msg: str,
        nickname: str,
        ) -> str:
    """发送文本消息给好友或者群组.

    Args:
        msg: 消息内容
        nickname: 好友或群组昵称
    """
    data = await get_contact_by_name(nickname)
    if not data:
        return "没有找到好友或群组."
    contact = data[0]
    data = await send_text_message_request(msg, contact["wxid"], '')

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_at_text_message_by_nickname(
        msg: str,
        nickname: str,
        at_nickname: list[str]
        ) -> str:
    """向群组发送文本消息并@指定成员.

    Args:
        msg: 消息内容
        nickname: 群组昵称
        at_nickname: 指定成员的昵称
    """
    at_wxid = []
    data = await get_contact_by_name(nickname)
    if not data:
        return "没有找到群组."
    contact = data[0]
    for at_nickname in at_nickname:
        data = await get_contact_by_name(at_nickname)
        if not data:
            return "没有找到指定成员."
        at_wxid.append(data[0]["wxid"])
    aters = ','.join(at_wxid)
    data = await send_text_message_request(msg, contact["wxid"], aters)

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_image_message_by_nickname(
        path: str,
        nickname: str,
        ) -> str:
    """发送图片消息给好友或者群组.

    Args:
        path: 图片路径
        nickname: 好友或群组昵称
    """
    data = await get_contact_by_name(nickname)
    if not data:
        return "没有找到好友或群组."
    contact = data[0]
    data = await send_image_message_request(path, contact["wxid"])

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_file_message_by_nickname(
        path: str,
        nickname: str
        ) -> str:
    """向群组发送图片消息.

    Args:
        path: 图片路径
        nickname: 群组昵称
        at_nickname: 指定成员的昵称
    """
    data = await get_contact_by_name(nickname)
    if not data:
        return "没有找到群组."
    contact = data[0]
    data = await send_image_message_request(path, contact["wxid"])

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_text_message_by_wxid(
        msg: str,
        receiver: str,
        ) -> str:
    """发送文本消息给好友或者群组.

    Args:
        msg: 消息内容
        receiver: 接收好友或群组的ID
    """
    data = await send_text_message_request(msg, receiver, '')

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_at_text_message_by_wxid(
        msg: str,
        receiver: str,
        at_wxid: list[str]
        ) -> str:
    """向群组发送文本消息并@指定成员.

    Args:
        msg: 消息内容
        receiver: 接收好友或群组的ID
        at_wxid: 指定成员的ID
    """
    aters = ','.join(at_wxid)
    data = await send_text_message_request(msg, receiver, aters)

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_image_message_by_wxid(
        path: str,
        receiver: str,
        ) -> str:
    """发送图片消息给好友或者群组.

    Args:
        path: 图片路径
        receiver: 接收好友或群组的ID
    """
    data = await send_image_message_request(path, receiver) 

    if not data:
        return "发送失败."

    return data

@mcp.tool()
async def send_file_message_by_wxid(
        path: str,
        receiver: str,
        ) -> str:
    """发送文件消息给好友或者群组.

    Args:
        path: 文件路径
        receiver: 接收好友或群组的ID
    """
    data = await send_file_message_request(path, receiver)

    if not data:
        return "发送失败."

    return data

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
