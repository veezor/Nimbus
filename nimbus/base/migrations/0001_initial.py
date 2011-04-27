# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UUID'
        db.create_table('base_uuid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid_hex', self.gf('django.db.models.fields.CharField')(default='none', unique=True, max_length=255)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('base', ['UUID'])


    def backwards(self, orm):
        
        # Deleting model 'UUID'
        db.delete_table('base_uuid')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['base']
