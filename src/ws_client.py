from datetime import datetime, timezone

import aiohttp
import base64
import hashlib
import hmac
import json
import os

from src.models.account import Account
from src.utils.logger import Logger


class WSClient(Logger):
    def __init__(self, account: Account):
        Logger.__init__(self)
        self.account = account

    def generate_signature(self):
        time_now = datetime.now(timezone.utc)

        # Create UTC timestamp
        timestamp = int(time_now.replace(tzinfo=timezone.utc).timestamp() * 1000)

        # Create signature using HMAC SHA256
        secret = "|`8S%QN9v&/J^Za"
        message = json.dumps(self.account.node_id) + str(timestamp)
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

        return signature, timestamp

    @staticmethod
    def generate_websocket_key():
        random_bytes = os.urandom(16)  # Generate 16 random bytes
        key = base64.b64encode(random_bytes).decode('utf-8')  # Encode in base64
        return key

    async def run_websocket(self):
        signature, timestamp = self.generate_signature()
        wss_url = f"wss://api.mygate.network/socket.io/?nodeId={self.account.node_id}&signature={signature}&timestamp={timestamp}&version=2&EIO=4&transport=websocket"
        sec_websocket_key = self.generate_websocket_key()

        headers = {
            "Accept-language": "en-US,en;q=0.9",
            "Cache-control": "no-cache",
            "Connection": "Upgrade",
            "Origin": "chrome-extension://hajiimgolngmlbglaoheacnejbnnmoco",
            "Pragma": "no-cache",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": sec_websocket_key,
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": self.account.user_agent
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(wss_url, proxy=self.account.proxy, headers=headers) as websocket:
                    async for message in websocket:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            if message.data.startswith("0{"):
                                break

                        elif message.type == aiohttp.WSMsgType.ERROR:
                            print("Error encountered:", message.data)
                            break

                    await websocket.send_str(f'40{{"token": "Bearer {self.account.token}"}}')

                    async for message in websocket:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            if message.data.startswith("41"):
                                break

                        elif message.type == aiohttp.WSMsgType.ERROR:
                            print("Error encountered:", message.data)
                            break

                    self.logger_msg(self.account, f"Heartbeat sent successfully.", 'success')

                await session.close()
        except Exception:
            self.logger_msg(self.account, f"Heartbeat was not sent successfully.", 'warning')
