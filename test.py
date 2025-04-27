from typing import Any
import re
import json
import httpx
# Constants
# BASE_URL = "http://127.0.0.1:9999"
BASE_URL = "http://10.211.55.13:9999"

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
        

async def main():
    # print(await get_friends_request())
    # print(await get_friend_by_name("美美"))
    print(await get_contact_by_name("大师"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())