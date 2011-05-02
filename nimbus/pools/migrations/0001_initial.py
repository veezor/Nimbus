# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Pool'
        db.create_table('pools_pool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.FloatField')(default=5242880)),
            ('retention_time', self.gf('django.db.models.fields.IntegerField')(default=30)),
        ))
        db.send_create_signal('pools', ['Pool'])


    def backwards(self, orm):
        
        # Deleting model 'Pool'
        db.delete_table('pools_pool')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'retention_time': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'size': ('django.db.models.fields.FloatField', [], {'default': '5242880'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['pools']
