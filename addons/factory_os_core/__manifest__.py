{
    "name": "Factory OS Core",
    "version": "19.0.1.0.0",
    "summary": "Factory OS identity, security, configuration and audit foundation",
    "author": "Factory OS",
    "category": "Manufacturing/Factory OS",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "web",
        "contacts",
        "product",
    ],
    "data": [
        "security/factory_os_security.xml",
        "security/ir.model.access.csv",
        "security/factory_os_rules.xml",
        "views/res_config_settings_views.xml",
        "views/factory_os_menu.xml",
    ],
    "application": True,
    "installable": True,
}
