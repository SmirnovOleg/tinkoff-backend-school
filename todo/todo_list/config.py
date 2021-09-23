from enum import Enum


class QueryParameter(str, Enum):
    # POST
    NEW_TASK_DESCRIPTION = 'new_item_desc'
    FINISHED_TASK_ID = 'finish_item_id'

    # GET
    FILTER_SUBSTRING = 'filter'


class Status(str, Enum):
    ALL = 'all'
    FINISHED = 'finished'
    ACTIVE = 'active'
