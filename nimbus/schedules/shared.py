#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly

trigger_map = {
        "monthly" : "mensal",
        "dayly" : "diário",
        "hourly" : "minuto",
        "weekly" : "semanal",
}

trigger_class = {
        "monthly" : Monthly,
        "dayly" : Daily,
        "hourly" : Hourly,
        "weekly" : Weekly,
}
