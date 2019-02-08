import json
import requests
from libs import auth
from libs import config
from libs import utils as util
from tabulate import tabulate
import pprint

with open('libs/templates/endpoints.json','r') as model :
    jsonmodel = json.load(model)

def listing_endpoint(endpoint):
    with open('libs/templates/var.json','r') as f :
        var_json = json.load(f)
    url = util.get_url(endpoint)
    headers = auth.get_headers()
    result = requests.get(url, headers=headers['data'])
    result = result.json()
    result = result['data']
    key = var_json['key'][endpoint]
    st = ''
    if result:
        for i in result:
            st += i[key]+'\t'
    else :
        "No value available"
    return st

def get_data(endpoint,key=None,tags=None,value=None):
    headers = auth.get_headers()
    url = util.get_url(endpoint)
    try:
        res = requests.get(url = url, headers = headers['data'] )
        res = res.json()
        res = res['data']

        check = bool(tags)&bool(value)
        data = list()
        if key != None and not check:
            data = list()
            for i in res:
                data.append(i[key])

        elif key == None and check :
            data = list()
            for i in res:
                if i[tags] == value:
                    data.append(i)
        
        elif bool(key)&check:
            for i in res:
                if i[tags] == value:
                    data.append(i[key])
        else :
            data = res
        return util.generate_respons(True,"success",data)

    except Exception as e:
        util.log_err(e)
        return util.generate_respons(False,str(e))

def list_dns():
    id_zone = get_data('userzone',key='id_zone')
    if not 'data' in id_zone:
        return util.generate_respons(False,"You don't own any dns yet")
    

    else :
        id_zone = id_zone['data']
        data = jsonmodel['search']['zone']['data']
        dnslist = list()
        try:
            for i in id_zone:
                data['where']['tags']['id_zone'] = i
                temp = config.send_request('zone', data= data)
                temp = temp['data'][0]['nm_zone']
                dnslist.append(temp)
        except Exception as e:
            print(str(e))
            return util.generate_respons(False,str(e))
    return util.generate_respons(True,"success",dnslist)

# def list_record_need_fix(dnslist, tag = None):
#     dnslist = check_zone_authorization(dnslist)
#     if not 'data' in dnslist.keys():
#         return util.generate_respons(False,"Zone doesn't exist")
#     dnslist = dnslist['data']
#     json_send = jsonmodel['view']['record']   
#     list_var = list()
#     data = dict()
#     for zone in dnslist:
#         data['zone'] = dict()
#         json_send['view']['tags']['nm_zone'] = zone
#         res = config.send_request('record',json_send)
#         if res['data'] is None:
#             print('{} dont have any record' .format(str(zone)))
#         else :
#             res = res['data']
#             for i in res:
#                 if i["nm_type"] not in ["SOA","NS"]:
#                     list_var.append(i)
#     for record in list_var:
#         json_send = jsonmodel['view']['ttldata']
#         json_send['view']['tags']['id_record'] = record['id_record']
#         res = config.send_request('ttldata',json_send)
#         res = res['data']
#         keys = res[0].keys()
#         for key in keys:
#             record[key] = res[0][key]
       
#         json_send = jsonmodel['view']['content_data']
#         json_send['view']['tags']['id_record'] = record['id_record']
#         res = config.send_request('content',json_send)
#         res = res['data']
#         content = ''
#         for i in res:
#             content += i['nm_content']+' '
#         record['nm_content'] = content
#         json_send = jsonmodel['view']['content_serial']
#         json_send['view']['tags']['nm_zone'] = record['nm_zone']
#         res = config.send_request('content_serial', json_send)
#         res = res['data']
#         content_serial = ''
#         if res is not None:
#             for data in res:
#                 if data['nm_type'] == record['nm_type'] :
#                     content_serial += data['nm_content_serial'] + ' '
#         record['nm_content_serial'] = content_serial
        
#     if tag is not None:
#         result = filter_record(list_var,tag)
#         return util.generate_respons(True,'success',result)
#     else :
#         return util.generate_respons(True,'success',list_var)

def check_zone_authorization(dnslist):
    listed = list_dns()
    if not listed['status']:
        return util.generate_respons(True, "No Zone")
    user_dns = listed['data']
    returnlist = list()
    for i in dnslist:
        if i not in user_dns :
            print("You are not authorized to access {}".format(i))
        else :
            returnlist.append(i)

    if not returnlist:
        return util.generate_respons(True,"Success")
    else :
        return util.generate_respons(True,"success",returnlist)
    
def filter_record(data,filter):
    tags = util.get_filter(filter)
    result = list()
    for row in data:
        check = bool(1)
        for tag in tags.keys():
            if row[tag] != tags[tag]:
                check = check & bool(0)
        if check == bool(1):
            row = util.convert(row)
            result.append(row)
    return result                


def list_record(dnslist, tag = None):
    dnslist = check_zone_authorization(dnslist)
    if not 'data' in dnslist.keys():
        return util.generate_respons(False,"Zone doesn't exist")
    dnslist = dnslist['data']
    dnsdata = list()
    recorddata = list()
    
    #get dns data

    for dns in dnslist:
        res = get_data("zone",tags="nm_zone",value=dns)
        res = res['data'][0]
        dnsdata.append(res)

    
    #get record data

    temp = list()
    for dns in dnsdata:
        json_send = jsonmodel['search']['record']['data']
        json_send['where']['tags']['id_zone'] = dns['id_zone']
        res = config.send_request('record',json_send)
        if 'data' not in res:
            print('{} dont have any record' .format(str(dns)))
        else :
            res = res['data']
            for i in res :
                json_send = jsonmodel['view']['record']
                json_send['view']['tags']['id_record'] = i['id_record']
                result = config.send_request('record', json_send)
                result = result['data'][0]
                recorddata.append({**i,**result})
    
    ### GET TTLDATA, CONTENT
    for record in recorddata:
        json_send = jsonmodel['view']['ttldata']
        json_send['view']['tags']['id_record'] = record['id_record']
        res = config.send_request('ttldata',json_send)
        res = res['data'][0]
        record.update(res)

        json_send = jsonmodel['view']['content_data']
        json_send['view']['tags']['id_record']=record['id_record']
        res = config.send_request('content',json_send)
        res = res['data']
        st = ''
        for i in res:
            st += i['nm_content'] + ' '
        record.update({"nm_content" : st})

    for record in recorddata:
        if record['nm_type'] == 'SRV' or record['nm_type'] == 'MX' :
            json_send = jsonmodel['view']['content_serial']
            json_send['view']['tags']['id_record']=record['id_record']
            res = config.send_request('content_serial', json_send)
            res = res['data']
            st = ''
            for row in res:
                st += row['nm_content_serial']
            record.update({"nm_content_serial" : st})

    idx = len(recorddata)-1
    while idx >=0 :
        if recorddata[idx]['nm_type'] == 'SOA' or recorddata[idx]['nm_type'] == 'NS':
            del recorddata[idx]
        idx=idx-1


    if tag is not None:
        result = filter_record(recorddata,tag)
        return util.generate_respons(True,'success',result)
    else :
        return util.generate_respons(True,'success',recorddata)
