from multiprocessing.context import Process
from typing import Any

from flask import Flask, jsonify

from app.config import WORKER_UPDATE_DELAY
from app.crypto import crypto as crypto_bp
from app.db.types import DecimalJSONEncoder
from app.db.utils import init_db, update_prices_permanently
from app.exceptions import InvalidUsage
from app.users import users as users_bp


def create_app(should_init_db: bool = True) -> Flask:
    app = Flask(__name__)
    app.json_encoder = DecimalJSONEncoder

    app.register_blueprint(users_bp)
    app.register_blueprint(crypto_bp)

    # pylint: disable=unused-variable
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(
        error: InvalidUsage,
    ) -> Any:
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    if should_init_db:
        init_db()

    app.worker = Process(target=update_prices_permanently, args=(WORKER_UPDATE_DELAY,))
    app.worker.start()

    return app
