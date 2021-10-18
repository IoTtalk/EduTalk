# os-EduTalk-Subsystem
## Required Systems
----------------------------------------------------------------------
1. os-IoTtalk
2. os-AutoGen
3. os-EduTalk

Installation
----------------------------------------------------------------------
```
## Install packages in a python 3.6 env
    virtualenv -p python3.6 myvenv
    source ~/myvenv/bin/activate

## Install python Packages
    cd os-EduTalk
    pip install -e .
```
    
Settings
----------------------------------------------------------------------
Set the server parameters in `./edutalk/config.py`. 

```py
#See Line 30
__http_port = 7000  #change to the port you use
__bind = '0.0.0.0'
```

Setup IoTtalk and Autogen endpoint. `./edutalk/config.py`

```py
#See  line 41
__ccm_api = 'http://localhost:7788/api/v0' #change to the port you use
__csm_api = 'http://localhost:9999' #change to the port you use

# line 52
ag_url = 'http://localhost:8080' #change to the port you use
``` 

Set the OAuth information in `./edutalk/config.py`. See `Line 43`

```py
__secret_key = 'edutalk_secret_key'
__client_id = 'your OAuth App ID'
__client_secret = 'your OAuth App secret'
__redirect_uri = 'http(s)://domain or IP/account/auth/callback'
__discovery_endpoint = 'OAuth discover Endpoint'
__revocation_endpoint = 'OAuth revoke token Endpoint'
```

Set the informatioin in `./os-EduTalk/edutalk/static/js/rc/main.js`. See `Line 33`
`csmapi.set_endpoint('http://domain or IP:9999');`

Set the informatioin in `./os-EduTalk/edutalk/static/js/vp-resource/app.js`. See `Line 1`
`csmapi.set_endpoint('http://domain or IP:9999');`

```py
#See  line 41
__ccm_api = 'http://localhost:7788/api/v0' #change to the port you use
__csm_api = 'http://localhost:9999' #change to the port you use

# line 52
ag_url = 'http://localhost:8080' #change to the port you use
``` 

Set the OAuth information in `./edutalk/config.py`. See `Line 43`

```py
__secret_key = 'edutalk_secret_key'
__client_id = 'your OAuth App ID'
__client_secret = 'your OAuth App secret'
__redirect_uri = 'http(s)://domain or IP/account/auth/callback'
__discovery_endpoint = 'OAuth discover Endpoint'
__revocation_endpoint = 'OAuth revoke token Endpoint'
```

Set the informatioin in `./os-EduTalk/edutalk/static/js/rc/main.js`. See `Line 33`
`csmapi.set_endpoint('http://domain or IP:9999');`

Set the informatioin in `./os-EduTalk/edutalk/static/js/vp-resource/app.js`. See `Line 1`
`csmapi.set_endpoint('http://domain or IP:9999');`

Initialization db
----------------------------------------------------------------------
    python ./edutalk/cli.py initdb

> if initdb failed，delete your edutalk db before you retry.
    
Start server
----------------------------------------------------------------------
    eduatlk start
