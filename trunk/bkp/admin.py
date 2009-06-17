from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.models import FileSet
from backup_corporativo.bkp.models import Pool
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.models import WeeklyTrigger
from backup_corporativo.bkp.models import MonthlyTrigger


from django.contrib import admin

admin.site.register(Computer)
admin.site.register(Procedure)
admin.site.register(FileSet)
admin.site.register(Pool)
admin.site.register(Schedule)
admin.site.register(WeeklyTrigger)
admin.site.register(MonthlyTrigger)
