from odoo.addons.base_rest.controllers import main

class V1Private(main.RestController):
    _root_path = '/api/v1/private/'
    _collection_name = "v1.private"
    _default_auth = "api_key"
    
