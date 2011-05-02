# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Offsite'
        db.create_table('offsite_offsite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('gateway_url', self.gf('django.db.models.fields.CharField')(default='http://www.veezor.com:8080', max_length=255)),
            ('upload_rate', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('offsite', ['Offsite'])

        # Adding model 'Volume'
        db.create_table('offsite_volume', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('nimbus.shared.fields.ModelPathField')(max_length=2048)),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('offsite', ['Volume'])

        # Adding model 'UploadedVolume'
        db.create_table('offsite_uploadedvolume', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.Volume'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('offsite', ['UploadedVolume'])

        # Adding model 'DownloadedVolume'
        db.create_table('offsite_downloadedvolume', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.Volume'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('offsite', ['DownloadedVolume'])

        # Adding model 'RemoteUploadRequest'
        db.create_table('offsite_remoteuploadrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.Volume'], unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('attempts', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_update', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('transferred_bytes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rate', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('offsite', ['RemoteUploadRequest'])

        # Adding model 'LocalUploadRequest'
        db.create_table('offsite_localuploadrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.Volume'], unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('attempts', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_update', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('transferred_bytes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rate', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('offsite', ['LocalUploadRequest'])

        # Adding model 'DownloadRequest'
        db.create_table('offsite_downloadrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.Volume'], unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('attempts', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_update', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('transferred_bytes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rate', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('offsite', ['DownloadRequest'])

        # Adding model 'DeleteRequest'
        db.create_table('offsite_deleterequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.Volume'], unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('attempts', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_update', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('transferred_bytes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rate', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('offsite', ['DeleteRequest'])

        # Adding model 'UploadTransferredData'
        db.create_table('offsite_uploadtransferreddata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bytes', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('offsite', ['UploadTransferredData'])

        # Adding model 'DownloadTransferredData'
        db.create_table('offsite_downloadtransferreddata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bytes', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('offsite', ['DownloadTransferredData'])


    def backwards(self, orm):
        
        # Deleting model 'Offsite'
        db.delete_table('offsite_offsite')

        # Deleting model 'Volume'
        db.delete_table('offsite_volume')

        # Deleting model 'UploadedVolume'
        db.delete_table('offsite_uploadedvolume')

        # Deleting model 'DownloadedVolume'
        db.delete_table('offsite_downloadedvolume')

        # Deleting model 'RemoteUploadRequest'
        db.delete_table('offsite_remoteuploadrequest')

        # Deleting model 'LocalUploadRequest'
        db.delete_table('offsite_localuploadrequest')

        # Deleting model 'DownloadRequest'
        db.delete_table('offsite_downloadrequest')

        # Deleting model 'DeleteRequest'
        db.delete_table('offsite_deleterequest')

        # Deleting model 'UploadTransferredData'
        db.delete_table('offsite_uploadtransferreddata')

        # Deleting model 'DownloadTransferredData'
        db.delete_table('offsite_downloadtransferreddata')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'offsite.deleterequest': {
            'Meta': {'object_name': 'DeleteRequest'},
            'attempts': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transferred_bytes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.Volume']", 'unique': 'True'})
        },
        'offsite.downloadedvolume': {
            'Meta': {'object_name': 'DownloadedVolume'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.Volume']"})
        },
        'offsite.downloadrequest': {
            'Meta': {'object_name': 'DownloadRequest'},
            'attempts': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transferred_bytes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.Volume']", 'unique': 'True'})
        },
        'offsite.downloadtransferreddata': {
            'Meta': {'object_name': 'DownloadTransferredData'},
            'bytes': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'offsite.localuploadrequest': {
            'Meta': {'object_name': 'LocalUploadRequest'},
            'attempts': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transferred_bytes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.Volume']", 'unique': 'True'})
        },
        'offsite.offsite': {
            'Meta': {'object_name': 'Offsite'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gateway_url': ('django.db.models.fields.CharField', [], {'default': "'http://www.veezor.com:8080'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'upload_rate': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'offsite.remoteuploadrequest': {
            'Meta': {'object_name': 'RemoteUploadRequest'},
            'attempts': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transferred_bytes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.Volume']", 'unique': 'True'})
        },
        'offsite.uploadedvolume': {
            'Meta': {'object_name': 'UploadedVolume'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.Volume']"})
        },
        'offsite.uploadtransferreddata': {
            'Meta': {'object_name': 'UploadTransferredData'},
            'bytes': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'offsite.volume': {
            'Meta': {'object_name': 'Volume'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('nimbus.shared.fields.ModelPathField', [], {'max_length': '2048'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['offsite']
