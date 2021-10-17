import edutalk.utils as utils
import logging
from edutalk.exceptions import CCMAPIError

log = logging.getLogger('edutalk.ag_ccmapi')

def _json(api_name, payload):
    data = {
        "api_name": api_name,
        "payload": payload
    }
    return data

'''
APIs for "device"

APIs:
    device.get
    device.bind
    device.unbind
'''

class device():
    def get(p_id, do_id, api_name='device.get'):
        payload = {
            "p_id": p_id,
            "do_id": do_id,
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Getting Device info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']


    def bind(p_id, do_id, d_id, api_name='device.bind'):
        payload = {
            "p_id": p_id,
            "do_id": do_id,
            "d_id": d_id
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Bind Device failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def unbind(p_id, do_id, api_name='device.unbind'):
        payload = {
            "p_id": p_id,
            "do_id": do_id
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError 
        except CCMAPIError:
            log.exception("Bind Device failed.")
        except Exception as err:
            log.exception(err)
        return response['result']



'''
APIs for "project"

APIs:
    project.get
    project.create
    project.delete
    project.on
    project.off
'''  

class project():
    def get(p_id, api_name='project.get'):
        payload = {
            "p_id": p_id,
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Getting Project info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def create(name, api_name='project.create'):
        payload = {
            "p_name": name,
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create Project failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def delete(p_id, api_name='project.delete'):
        payload = {
            "p_id": p_id,
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Delete Project failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def on(p_id, api_name='project.on'):
        payload = {
            "p_id": p_id,
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Turn on Project failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def off(p_id, api_name='project.off'):
        payload = {
            "p_id": p_id,
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Turn off Project failed.")
        except Exception as err:
            log.exception(err)
        return response['result']


'''
APIs for "deviceobject"

APIs:
    deviceobject.get
    deviceobject.create
    deviceobject.delete

'''  

class deviceobject():
    def get(p_id, do_id, api_name='deviceobject.get'):
        payload = {
            "p_id": p_id,
            "do_id": do_id
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Getting Deviceobject info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def create(p_id, dm_name: str, dfs: list= [] ,api_name='deviceobject.create'):
        payload = {
            "p_id": p_id,
            "dm_name": dm_name,
            "dfs": dfs
        }

        if not dfs: # if dfs is not assigned, get all dfs
            payload['dfs'] = [df['df_name'] for df in devicemodel.get(dm_name)['df_list']]

        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create Deviceobject failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def delete(p_id, do_id ,api_name='deviceobject.create'):
        payload = {
            "p_id": p_id,
            "do_id": do_id
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create Deviceobject failed.")
        except Exception as err:
            log.exception(err)
        return response['result']


'''
APIs for "devicefeature"

APIs:
    devicefeature.get
    devicefeature.create
    devicefeature.update

'''  

class devicefeature():
    def get(df, api_name='devicefeature.get'):
        payload = {
            "df": df
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Getting Devicefeature info failed.")
            return response
        except Exception as err:
            log.exception(err)
        return response['result']

    def create(name, type, parameter, comment="", category="Other", api_name='devicefeature.create'):
        payload = {
            "df_name": name,
            "type": type,
            "parameter": parameter,
            "comment": comment,
            "category": category
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create Devicefeature info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def get_or_create(df_name: str, typ, parameter):
        try:
            return devicefeature.get(df_name)
        except CCMAPIError as e:
            log.exception("Get or create Devicefeature info failed.")
        print("Did not get")
        return devicefeature.get(devicefeature.create(df_name, typ, parameter))


    def update(df_id, df_name, df_type, parameter, api_name='devicefeature.update'):
        payload = {
            "df_id": df_id,
            "df_name": df_name,
            "df_type": df_type,
            "parameter": parameter
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Update Devicefeature info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']



'''
APIs for "networkapplication"

APIs:
    networkapplication.get
    networkapplication.create
    networkapplication.delete

'''  

class networkapplication():
    def get(p_id, na_id, api_name='networkapplication.get'):
        payload = {
            "p_id": p_id,
            "na_id": na_id
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Getting NetworkApplication info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def create(p_id, joins, api_name='networkapplication.create'):
        payload = {
            "p_id": p_id,
            "joins": joins
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create NetworkApplication info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def delete(p_id, na_id, api_name='networkapplication.delete'):
        payload = {
            "p_id": p_id,
            "na_id": na_id
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError   
        except CCMAPIError:
            log.exception("Deley NetworkApplication info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']



'''
APIs for "devicemodel"

APIs:
    devicemodel.get
    devicemodel.create
    devicemodel.delete
    devicemodel.update

'''  

class devicemodel():
    def get(dm, api_name='devicemodel.get'):
        payload = {
            "dm": dm
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
            return response['result']
        except CCMAPIError:
            log.exception("Getting DeviceModel info failed.")
            return response
        except Exception as err:
            log.exception(err)

    def create(name, dfs, api_name='devicemodel.create'):
        payload = {
            "dm_name": name,
            "dfs": dfs
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create DeviceModel info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def delete(dm, api_name='devicemodel.delete'):
        payload = {
            "dm": dm
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Delete DeviceModel info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']

    def update(dm_id, dm_name, dfs, api_name='devicemodel.update'):
        payload = {
            "dn_id": dm_id,
            "dm_name": dm_name,
            "dfs": dfs
        }
        
        try:
            status, response = utils.ag_post(_json(api_name, payload))
            if not status:
                raise CCMAPIError
        except CCMAPIError:
            log.exception("Create DeviceModel info failed.")
        except Exception as err:
            log.exception(err)
        return response['result']
