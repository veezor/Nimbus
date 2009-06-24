import commands
user_cron = 'root'
script_name = 'speedctl.py'
cron_file = 'custom/nimbus'

class bandwidth_cron:

	def make_bandwidth_restriction():
		fileHandle = open(cron_file,'w')
		if not(fileHandle): return False

		from backup_corporativo.bkp.models import BandwidthRestriction, RestrictionTime, DayOfTheWeek
		restrictions = BandwidthRestriction.objects.all()
		for restriction in restrictions:
			data = ('%s' % restriction).split(" ")
			time = data[0].split(":")
			abr_day = data[1][0:3]
			cron_format = '%s %s * * %s %s %s %s\n' % (time[1],time[0],abr_day,user_cron,script_name,data[2])
			fileHandle.write(cron_format)
		fileHandle.close()

		return True

	# Static Methods
	make =  staticmethod(make_bandwidth_restriction)
