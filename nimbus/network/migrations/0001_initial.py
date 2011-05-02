# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NetworkInterface'
        db.create_table('network_networkinterface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('netmask', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('gateway', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('dns1', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('dns2', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal('network', ['NetworkInterface'])


    def backwards(self, orm):
        
        # Deleting model 'NetworkInterface'
        db.delete_table('network_networkinterface')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'network.networkinterface': {
            'Meta': {'object_name': 'NetworkInterface'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'dns1': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'dns2': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'gateway': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'netmask': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['network']
