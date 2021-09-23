from flask import Flask, Request, redirect, render_template, request, url_for

from todo_list.config import QueryParameter, Status
from todo_list.models import InvalidArgumentError, TodoItem, TodoList
from todo_list.Paginator import Paginator

app = Flask(__name__)

app.todo_list = TodoList()


@app.route('/')
@app.route('/active')
def index():
    return redirect(url_for('get_or_update_active_items', page_num=1))


@app.route('/finished')
def get_finished():
    return redirect(url_for('get_finished_items', page_num=1))


@app.route('/all')
def get_all():
    return redirect(url_for('get_or_update_all_items', page_num=1))


@app.route('/finished/<int:page_num>', methods=['GET'])
def get_finished_items(page_num: int):
    items = app.todo_list.get_finished_items(
        filter_substring=request.args.get(QueryParameter.FILTER_SUBSTRING)
    )
    paginator = Paginator(all_items=items, page_num=page_num)
    return render_template('todo.html', paginator=paginator, status=Status.FINISHED)


@app.route('/all/<int:page_num>', methods=['GET', 'POST'])
def get_or_update_all_items(page_num: int):
    try:
        process_request(request)
    except InvalidArgumentError as e:
        return f'Invalid query parameter: {str(e)}', 400
    items = app.todo_list.get_all_items(
        filter_substring=request.args.get(QueryParameter.FILTER_SUBSTRING)
    )
    paginator = Paginator(all_items=items, page_num=page_num)
    return render_template('todo.html', paginator=paginator, status=Status.ALL)


@app.route('/active/<int:page_num>', methods=['GET', 'POST'])
def get_or_update_active_items(page_num: int):
    try:
        process_request(request)
    except InvalidArgumentError as e:
        return f'Invalid query parameter: {str(e)}', 400
    items = app.todo_list.get_active_items(
        filter_substring=request.args.get(QueryParameter.FILTER_SUBSTRING)
    )
    paginator = Paginator(all_items=items, page_num=page_num)
    return render_template('todo.html', paginator=paginator, status=Status.ACTIVE)


def process_request(req: Request):
    if req.method == 'POST':
        if QueryParameter.NEW_TASK_DESCRIPTION in req.form:
            # Add new task
            app.todo_list.add_item(
                item=TodoItem(req.form[QueryParameter.NEW_TASK_DESCRIPTION])
            )
        elif QueryParameter.FINISHED_TASK_ID in req.form:
            # Finish specified task
            item_id = req.form[QueryParameter.FINISHED_TASK_ID]
            if item_id.isnumeric():
                item_id = int(item_id)
            else:
                raise InvalidArgumentError('ID of the finished task must be numeric')
            app.todo_list.finish_item_by_id(item_id)
