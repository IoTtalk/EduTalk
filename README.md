# os-EduTalk-Subsystem

Installation
----------------------------------------------------------------------

    cd edutalk 
    pip install -e .
    
Settings
----------------------------------------------------------------------
Set the information in `./edutalk/config.py`. See `Line 43`

```py
__secret_key = 'edutalk_secret_key'
__client_id = 'your OAuth App ID'
__client_secret = 'your OAuth App secret'
__redirect_uri = 'http(s)://domain or IP/account/auth/callback'
__discovery_endpoint = 'OAuth discover Endpoint'
__revocation_endpoint = 'OAuth revoke token Endpoint'
```

Initialization
----------------------------------------------------------------------

    python cli.py initdb
    
Start server
----------------------------------------------------------------------

    python cli.py start
