import csv
import os
from datetime import datetime

from src.utils.logger import Logger


async def update_variables_in_file(logger: Logger, account, updates: dict):
    account_email = account.email
    file_path = f'./data/accounts/{account_email}.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.isfile(file_path):
        existing_data = await read_account(account_email)
    else:
        existing_data = {}
    updates.update({"Last_Updated": str(datetime.now())})
    for key in updates.keys():
        if key in existing_data.keys():
            existing_data.pop(key)

    new_data = dict(updates, **existing_data)

    # Write updated lines back to the file
    with open(file_path, 'w') as account_file:
        for variable, value in new_data.items():
            account_file.write(f'{variable}={value}\n')

    logger.logger_msg(account, "Account data was updated in file successfully", 'success')


async def read_account(account_email: str) -> dict[str, str]:
    variables = {}
    file_path = f'./data/accounts/{account_email}.txt'
    if os.path.isfile(file_path):
        with open(f'./data/accounts/{account_email}.txt', 'r') as file:
            for line in file:
                # Remove whitespace and split each line into VAR and value
                var, value = line.strip().split('=')
                variables[var] = value
    return variables


async def read_csv(filename: str) -> list[dict[str, str]]:
    accounts_data = []
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if isinstance(row, dict):
                    accounts_data.append(row)
    except (IOError, OSError) as e:
        print(f"Read the file failed: {e}")
    return accounts_data


async def read_accounts() -> list[dict[str, str]]:
    return await read_csv('./data/accounts.csv')

