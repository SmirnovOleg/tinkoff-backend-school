from typing import Dict, Optional


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: Optional[int] = None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> Dict[str, str]:
        return {'message': self.message}
