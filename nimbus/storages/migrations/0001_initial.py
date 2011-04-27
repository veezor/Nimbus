# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Storage'
        db.create_table('storages_storage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address', self.gf('django.db.models.fields.IPAddressField')(default=u'192.168.15.102', max_length=15)),
            ('password', self.gf('django.db.models.fields.CharField')(default='iGxzM4Y76eCDymyWl7u0', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('storages', ['Storage'])

        # Adding model 'Device'
        db.create_table('storages_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('archive', self.gf('nimbus.shared.fields.ModelPathField')(max_length=2048)),
            ('storage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='devices', to=orm['storages.Storage'])),
        ))
        db.send_create_signal('storages', ['Device'])


    def backwards(self, orm):
        
        # Deleting model 'Storage'
        db.delete_table('storages_storage')

        # Deleting model 'Device'
        db.delete_table('storages_device')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'storages.device': {
            'Meta': {'object_name': 'Device'},
            'archive': ('nimbus.shared.fields.ModelPathField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'devices'", 'to': "orm['storages.Storage']"}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'storages.storage': {
            'Meta': {'object_name': 'Storage'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address': ('django.db.models.fields.IPAddressField', [], {'default': "u'192.168.15.102'", 'max_length': '15'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "'Aq0o6MRARgdhbRj7srNK'", 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['storages']
