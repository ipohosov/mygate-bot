import asyncio
from datetime import datetime

from src.base_client import BaseClient
from src.models.account import Account
from src.utils.logger import Logger
from src.utils.retry_decorator import retry_on_none


class MyGate(Logger, BaseClient):

    def __init__(self, account: Account):
        Logger.__init__(self)
        BaseClient.__init__(self, account)
        self.account = account



    @staticmethod
    def generate_activation_date():
        activation_date = datetime.utcnow().isoformat() + "Z"
        return activation_date

    @retry_on_none(retries=5, delay=2)
    async def get_users_all_nodes_data(self):
        url = "https://api.mygate.network/api/front/nodes"
        try:
            result = await self.make_request(method="GET", url=url)
            self.logger_msg(self.account,
                            f"All nodes data was collected successfully", 'success')
            return result['data']['items']
        except Exception as e:
            self.logger_msg(self.account,
                            f"Attempt failed to get all nodes data. {e}", 'warning')
            return []

    @retry_on_none(retries=5, delay=2)
    async def get_users_nodes_data(self):
        url = f"https://api.mygate.network/api/front/nodes/{self.account.node__id}"
        try:
            result = await self.make_request(method="GET", url=url)
            self.logger_msg(self.account,
                            f"Node {self.account.node__id} data was collected successfully", 'success')
            return result['data']
        except Exception as e:
            self.logger_msg(self.account,
                            f"Attempt failed to get {self.account.node__id} nodes data. {e}", 'warning')
            return None

    @retry_on_none(retries=5, delay=2)
    async def get_social_tasks(self):
        url = "https://api.mygate.network/api/front/achievements?limit=100"
        try:
            result = await self.make_request(method="GET", url=url, json={})
            self.logger_msg(self.account,
                            f"Social tasks were collected successfully", 'success')
            return result['data']['items']
        except Exception as e:
            self.logger_msg(self.account,
                            f"Attempt failed to get social tasks. {e}", 'warning')
            return None

    @retry_on_none(retries=5, delay=2)
    async def social_media_tasks(self, task_type: str):
        url = f"https://api.mygate.network/api/front/achievements/{task_type}?"
        try:
            result = await self.make_request(method="POST", url=url, json={})
            self.logger_msg(self.account,
                            f"Social media tasks were completed successfully", 'success')
            return result['data']['items']
        except Exception as e:
            self.logger_msg(self.account,
                            f"Attempt failed to complete {task_type} task. {e}", 'warning')
            return None

    @retry_on_none(retries=5, delay=2)
    async def get_ambassador_tasks(self):
        url = "https://api.mygate.network/api/front/achievements/ambassador?limit=100"
        try:
            result = await self.make_request(method="GET", url=url, json={})
            self.logger_msg(self.account,
                            f"Ambassador tasks were collected successfully", 'success')
            return result['data']['items']
        except Exception as e:
            self.logger_msg(self.account,
                            f"Attempt failed to get ambassador tasks. {e}", 'warning')
            return None

    @retry_on_none(retries=5, delay=2)
    async def submit_tasks(self, task_id: str, task_description: str):
        url = f"https://api.mygate.network/api/front/achievements/ambassador/{task_id}/submit"
        try:
            result = await self.make_request(method="POST", url=url, json={})
            self.logger_msg(self.account,
                            f"Task was completed successfully", 'success')
            return result['data']['items']
        except Exception as e:
            self.logger_msg(self.account,
                            f"Attempt failed to complete {task_description} task. {e}", 'warning')
            return None

    @retry_on_none(retries=5, delay=2)
    async def quality(self):
        url = "https://api.mygate.network/api/front/metadata/nodes/quality"
        try:
            await self.make_request(method="GET", url=url, json={}, extension=True)
            self.logger_msg(self.account,
                            f"Quality got successfully.", 'success')
        except Exception as e:
            self.logger_msg(self.account,
                            f"There some issues during getting node quality. {e}", 'warning')
            return None

    async def process_loads_nodes_data(self):
        if 'None' in str(self.account.node_id) or 'None' in str(self.account.node__id):
            nodes = await self.get_users_all_nodes_data()
            if len(nodes) < 0:
                self.logger_msg(self.account, "GET Node Data Failed", 'warning')
                raise Exception("Node Data was not collected successfully")

            self.account.node_id = nodes[0].get('id')
            self.account.node__id = nodes[0].get('_id')

    async def process_loads_nodes_earning(self):
        nodes_data = await self.get_users_nodes_data()
        if nodes_data:
            today_earn = nodes_data['todayEarn']
            season_earn = nodes_data['seasonEarn']
            self.account.points = season_earn
            uptime = nodes_data['uptime']
            self.logger_msg(self.account,
                            f"Earning Today: {today_earn} PTS. "
                            f"Earning Season: {season_earn} PTS. Uptime: {uptime}.", 'info')
        else:
            self.logger_msg(self.account,
                            f"GET Eearning Data Failed", 'warning')

    async def process_users_tasks_completion(self):
        social_tasks = await self.get_social_tasks()
        for social_task in social_tasks:
            if social_task['type'] == 'keep-in-touch' and social_task['status'] == 'UNCOMPLETED':
                await self.social_media_tasks("follow-x")
            elif social_task['type'] == 'telegram-follower' and social_task['status'] == 'UNCOMPLETED':
                await self.social_media_tasks("follow-telegram")
            elif social_task['type'] == 'open-link' and social_task['status'] == 'UNCOMPLETED':
                await self.social_media_tasks("open-link/67890c36f9921e50ad4c2e4e/submit")

        tasks = await self.get_ambassador_tasks()
        if tasks:
            for task in tasks:
                task_id = task['_id']
                status = task['status']

                if task and status == 'UNCOMPLETED':
                    submit = await self.submit_tasks(task_id, task['description'])
                    if submit and submit['message'] == 'OK':
                        self.logger_msg(self.account,
                                        f"Ambassador Task: {task['name']} - {task['description']} "
                                        f"Is Completed. Reward {task['experience']} EXP.", 'success')
                    else:
                        self.logger_msg(self.account,
                                        f"Ambassador Task: {task['name']} - {task['description']} "
                                        f"Isn't Completed", 'warning')
                    await asyncio.sleep(5)
