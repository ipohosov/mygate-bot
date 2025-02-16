import copy
import os
import random
import asyncio

from src.mygate import MyGate
from src.utils.logger import Logger


from src.models.account import Account, default_dict_to_account
from src.utils.file_manager import read_accounts, update_variables_in_file, add_stopped_acc, get_stopped_acc

from src.ws_client import WSClient


class Runner(Logger):

    @staticmethod
    async def get_accounts() -> list[Account]:
        accounts = []
        accounts_data = await read_accounts()
        for account in accounts_data:
            accounts.append(await default_dict_to_account(account))

        return accounts

    async def run_account(self, accounts: list[Account], index):
        account = copy.deepcopy(accounts[index])
        self.logger_msg(account,
                        f"Task for account {account.email} was started.", 'success')

        await account.get_detailed_dict_for_account()
        self.logger_msg(account, f"Account details - {await account.account_to_dict()}", 'success')

        if account.timer == 0:
            account.timer = random.randrange(6600)
        mygate_bot = MyGate(account)
        ws_client = WSClient(account)

        while True:
            try:
                stopped_emails = await get_stopped_acc()
                if account.email in stopped_emails:
                    await mygate_bot.close_all()
                    self.logger_msg(account, "The execution for this account stopped.", 'error')
                    return
                # if random.random() > 0.99:
                await mygate_bot.process_users_tasks_completion()
                if random.random() > 0.9:
                    await mygate_bot.process_loads_nodes_earning()
                    await update_variables_in_file(self, account, await account.account_to_dict())

                await mygate_bot.quality()

                if account.timer > 6600:
                    await ws_client.run_websocket()
                    account.timer = 1

                await asyncio.sleep(600)
                account.timer += 600
                await update_variables_in_file(self, account, await account.account_to_dict())
            except Exception as e:
                continue

    async def run_accounts(self):
        self.logger_msg(None, "Clean up data", 'success')
        stopped_accounts = "./data/accounts/stopped_accounts.txt"
        if os.path.isfile(stopped_accounts):
            os.remove(stopped_accounts)

        self.logger_msg(None, "Collect accounts data", 'success')
        accounts = await self.get_accounts()
        tasks = []

        worked_accounts = []

        for account in accounts:
            bot = MyGate(account)
            try:
                await account.get_detailed_dict_for_account()
                await bot.process_loads_nodes_data()
                await bot.process_loads_nodes_earning()
                await update_variables_in_file(self, account, await account.account_to_dict())
                worked_accounts.append(account)
            except Exception as e:
                self.logger_msg(None, "Account was not processed successfully. "
                                      "Check account and node configuration.", 'error')
                await add_stopped_acc(account.email)
            await bot.close_all()

        self.logger_msg(None, "Create tasks for accounts", 'success')
        for index, account in enumerate(worked_accounts):
            tasks.append(asyncio.create_task(self.run_account(worked_accounts, index)))

        self.logger_msg(None, "Execute tasks for accounts", 'success')
        await asyncio.gather(*tasks, return_exceptions=True)
