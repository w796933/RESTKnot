from flask_restful import Resource, reqparse, inputs
from app.helpers.rest import response
from app.models import model
from app.models import zone as zone_model
from app.libs import validation
from app.middlewares import auth


def get_datum(data):
    if data is None:
        return

    results = []
    for d in data:
        # FIXME add created_at?
        datum = {
            "id": str(d["id"]),
            "owner": d["record"],
            "zone_id": d["zone_id"],
            "type_id": d["type_id"],
            "ttl_id": d["ttl_id"],
        }
        results.append(datum)
    return results


def is_duplicate(owner, zone_id):
    query = 'SELECT * FROM "record" WHERE "zone_id"=%(zone_id)s AND "owner"=%(owner)s'
    value = {"zone_id": zone_id, "owner": owner}
    mx_records = model.plain_get(query, value)
    if len(mx_records) >= 1:
        return True

    return False


def get_typeid(record):
    try:
        type_ = model.get_by_condition(table="type", field="type", value=record.upper())
        type_id = type_[0]["id"]
        return type_id
    except Exception:
        return response(401, message="Record Unrecognized")


class GetRecordData(Resource):
    @auth.auth_required
    def get(self):
        try:
            records = model.get_all("record")
        except Exception as e:
            return response(401, message=str(e))

        results = []
        for record in records:
            zone = model.get_by_condition(
                table="zone", field="id", value=record["zone_id"]
            )
            ttl = model.get_by_condition(
                table="ttl", field="id", value=record["ttl_id"]
            )
            type_ = model.get_by_condition(
                table="type", field="id", value=record["type_id"]
            )

            data = {
                "id": record["id"],
                "owner": record["owner"],
                "zone": zone,
                "type": type_,
                "ttl": ttl,
            }
            results.append(data)

        return response(200, data=results)


class GetRecordDataId(Resource):
    @auth.auth_required
    def get(self, record_id):
        try:
            # data_record = model.read_by_id("record", key)
            records = model.get_by_condition(
                table="record", field="id", value=record_id
            )
        except Exception as e:
            return response(401, message=str(e))
        else:
            data = get_datum(records)
            return response(200, data=data)


class RecordAdd(Resource):
    @auth.auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("zone", type=str, required=True)
        parser.add_argument("owner", type=str, required=True)
        parser.add_argument("rtype", type=str, required=True)
        parser.add_argument("rdata", type=str, required=True)
        parser.add_argument("ttl_id", type=str, required=True)
        args = parser.parse_args()
        owner = args["owner"].lower()
        rtype = args["rtype"].lower()
        zone = args["zone"]
        ttl_id = args["ttl_id"]

        type_id = get_typeid(rtype)

        try:
            zone_id = zone_model.get_zone_id(zone)
        except Exception as e:
            return response(401, message=str(e))

        if validation.record_validation(rtype):
            return response(401, message="Named Error")
        if validation.count_character(rtype):
            return response(401, message="Count Character Error")

        if rtype == "mx" or rtype == "cname":
            if is_duplicate(rtype, zone_id):
                return response(401, message="Duplicate Record found")

        try:
            data = {
                "owner": owner,
                "zone_id": zone_id,
                "type_id": type_id,
                "ttl_id": ttl_id,
            }
            model.insert(table="record", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Inserted")


class RecordEdit(Resource):
    @auth.auth_required
    def put(self, record_id):
        parser = reqparse.RequestParser()
        parser.add_argument("record", type=str, required=True)
        parser.add_argument("zone_id", type=str, required=True)
        parser.add_argument("ttl_id", type=str, required=True)
        args = parser.parse_args()

        record = args["record"].lower()
        zone_id = args["zone_id"]
        ttl_id = args["ttl_id"]

        type_id = get_typeid(record)

        if validation.record_validation(record):
            return response(401, message="Named Error")
        if validation.count_character(record):
            return response(401, message="Count Character Error")

        if record == "mx" or record == "cname":
            if is_duplicate(record, zone_id):
                return response(401, message="Duplicate Record found")
        data = {
            "where": {"id": record_id},
            "data": {
                "owner": record,
                "zone_id": zone_id,
                "type_id": type_id,
                "ttl_id": ttl_id,
            },
        }

        try:
            model.update("record", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Edited")


class RecordDelete(Resource):
    @auth.auth_required
    def delete(self, record_id):
        try:
            data = model.delete(table="record", field="id", value=record_id)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Deleted")
