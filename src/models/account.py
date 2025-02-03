import re
from random import randint

from src.models.user_agents import USER_AGENTS
from src.utils.file_manager import read_account


class Account:
    def __init__(self, email, token, proxy):
        super().__init__()
        self.email = email
        self.token = token
        self.node_id = None
        self.node__id = None
        self.proxy = proxy
        self.user_agent = None
        self.points = None
        self.timer = 0

    async def get_detailed_dict_for_account(self):
        data = await read_account(self.email)
        if len(data) > 0:
            self.node_id = data.get("Node_ID")
            self.node__id = data.get("Node__ID")
            self.user_agent = data.get("User_Agent") or USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
            self.points = data.get("Points") or None
            self.timer = int(data.get("Timer"))
        else:
            self.user_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]

    async def account_to_dict(self) -> dict:
        return {
            "Email": self.email,
            "Token": self.token,
            "Node_ID": self.node_id,
            "Node__ID": self.node__id,
            "Proxy": self.proxy,
            "User_Agent": self.user_agent,
            "Points": self.points,
            "Timer": self.timer
        }


async def default_dict_to_account(data) -> Account:
    def beautify_string(data_string):
        data_string = data_string.strip()
        data_string = re.sub('\\s+', ' ', data_string)
        return data_string
    return Account(email=beautify_string(data.get('Email')),
                   token=beautify_string(data.get('Token')),
                   proxy=beautify_string(data.get('Proxy')))
