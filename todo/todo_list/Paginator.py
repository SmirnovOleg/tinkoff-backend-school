from typing import Any, List

from todo_list.models import TodoItem


class Paginator:
    ITEMS_PER_PAGE: int = 10

    def __init__(self, all_items: List[Any], page_num: int):
        self.all_items = all_items
        self.page_num = page_num
        self.page_items = self.get_items_by_page(
            items=all_items, offset=(page_num - 1) * Paginator.ITEMS_PER_PAGE
        )
        self.total_items_count = len(all_items)
        if self.total_items_count % Paginator.ITEMS_PER_PAGE == 0:
            self.total_pages_count = self.total_items_count // Paginator.ITEMS_PER_PAGE
        else:
            self.total_pages_count = (
                self.total_items_count // Paginator.ITEMS_PER_PAGE + 1
            )

    @staticmethod
    def get_items_by_page(items: List[TodoItem], offset: int):
        return items[offset : offset + Paginator.ITEMS_PER_PAGE]
