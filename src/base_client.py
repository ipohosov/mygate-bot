import re
import ssl
from abc import ABC

import aiohttp
import requests
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from src.models.account import Account
from src.models.exceptions import SoftwareException, ProxyException, TokenException
from src.utils.file_manager import add_stopped_acc


class BaseClient(ABC):
    def __init__(self, account: Account):
        self.account = account
        self.session = ClientSession(timeout=aiohttp.ClientTimeout(total=120),
                                     connector=ProxyConnector.from_url(f'{account.proxy}',
                                                                       ssl=ssl.create_default_context(),
                                                                       verify_ssl=True))

    async def make_request(self, auth=True, method: str = 'GET', url: str = None, params: dict = None,
                           headers: dict = None, data: str = None, json: dict = None, extension=False):
        while True:
            response_text = ""
            try:
                request_headers = await self.generate_headers(auth, extension, headers)
                async with self.session.request(
                        method=method, url=url, headers=request_headers,
                        data=data, params=params, json=json) as response:
                    response_text = str(await response.text())
                    if response.status in [200, 201]:
                        data = await response.json()
                        return data
                    elif response.status in [401]:
                        data = await response.json()
                        await add_stopped_acc(self.account.email)
                        raise TokenException(f"Token expired. {data}")
                    else:
                        raise SoftwareException()
            except SoftwareException as error:
                if response_text:
                    message = f"Response - {response_text}. Error - {error}."
                else:
                    message = f"Error - {error}."
                raise SoftwareException(f"Details: {message}")

    async def generate_headers(self, auth: bool, extension: bool, extra_headers: dict = None,):
        ua_pattern = re.compile(
            r'Mozilla/5.0 \(([^)]+)\) AppleWebKit/([\d.]+) \(KHTML, like Gecko\) Chrome/([\d.]+) Safari/([\d.]+)'
        )
        # Match the User-Agent string
        match = ua_pattern.match(self.account.user_agent)

        # If not matched, raise an exception
        if not match:
            raise ValueError("User-Agent format not recognized")

        # Extract platform and version information
        platform = match.group(1).strip()
        chrome_version = match.group(3).split('.')[0]

        # Calculate platform
        sec_ua_platform = ""
        sec_ch_ua = ""
        if "Windows" in platform:
            sec_ua_platform = "Windows"
            sec_ch_ua = f'"Not/A)Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"'
        if "Linux" in platform:
            sec_ua_platform = "Linux"
            sec_ch_ua = f'"Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}", "Not-A.Brand";v="99"'
        if "Macintosh" in platform:
            sec_ua_platform = "macOS"
            sec_ch_ua = f'"Not_A Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"'

        if extension:
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'priority': 'u=1, i',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'none',
                'sec-gpc': '1',
                'user-agent': self.account.user_agent
            }
        else:
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://app.mygate.network',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://app.mygate.network/',
                'sec-ch-ua': f'{sec_ch_ua}',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': f'"{sec_ua_platform}"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'sec-gpc': '1',
                'user-agent': self.account.user_agent
            }

        if auth:
            headers = dict({'authorization': f'Bearer {self.account.token}'}, **headers)

        if extra_headers:
            headers = dict(headers, **extra_headers)
        return headers

    async def check_proxy(self):
        proxy = self.account.proxy
        try:
            # Make a request through the proxy
            response = requests.get('http://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=15)
            # If the request is successful, print the response
            if response.status_code == 200:
                return True
            else:
                raise ProxyException(f"Proxy for account  {self.account.account_name} is not working. "
                                 f"Error: {response.status_code}")
        except Exception as e:
            raise ProxyException(f"Proxy for account  {self.account.account_name} is not working. Error: {e}")

    async def close_all(self):
        await self.session.connector.close()
        await self.session.close()
