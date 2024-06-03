from flask import jsonify

from utils import setup_logger


class AppResponse:
    @staticmethod
    def success_with_data(
        data: dict | list = {}, message: str = "Success", status_code: int = 200
    ):
        return (
            jsonify(
                {
                    "success": True,
                    "data": data,
                    "message": message,
                }
            ),
            status_code,
        )

    @staticmethod
    def success_with_message(message: str = "Success", status_code: int = 200):
        return (
            jsonify(
                {
                    "success": True,
                    "message": message,
                }
            ),
            status_code,
        )

    @staticmethod
    def success_with_meta(meta: dict, data: dict | list = []):
        return (
            jsonify(
                {
                    "data": data,
                    "success": True,
                    "message": "200 Success",
                    "meta": meta,
                }
            ),
            200,
        )

    @staticmethod
    def bad_request(message: str = "Bad Request", status_code: int = 400):
        return (
            jsonify(
                {
                    "success": False,
                    "message": message,
                }
            ),
            status_code,
        )

    @staticmethod
    def server_error(
        error, message: str = "Internal Server Error", status_code: int = 500
    ):
        logger = setup_logger()
        logger.error(error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": message,
                    "error": {
                        "code": "ERR_SER0101",
                        "message": str(error),
                    },
                }
            ),
            status_code,
        )
