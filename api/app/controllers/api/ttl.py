from flask_restful import Resource, reqparse
from app.helpers.rest import response
from app.models import model
from app.middlewares import auth


class GetTtlData(Resource):
    @auth.auth_required
    def get(self):
        try:
            data = model.get_all("ttl")
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data)


class GetTtlDataId(Resource):
    @auth.auth_required
    def get(self, ttl_id):
        try:
            data = model.get_by_condition(table="ttl", field="id", value=ttl_id)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data)


class TtlAdd(Resource):
    @auth.auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("ttl", type=str, required=True)
        args = parser.parse_args()
        ttl = args["ttl"]

        data = {"ttl": ttl}
        try:
            model.insert(table="ttl", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Inserted")


class TtlEdit(Resource):
    @auth.auth_required
    def put(self, ttl_id):
        parser = reqparse.RequestParser()
        parser.add_argument("ttl", type=str, required=True)
        args = parser.parse_args()
        ttl = args["ttl"]

        data = {"where": {"id": ttl_id}, "data": {"ttl": ttl}}

        try:
            model.update("ttl", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Edited")


class TtlDelete(Resource):
    @auth.auth_required
    def delete(self, ttl_id):
        try:
            data = model.delete(table="ttl", field="id", value=ttl_id)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Deleted")
