import pathlib

from flask_restful import Resource

from app.vendors.rest import response


class HealthCheck(Resource):
    def get(self):
        version = ""

        current_path = pathlib.Path(__file__)
        path = current_path.parents[3].joinpath("version.txt")
        if path.is_file():
            with open(path, "rb") as f:
                version = f.read().decode("utf-8")
                version = version.rstrip()

        if not version:
            version = "__UNKNOWN__"

        data = {"status": "running", "version": version}
        return response(200, data=data, message="OK")
