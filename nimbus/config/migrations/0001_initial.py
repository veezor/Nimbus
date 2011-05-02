# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Config'
        db.create_table('config_config', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('director_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('director_password', self.gf('django.db.models.fields.CharField')(default='RWz6i9h8GJtLoPRSd2Z2', max_length=255)),
            ('director_address', self.gf('django.db.models.fields.IPAddressField')(default=u'192.168.15.102', max_length=15)),
        ))
        db.send_create_signal('config', ['Config'])


    def backwards(self, orm):
        
        # Deleting model 'Config'
        db.delete_table('config_config')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'config.config': {
            'Meta': {'object_name': 'Config'},
            'director_address': ('django.db.models.fields.IPAddressField', [], {'default': "u'192.168.15.102'", 'max_length': '15'}),
            'director_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'director_password': ('django.db.models.fields.CharField', [], {'default': "'vJkenT7MxuUjuhxrrtq6'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['config']
