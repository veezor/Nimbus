# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Profile'
        db.create_table('procedures_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, blank=True)),
            ('storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['storages.Storage'])),
            ('fileset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filesets.FileSet'])),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.Schedule'])),
        ))
        db.send_create_signal('procedures', ['Profile'])

        # Adding model 'Procedure'
        db.create_table('procedures_procedure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['computers.Computer'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['procedures.Profile'])),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pools.Pool'])),
            ('offsite_on', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('procedures', ['Procedure'])


    def backwards(self, orm):
        
        # Deleting model 'Profile'
        db.delete_table('procedures_profile')

        # Deleting model 'Procedure'
        db.delete_table('procedures_procedure')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'computers.computer': {
            'Meta': {'object_name': 'Computer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'crypto_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['computers.CryptoInfo']", 'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'computers'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['computers.ComputerGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'operation_system': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "'GTsC80cb0O1JPGwaZhl1'", 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'computers.computergroup': {
            'Meta': {'object_name': 'ComputerGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'computers.cryptoinfo': {
            'Meta': {'object_name': 'CryptoInfo'},
            'certificate': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'pem': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        },
        'filesets.fileset': {
            'Meta': {'object_name': 'FileSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'retention_time': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'size': ('django.db.models.fields.FloatField', [], {'default': '5242880'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'procedures.procedure': {
            'Meta': {'object_name': 'Procedure'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['computers.Computer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offsite_on': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pools.Pool']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['procedures.Profile']"}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'procedures.profile': {
            'Meta': {'object_name': 'Profile'},
            'fileset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filesets.FileSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.Schedule']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['storages.Storage']"})
        },
        'schedules.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'storages.storage': {
            'Meta': {'object_name': 'Storage'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address': ('django.db.models.fields.IPAddressField', [], {'default': "u'192.168.15.102'", 'max_length': '15'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "'GBG64I8TpdhuVlvFbN6M'", 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['procedures']
