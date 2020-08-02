from typing import Dict, Iterator, List

from jira.resources import Board

from ..exceptions import QueryError
from ..plugin import BaseSource
from ..types import SchemaRow


class Source(BaseSource):
    SCHEMA: List[SchemaRow] = [
        {"id": "id", "type": "int"},
        {"id": "name", "type": "str"},
        {"id": "type", "type": "str"},
    ]

    def __iter__(self) -> Iterator[Dict]:
        start_at = 0
        max_results = 2 ** 32
        result_limit = self.query.limit or 2 ** 32

        where = self.query.where or {}
        if where and not isinstance(where, dict):
            raise QueryError(
                "Board query 'where' expressions should be a dictionary "
                "having any of the following keys: 'type' or 'name'"
            )

        param_type = where.pop("type", None)
        param_name = where.pop("name", None)

        if where:
            raise QueryError(f"Unexpected 'where' parameters: {where}.")

        self.update_progress(completed=0, total=1, visible=True)
        while start_at < min(max_results, result_limit):
            results = self.jira.boards(
                startAt=start_at,
                maxResults=min(result_limit, 100),
                type=param_type,
                name=param_name,
            )

            max_results = results.total
            count = min([results.total, result_limit])
            self.update_count(count)

            for result in results:
                self.update_progress(advance=1, total=count, visible=True)

                yield result.raw

                start_at += 1

                # Return early if our result limit has been reached
                if start_at >= result_limit:
                    break

    def rehydrate(self, value: Dict) -> Board:
        return Board(
            {"agile_rest_path": self.jira._options["agile_rest_path"]}, None, value
        )
