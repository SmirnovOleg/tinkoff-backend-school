import re
from typing import Callable, List, Optional


class TodoItem:
    __id = 0

    def __init__(self, description: str, is_finished: bool = False):
        if description == '' or description.isspace():
            raise InvalidArgumentError('task description should not be empty')
        self.id = TodoItem.__id
        TodoItem.__id += 1
        self.desc = description
        self.is_finished = is_finished

    def __repr__(self):
        return self.desc

    def __eq__(self, other):
        return self.desc == other.desc


class TodoList:
    def __init__(self, items=None):
        self.items = items or []

    def add_item(self, item: TodoItem):
        self.items.append(item)

    def finish_item_by_id(self, item_id: int):
        for item in self.items:
            if item.id == item_id:
                item.is_finished = True

    def get_all_items(self, filter_substring: Optional[str] = None) -> List[TodoItem]:
        return list(
            filter(
                self.__get_filter_func(filter_substring),
                self.get_active_items() + self.get_finished_items(),
            )
        )

    def get_finished_items(
        self, filter_substring: Optional[str] = None
    ) -> List[TodoItem]:
        return list(
            filter(
                self.__get_filter_func(filter_substring),
                [item for item in reversed(self.items) if item.is_finished],
            )
        )

    def get_active_items(
        self, filter_substring: Optional[str] = None
    ) -> List[TodoItem]:
        return list(
            filter(
                self.__get_filter_func(filter_substring),
                [item for item in reversed(self.items) if not item.is_finished],
            )
        )

    @staticmethod
    def __get_filter_func(substring: Optional[str]) -> Callable[[TodoItem], bool]:
        if substring is None:
            return lambda item: True
        return lambda item: re.search(substring, item.desc, re.IGNORECASE) is not None


class InvalidArgumentError(Exception):
    pass
