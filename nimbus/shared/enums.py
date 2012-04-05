#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.utils.translation import ugettext_lazy as _
days = range(1, 32)

weekdays = ("sun","mon","tue","wed","fri", "thu" ,"sat")
week_dict = {0: 'sunday', #used in bacula conf
             1: 'monday',
             2: 'tuesday',
             3: 'wednesday',
             4: 'thursday',
             5: 'friday',
             6: 'saturday'}


levels = ("Full", "Incremental")

operating_systems = ("unix", "windows")

days_range = range(1, 32)
weekdays_range = {0:_(u'Sunday'),
                  1:_(u'Monday'),
                  2:_(u'Tuesday'),
                  3:_(u'Wednesday'),
                  4:_(u'Thusday'),
                  5:_(u'Friday'),
                  6:_(u'Saturday')}
end_days_range = [5, 10, 15, 20, 25, 30]
