# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Client'
        db.create_table(u'Client', (
            ('clientid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='ClientId')),
            ('name', self.gf('django.db.models.fields.TextField')(unique=True, db_column='Name')),
            ('uname', self.gf('django.db.models.fields.TextField')(db_column='Uname')),
            ('autoprune', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='AutoPrune', blank=True)),
            ('fileretention', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='FileRetention', blank=True)),
            ('jobretention', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='JobRetention', blank=True)),
        ))
        db.send_create_signal('bacula', ['Client'])

        # Adding model 'File'
        db.create_table(u'File', (
            ('fileid', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True, db_column='FileId')),
            ('fileindex', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='FileIndex', blank=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Job'], db_column='JobId')),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Path'], db_column='PathId')),
            ('filename', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Filename'], db_column='FilenameId')),
            ('markid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MarkId', blank=True)),
            ('lstat', self.gf('django.db.models.fields.TextField')(db_column='LStat')),
            ('md5', self.gf('django.db.models.fields.TextField')(db_column='MD5', blank=True)),
        ))
        db.send_create_signal('bacula', ['File'])

        # Adding model 'Fileset'
        db.create_table(u'FileSet', (
            ('filesetid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='FileSetId')),
            ('fileset', self.gf('django.db.models.fields.TextField')(db_column='FileSet')),
            ('md5', self.gf('django.db.models.fields.TextField')(db_column='MD5', blank=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='CreateTime', blank=True)),
        ))
        db.send_create_signal('bacula', ['Fileset'])

        # Adding model 'Filename'
        db.create_table(u'Filename', (
            ('filenameid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='FilenameId')),
            ('name', self.gf('django.db.models.fields.TextField')(db_column='Name')),
        ))
        db.send_create_signal('bacula', ['Filename'])

        # Adding model 'Job'
        db.create_table(u'Job', (
            ('jobid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='JobId')),
            ('job', self.gf('django.db.models.fields.TextField')(db_column='Job')),
            ('name', self.gf('django.db.models.fields.TextField')(db_column='Name')),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1, db_column='Type')),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=1, db_column='Level')),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Client'], null=True, db_column='ClientId', blank=True)),
            ('jobstatus', self.gf('django.db.models.fields.CharField')(max_length=1, db_column='JobStatus')),
            ('schedtime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='SchedTime', blank=True)),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='StartTime', blank=True)),
            ('endtime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='EndTime', blank=True)),
            ('realendtime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='RealEndTime', blank=True)),
            ('jobtdate', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='JobTDate', blank=True)),
            ('volsessionid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolSessionId', blank=True)),
            ('volsessiontime', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolSessionTime', blank=True)),
            ('jobfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='JobFiles', blank=True)),
            ('jobbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='JobBytes', blank=True)),
            ('readbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='ReadBytes', blank=True)),
            ('joberrors', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='JobErrors', blank=True)),
            ('jobmissingfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='JobMissingFiles', blank=True)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Pool'], null=True, db_column='PoolId', blank=True)),
            ('fileset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Fileset'], null=True, db_column='FileSetId', blank=True)),
            ('priorjobid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='PriorJobId', blank=True)),
            ('purgedfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='PurgedFiles', blank=True)),
            ('hasbase', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='HasBase', blank=True)),
        ))
        db.send_create_signal('bacula', ['Job'])

        # Adding model 'JobMedia'
        db.create_table(u'JobMedia', (
            ('jobmediaid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='JobMediaId')),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Job'], db_column='JobId')),
            ('media', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Media'], db_column='MediaId')),
            ('firstindex', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='FirstIndex', blank=True)),
            ('lastindex', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='LastIndex', blank=True)),
            ('startfile', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='StartFile', blank=True)),
            ('endfile', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='EndFile', blank=True)),
            ('startblock', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='StartBlock', blank=True)),
            ('endblock', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='EndBlock', blank=True)),
            ('volindex', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolIndex', blank=True)),
            ('copy', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Copy', blank=True)),
            ('stripe', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Stripe', blank=True)),
        ))
        db.send_create_signal('bacula', ['JobMedia'])

        # Adding model 'Media'
        db.create_table(u'Media', (
            ('mediaid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='MediaId')),
            ('volumename', self.gf('django.db.models.fields.TextField')(unique=True, db_column='VolumeName')),
            ('slot', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Slot', blank=True)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Pool'], null=True, db_column='PoolId', blank=True)),
            ('mediatype', self.gf('django.db.models.fields.TextField')(db_column='MediaType')),
            ('mediatypeid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MediaTypeId', blank=True)),
            ('labeltype', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='LabelType', blank=True)),
            ('firstwritten', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='FirstWritten', blank=True)),
            ('lastwritten', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='LastWritten', blank=True)),
            ('labeldate', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='LabelDate', blank=True)),
            ('voljobs', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolJobs', blank=True)),
            ('volfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolFiles', blank=True)),
            ('volblocks', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolBlocks', blank=True)),
            ('volmounts', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolMounts', blank=True)),
            ('volbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolBytes', blank=True)),
            ('volparts', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolParts', blank=True)),
            ('volerrors', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolErrors', blank=True)),
            ('volwrites', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolWrites', blank=True)),
            ('volcapacitybytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolCapacityBytes', blank=True)),
            ('volstatus', self.gf('django.db.models.fields.CharField')(max_length=27, db_column='VolStatus')),
            ('enabled', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Enabled', blank=True)),
            ('recycle', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Recycle', blank=True)),
            ('actiononpurge', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='ActionOnPurge', blank=True)),
            ('volretention', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolRetention', blank=True)),
            ('voluseduration', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolUseDuration', blank=True)),
            ('maxvoljobs', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MaxVolJobs', blank=True)),
            ('maxvolfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MaxVolFiles', blank=True)),
            ('maxvolbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='MaxVolBytes', blank=True)),
            ('inchanger', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='InChanger', blank=True)),
            ('storageid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='StorageId', blank=True)),
            ('deviceid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='DeviceId', blank=True)),
            ('mediaaddressing', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MediaAddressing', blank=True)),
            ('volreadtime', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolReadTime', blank=True)),
            ('volwritetime', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolWriteTime', blank=True)),
            ('endfile', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='EndFile', blank=True)),
            ('endblock', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='EndBlock', blank=True)),
            ('locationid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='LocationId', blank=True)),
            ('recyclecount', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='RecycleCount', blank=True)),
            ('initialwrite', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='InitialWrite', blank=True)),
            ('scratchpoolid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='ScratchPoolId', blank=True)),
            ('recyclepoolid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='RecyclePoolId', blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(db_column='Comment', blank=True)),
        ))
        db.send_create_signal('bacula', ['Media'])

        # Adding model 'Path'
        db.create_table(u'Path', (
            ('pathid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='PathId')),
            ('path', self.gf('django.db.models.fields.TextField')(db_column='Path')),
        ))
        db.send_create_signal('bacula', ['Path'])

        # Adding model 'Pool'
        db.create_table(u'Pool', (
            ('poolid', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='PoolId')),
            ('name', self.gf('django.db.models.fields.TextField')(unique=True, db_column='Name')),
            ('numvols', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='NumVols', blank=True)),
            ('maxvols', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MaxVols', blank=True)),
            ('useonce', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='UseOnce', blank=True)),
            ('usecatalog', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='UseCatalog', blank=True)),
            ('acceptanyvolume', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='AcceptAnyVolume', blank=True)),
            ('volretention', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolRetention', blank=True)),
            ('voluseduration', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='VolUseDuration', blank=True)),
            ('maxvoljobs', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MaxVolJobs', blank=True)),
            ('maxvolfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='MaxVolFiles', blank=True)),
            ('maxvolbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='MaxVolBytes', blank=True)),
            ('autoprune', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='AutoPrune', blank=True)),
            ('recycle', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Recycle', blank=True)),
            ('actiononpurge', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='ActionOnPurge', blank=True)),
            ('pooltype', self.gf('django.db.models.fields.CharField')(max_length=27, db_column='PoolType')),
            ('labeltype', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='LabelType', blank=True)),
            ('labelformat', self.gf('django.db.models.fields.TextField')(db_column='LabelFormat', blank=True)),
            ('enabled', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Enabled', blank=True)),
            ('scratchpoolid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='ScratchPoolId', blank=True)),
            ('recyclepoolid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='RecyclePoolId', blank=True)),
            ('nextpoolid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='NextPoolId', blank=True)),
            ('migrationhighbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='MigrationHighBytes', blank=True)),
            ('migrationlowbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='MigrationLowBytes', blank=True)),
            ('migrationtime', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='MigrationTime', blank=True)),
        ))
        db.send_create_signal('bacula', ['Pool'])

        # Adding model 'Temp'
        db.create_table(u'temp', (
            ('jobid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Job'], primary_key=True, db_column='JobId')),
            ('jobtdate', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='JobTDate', blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Client'], db_column='ClientId')),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=3, db_column='Level')),
            ('jobfiles', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='JobFiles', blank=True)),
            ('jobbytes', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='JobBytes', blank=True)),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='StartTime', blank=True)),
            ('volumename', self.gf('django.db.models.fields.CharField')(max_length=384, db_column='VolumeName')),
            ('startfile', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='StartFile', blank=True)),
            ('volsessionid', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolSessionId', blank=True)),
            ('volsessiontime', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='VolSessionTime', blank=True)),
        ))
        db.send_create_signal('bacula', ['Temp'])

        # Adding model 'Temp1'
        db.create_table(u'temp1', (
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bacula.Job'], primary_key=True, db_column='JobId')),
            ('jobtdate', self.gf('django.db.models.fields.BigIntegerField')(null=True, db_column='JobTDate', blank=True)),
        ))
        db.send_create_signal('bacula', ['Temp1'])


    def backwards(self, orm):
        
        # Deleting model 'Client'
        db.delete_table(u'Client')

        # Deleting model 'File'
        db.delete_table(u'File')

        # Deleting model 'Fileset'
        db.delete_table(u'FileSet')

        # Deleting model 'Filename'
        db.delete_table(u'Filename')

        # Deleting model 'Job'
        db.delete_table(u'Job')

        # Deleting model 'JobMedia'
        db.delete_table(u'JobMedia')

        # Deleting model 'Media'
        db.delete_table(u'Media')

        # Deleting model 'Path'
        db.delete_table(u'Path')

        # Deleting model 'Pool'
        db.delete_table(u'Pool')

        # Deleting model 'Temp'
        db.delete_table(u'temp')

        # Deleting model 'Temp1'
        db.delete_table(u'temp1')


    models = {
        'bacula.client': {
            'Meta': {'object_name': 'Client', 'db_table': "u'Client'"},
            'autoprune': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'AutoPrune'", 'blank': 'True'}),
            'clientid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'ClientId'"}),
            'fileretention': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'FileRetention'", 'blank': 'True'}),
            'jobretention': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'JobRetention'", 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_column': "'Name'"}),
            'uname': ('django.db.models.fields.TextField', [], {'db_column': "'Uname'"})
        },
        'bacula.file': {
            'Meta': {'object_name': 'File', 'db_table': "u'File'"},
            'fileid': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_column': "'FileId'"}),
            'fileindex': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'FileIndex'", 'blank': 'True'}),
            'filename': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Filename']", 'db_column': "'FilenameId'"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Job']", 'db_column': "'JobId'"}),
            'lstat': ('django.db.models.fields.TextField', [], {'db_column': "'LStat'"}),
            'markid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MarkId'", 'blank': 'True'}),
            'md5': ('django.db.models.fields.TextField', [], {'db_column': "'MD5'", 'blank': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Path']", 'db_column': "'PathId'"})
        },
        'bacula.filename': {
            'Meta': {'object_name': 'Filename', 'db_table': "u'Filename'"},
            'filenameid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'FilenameId'"}),
            'name': ('django.db.models.fields.TextField', [], {'db_column': "'Name'"})
        },
        'bacula.fileset': {
            'Meta': {'object_name': 'Fileset', 'db_table': "u'FileSet'"},
            'createtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'CreateTime'", 'blank': 'True'}),
            'fileset': ('django.db.models.fields.TextField', [], {'db_column': "'FileSet'"}),
            'filesetid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'FileSetId'"}),
            'md5': ('django.db.models.fields.TextField', [], {'db_column': "'MD5'", 'blank': 'True'})
        },
        'bacula.job': {
            'Meta': {'object_name': 'Job', 'db_table': "u'Job'"},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Client']", 'null': 'True', 'db_column': "'ClientId'", 'blank': 'True'}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'EndTime'", 'blank': 'True'}),
            'fileset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Fileset']", 'null': 'True', 'db_column': "'FileSetId'", 'blank': 'True'}),
            'hasbase': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'HasBase'", 'blank': 'True'}),
            'job': ('django.db.models.fields.TextField', [], {'db_column': "'Job'"}),
            'jobbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'JobBytes'", 'blank': 'True'}),
            'joberrors': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'JobErrors'", 'blank': 'True'}),
            'jobfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'JobFiles'", 'blank': 'True'}),
            'jobid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'JobId'"}),
            'jobmissingfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'JobMissingFiles'", 'blank': 'True'}),
            'jobstatus': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "'JobStatus'"}),
            'jobtdate': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'JobTDate'", 'blank': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "'Level'"}),
            'name': ('django.db.models.fields.TextField', [], {'db_column': "'Name'"}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Pool']", 'null': 'True', 'db_column': "'PoolId'", 'blank': 'True'}),
            'priorjobid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'PriorJobId'", 'blank': 'True'}),
            'purgedfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'PurgedFiles'", 'blank': 'True'}),
            'readbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'ReadBytes'", 'blank': 'True'}),
            'realendtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'RealEndTime'", 'blank': 'True'}),
            'schedtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'SchedTime'", 'blank': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'StartTime'", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "'Type'"}),
            'volsessionid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolSessionId'", 'blank': 'True'}),
            'volsessiontime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolSessionTime'", 'blank': 'True'})
        },
        'bacula.jobmedia': {
            'Meta': {'object_name': 'JobMedia', 'db_table': "u'JobMedia'"},
            'copy': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Copy'", 'blank': 'True'}),
            'endblock': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'EndBlock'", 'blank': 'True'}),
            'endfile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'EndFile'", 'blank': 'True'}),
            'firstindex': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'FirstIndex'", 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Job']", 'db_column': "'JobId'"}),
            'jobmediaid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'JobMediaId'"}),
            'lastindex': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'LastIndex'", 'blank': 'True'}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Media']", 'db_column': "'MediaId'"}),
            'startblock': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'StartBlock'", 'blank': 'True'}),
            'startfile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'StartFile'", 'blank': 'True'}),
            'stripe': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Stripe'", 'blank': 'True'}),
            'volindex': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolIndex'", 'blank': 'True'})
        },
        'bacula.media': {
            'Meta': {'object_name': 'Media', 'db_table': "u'Media'"},
            'actiononpurge': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ActionOnPurge'", 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'db_column': "'Comment'", 'blank': 'True'}),
            'deviceid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'DeviceId'", 'blank': 'True'}),
            'enabled': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Enabled'", 'blank': 'True'}),
            'endblock': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'EndBlock'", 'blank': 'True'}),
            'endfile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'EndFile'", 'blank': 'True'}),
            'firstwritten': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'FirstWritten'", 'blank': 'True'}),
            'inchanger': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'InChanger'", 'blank': 'True'}),
            'initialwrite': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'InitialWrite'", 'blank': 'True'}),
            'labeldate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'LabelDate'", 'blank': 'True'}),
            'labeltype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'LabelType'", 'blank': 'True'}),
            'lastwritten': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'LastWritten'", 'blank': 'True'}),
            'locationid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'LocationId'", 'blank': 'True'}),
            'maxvolbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'MaxVolBytes'", 'blank': 'True'}),
            'maxvolfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MaxVolFiles'", 'blank': 'True'}),
            'maxvoljobs': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MaxVolJobs'", 'blank': 'True'}),
            'mediaaddressing': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MediaAddressing'", 'blank': 'True'}),
            'mediaid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'MediaId'"}),
            'mediatype': ('django.db.models.fields.TextField', [], {'db_column': "'MediaType'"}),
            'mediatypeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MediaTypeId'", 'blank': 'True'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Pool']", 'null': 'True', 'db_column': "'PoolId'", 'blank': 'True'}),
            'recycle': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Recycle'", 'blank': 'True'}),
            'recyclecount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'RecycleCount'", 'blank': 'True'}),
            'recyclepoolid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'RecyclePoolId'", 'blank': 'True'}),
            'scratchpoolid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ScratchPoolId'", 'blank': 'True'}),
            'slot': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Slot'", 'blank': 'True'}),
            'storageid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'StorageId'", 'blank': 'True'}),
            'volblocks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolBlocks'", 'blank': 'True'}),
            'volbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolBytes'", 'blank': 'True'}),
            'volcapacitybytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolCapacityBytes'", 'blank': 'True'}),
            'volerrors': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolErrors'", 'blank': 'True'}),
            'volfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolFiles'", 'blank': 'True'}),
            'voljobs': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolJobs'", 'blank': 'True'}),
            'volmounts': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolMounts'", 'blank': 'True'}),
            'volparts': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolParts'", 'blank': 'True'}),
            'volreadtime': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolReadTime'", 'blank': 'True'}),
            'volretention': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolRetention'", 'blank': 'True'}),
            'volstatus': ('django.db.models.fields.CharField', [], {'max_length': '27', 'db_column': "'VolStatus'"}),
            'volumename': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_column': "'VolumeName'"}),
            'voluseduration': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolUseDuration'", 'blank': 'True'}),
            'volwrites': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolWrites'", 'blank': 'True'}),
            'volwritetime': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolWriteTime'", 'blank': 'True'})
        },
        'bacula.path': {
            'Meta': {'object_name': 'Path', 'db_table': "u'Path'"},
            'path': ('django.db.models.fields.TextField', [], {'db_column': "'Path'"}),
            'pathid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'PathId'"})
        },
        'bacula.pool': {
            'Meta': {'object_name': 'Pool', 'db_table': "u'Pool'"},
            'acceptanyvolume': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'AcceptAnyVolume'", 'blank': 'True'}),
            'actiononpurge': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ActionOnPurge'", 'blank': 'True'}),
            'autoprune': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'AutoPrune'", 'blank': 'True'}),
            'enabled': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Enabled'", 'blank': 'True'}),
            'labelformat': ('django.db.models.fields.TextField', [], {'db_column': "'LabelFormat'", 'blank': 'True'}),
            'labeltype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'LabelType'", 'blank': 'True'}),
            'maxvolbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'MaxVolBytes'", 'blank': 'True'}),
            'maxvolfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MaxVolFiles'", 'blank': 'True'}),
            'maxvoljobs': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MaxVolJobs'", 'blank': 'True'}),
            'maxvols': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'MaxVols'", 'blank': 'True'}),
            'migrationhighbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'MigrationHighBytes'", 'blank': 'True'}),
            'migrationlowbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'MigrationLowBytes'", 'blank': 'True'}),
            'migrationtime': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'MigrationTime'", 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_column': "'Name'"}),
            'nextpoolid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'NextPoolId'", 'blank': 'True'}),
            'numvols': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'NumVols'", 'blank': 'True'}),
            'poolid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'PoolId'"}),
            'pooltype': ('django.db.models.fields.CharField', [], {'max_length': '27', 'db_column': "'PoolType'"}),
            'recycle': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Recycle'", 'blank': 'True'}),
            'recyclepoolid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'RecyclePoolId'", 'blank': 'True'}),
            'scratchpoolid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ScratchPoolId'", 'blank': 'True'}),
            'usecatalog': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'UseCatalog'", 'blank': 'True'}),
            'useonce': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'UseOnce'", 'blank': 'True'}),
            'volretention': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolRetention'", 'blank': 'True'}),
            'voluseduration': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'VolUseDuration'", 'blank': 'True'})
        },
        'bacula.temp': {
            'Meta': {'object_name': 'Temp', 'db_table': "u'temp'"},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Client']", 'db_column': "'ClientId'"}),
            'jobbytes': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'JobBytes'", 'blank': 'True'}),
            'jobfiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'JobFiles'", 'blank': 'True'}),
            'jobid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Job']", 'primary_key': 'True', 'db_column': "'JobId'"}),
            'jobtdate': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'JobTDate'", 'blank': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_column': "'Level'"}),
            'startfile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'StartFile'", 'blank': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'StartTime'", 'blank': 'True'}),
            'volsessionid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolSessionId'", 'blank': 'True'}),
            'volsessiontime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'VolSessionTime'", 'blank': 'True'}),
            'volumename': ('django.db.models.fields.CharField', [], {'max_length': '384', 'db_column': "'VolumeName'"})
        },
        'bacula.temp1': {
            'Meta': {'object_name': 'Temp1', 'db_table': "u'temp1'"},
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bacula.Job']", 'primary_key': 'True', 'db_column': "'JobId'"}),
            'jobtdate': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'db_column': "'JobTDate'", 'blank': 'True'})
        }
    }

    complete_apps = ['bacula']
