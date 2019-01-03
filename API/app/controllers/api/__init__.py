from flask import Blueprint
from flask_restful import Api
from .user import *
from .auth import *
from .zone import *
from .type import *
from .ttl import *
from .record import *
from .ttldata import *
from .content import *
from .content_serial import *
#from .command import *
from .dns.create import *
from .command_rest import *


api_blueprint = Blueprint("api", __name__, url_prefix='/api')
api = Api(api_blueprint)
api.add_resource(UserdataResource, '/user')
api.add_resource(UserdataResourceById, '/user/<userdata_id>')
api.add_resource(UserdataInsert, '/user')
api.add_resource(UserdataUpdate, '/user/<userdata_id>')
api.add_resource(UserdataRemove, '/user/<userdata_id>')

api.add_resource(Usersignin, '/sign')
api.add_resource(UserTokenRefresh, '/sign/token')
api.add_resource(UserloginInsert, '/user/add')

api.add_resource(ZoneName, '/zone')
api.add_resource(Type, '/type')
api.add_resource(TtlName, '/ttl')
api.add_resource(Record, '/record')
api.add_resource(TtlData, '/ttldata')
api.add_resource(Content, '/content')
api.add_resource(ContentSerial, '/content_serial')

#api.add_resource(SendCommand, '/sendsocket')
api.add_resource(SendCommandRest, '/sendcommand')
api.add_resource(CreateDNS, '/user/dnscreate')
