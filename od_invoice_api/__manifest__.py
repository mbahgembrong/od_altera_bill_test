# -*- coding: utf-8 -*-
{
    'name': "Custom Invoice API",

    'author': "hams",
    'website': "http://www.hamserver.cloud",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_rest_datamodel', 'base_rest_auth_api_key', 'account', 'queue_job'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
