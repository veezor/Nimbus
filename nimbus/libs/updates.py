#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import apt

NIMBUS_PACKAGES = ["bacula-nimbus", "nimbus", "nimbus-dependencies"]


def check_updates(*packages):
    """ check in apt-cache new updates for packages.
    a bit slow"""

    cache = apt.Cache()
    return [ bool(cache[pkg].is_upgradable) for pkg in packages  ]



def check_nimbus_updates():

    has_updates = check_updates(*NIMBUS_PACKAGES)
    return dict(zip(NIMBUS_PACKAGES,has_updates))



def get_upgradable_nimbus_packages():
    status = check_nimbus_updates()
    return [ k for k,v in status.items() if v ]



def has_nimbus_updates():
    return any(check_updates(*NIMBUS_PACKAGES))



