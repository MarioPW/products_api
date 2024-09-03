from typing import Any, Dict, Optional
from fastapi import HTTPException

class CustomErrors(HTTPException):
    def __init__(self, status_code: int, detail: Any = None, headers: Dict[str, str] | None = None) -> None:
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


if __name__ == "__name__":

    error = CustomErrors(400, "Not Found", { "acces": "denied" })
    print(error)