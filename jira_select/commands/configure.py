from logging import getLogger
from typing import Tuple

import keyring
from jira import JIRA, JIRAError
from prompt_toolkit.shortcuts import input_dialog, yes_no_dialog

from ..constants import APP_NAME
from ..exceptions import UserError
from ..plugin import BaseCommand

logger = getLogger(__name__)


class Command(BaseCommand):
    @classmethod
    def get_help(cls) -> str:
        return (
            "Interactively allows you to configure jira-select to connect "
            "to your Jira instance."
        )

    def collect_credentials(self) -> Tuple[str, str, str]:
        instance_url = input_dialog(
            title="Instance URL",
            text="Please enter your Jira instance URL (e.g. 'https://mycompany.jira.com/')",
        ).run()
        if not instance_url:
            raise UserError("Cancelled")
        username = input_dialog(
            title="Username",
            text=(
                "Please enter your Jira username:\n\nfor Jira Cloud instances, you may need to generate a new API token to use as a password at https://id.atlassian.com/manage-profile/security/api-tokens"
            ),
        ).run()
        if not username:
            raise UserError("Cancelled")
        password = input_dialog(
            title="Password",
            text=f"Please enter the password for {username}: ",
            password=True,
        ).run()
        if not password:
            raise UserError("Cancelled")

        return instance_url, username, password

    def handle(self) -> None:
        instance_url = ""
        username = ""
        password = ""

        while True:
            instance_url, username, password = self.collect_credentials()

            try:
                JIRA(
                    instance_url,
                    options={"agile_rest_path": "agile",},
                    basic_auth=(username, password),
                    max_retries=0,
                )
                break
            except JIRAError:
                result = yes_no_dialog(
                    title="Error connecting to Jira",
                    text=(
                        "A connection to Jira could not be established using "
                        "the credentials you provided; try again?"
                    ),
                ).run()
                if not result:
                    raise UserError("Aborted; configuration not saved.")

        self.config.setdefault("instances", {})[self.options.instance_name] = {
            "url": instance_url,
            "username": username,
        }
        self.save_config()

        store_password = yes_no_dialog(
            title="Save password?",
            text="Would you like to save this password to your system keyring?",
        ).run()
        if store_password:
            keyring.set_password(APP_NAME, instance_url + username, password)
