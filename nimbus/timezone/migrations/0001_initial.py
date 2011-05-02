# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Timezone'
        db.create_table('timezone_timezone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('ntp_server', self.gf('django.db.models.fields.CharField')(default='a.ntp.br', max_length=255)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('timezone', ['Timezone'])


    def backwards(self, orm):
        
        # Deleting model 'Timezone'
        db.delete_table('timezone_timezone')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'timezone.timezone': {
            'Meta': {'object_name': 'Timezone'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ntp_server': ('django.db.models.fields.CharField', [], {'default': "'a.ntp.br'", 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['timezone']
