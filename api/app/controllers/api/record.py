from flask_restful import Resource, reqparse
from app.helpers.rest import response
from app.models import model
from app.models import zone as zone_model
from app.models import record as record_model
from app.models import type_ as type_model
from app.helpers import validator
from app.middlewares import auth
from app.helpers import command


class GetRecordData(Resource):
    @auth.auth_required
    def get(self):
        try:
            records = model.get_all("record")
            records_detail = []
            for record in records:
                detail = record_model.get_other_data(record)
                records_detail.append(detail)

            return response(200, data=records_detail)
        except Exception as e:
            return response(401, message=str(e))


class GetRecordDataId(Resource):
    @auth.auth_required
    def get(self, record_id):
        try:
            record = model.get_one(table="record", field="id", value=record_id)
            data = record_model.get_other_data(record)
            return response(200, data=data)
        except Exception as e:
            return response(401, message=str(e))


class RecordAdd(Resource):
    @auth.auth_required
    def post(self):
        """Add new record.

        note:
        Adding any record with other record is allowed. IETF best practice
        is not handled automatically.  Knot didn't handle this too, and let the
        user know the standards themselves.
        See https://tools.ietf.org/html/rfc1912
        """
        parser = reqparse.RequestParser()
        parser.add_argument("zone", type=str, required=True)
        parser.add_argument("owner", type=str, required=True)
        parser.add_argument("rtype", type=str, required=True)
        parser.add_argument("rdata", type=str, required=True)
        parser.add_argument("ttl_id", type=str, required=True)
        args = parser.parse_args()
        owner = args["owner"].lower()
        rtype = args["rtype"].lower()
        rdata = args["rdata"]
        zone = args["zone"]
        ttl_id = args["ttl_id"]

        try:
            type_id = type_model.get_typeid_by_rtype(rtype)
            zone_id = zone_model.get_zone_id(zone)
        except Exception as e:
            return response(401, message=str(e))

        try:
            # rtype no need to be validated & no need to check its length
            # `get_typeid` will raise error for non existing rtype
            validator.validate(rtype.upper(), rdata)

        except Exception as e:
            return response(401, message=str(e))

        try:
            data = {
                "owner": owner,
                "zone_id": zone_id,
                "type_id": type_id,
                "ttl_id": ttl_id,
            }
            record_id = model.insert(table="record", data=data)

            content_data = {"rdata": rdata, "record_id": record_id}
            model.insert(table="rdata", data=content_data)

            command.send_zone(record_id, "zone-set")
            return response(200, data=data, message="Inserted")
        except Exception as e:
            return response(401, message=str(e))


class RecordEdit(Resource):
    @auth.auth_required
    def put(self, record_id):
        parser = reqparse.RequestParser()
        parser.add_argument("zone", type=str, required=True)
        parser.add_argument("owner", type=str, required=True)
        parser.add_argument("rtype", type=str, required=True)
        parser.add_argument("rdata", type=str, required=True)
        parser.add_argument("ttl_id", type=str, required=True)
        args = parser.parse_args()
        owner = args["owner"].lower()
        rtype = args["rtype"].lower()
        rdata = args["rdata"]
        zone = args["zone"]
        ttl_id = args["ttl_id"]

        try:
            type_id = type_model.get_typeid_by_rtype(rtype)
            zone_id = zone_model.get_zone_id(zone)
        except Exception as e:
            return response(401, message=str(e))

        try:
            validator.validate(rtype.upper(), rdata)
            record_model.is_duplicate_rdata(zone_id, type_id, rdata)
        except Exception as e:
            return response(401, message=str(e))

        try:
            record_model.is_exists(record_id)
            data = {
                "where": {"id": record_id},
                "data": {
                    "owner": owner,
                    "zone_id": zone_id,
                    "type_id": type_id,
                    "ttl_id": ttl_id,
                },
            }
            content_data = {
                "where": {"record_id": record_id},
                "data": {"rdata": rdata, "record_id": record_id},
            }

            command.send_zone(record_id, "zone-unset")

            model.update("rdata", data=content_data)
            model.update("record", data=data)

            command.send_zone(record_id, "zone-set")

            return response(200, data=data.get("data"), message="Edited")
        except Exception as e:
            return response(401, message=str(e))


class RecordDelete(Resource):
    @auth.auth_required
    def delete(self, record_id):
        """Delete specific record.

        note:
        SOA record can't be deleted. One zone must have minimum one SOA record at time.
        But it can be edited, see`record edit`.
        """
        try:
            record_model.is_exists(record_id)

            rtype = type_model.get_type_by_recordid(record_id)
            if rtype == "SOA":
                return response(401, message=f"Can't Delete SOA Record")

            command.send_zone(record_id, "zone-unset")

            data = model.delete(table="record", field="id", value=record_id)
            return response(200, data=data, message="Deleted")
        except Exception as e:
            return response(401, message=str(e))
