# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Schedule'
        db.create_table('schedules_schedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('schedules', ['Schedule'])

        # Adding model 'Daily'
        db.create_table('schedules_daily', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.Schedule'])),
            ('level', self.gf('django.db.models.fields.CharField')(max_length='25')),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('schedules', ['Daily'])

        # Adding model 'Hourly'
        db.create_table('schedules_hourly', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.Schedule'])),
            ('level', self.gf('django.db.models.fields.CharField')(max_length='25')),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('schedules', ['Hourly'])

        # Adding model 'Monthly'
        db.create_table('schedules_monthly', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.Schedule'])),
            ('level', self.gf('django.db.models.fields.CharField')(max_length='25')),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('schedules', ['Monthly'])

        # Adding model 'Weekly'
        db.create_table('schedules_weekly', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.Schedule'])),
            ('level', self.gf('django.db.models.fields.CharField')(max_length='25')),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('schedules', ['Weekly'])


    def backwards(self, orm):
        
        # Deleting model 'Schedule'
        db.delete_table('schedules_schedule')

        # Deleting model 'Daily'
        db.delete_table('schedules_daily')

        # Deleting model 'Hourly'
        db.delete_table('schedules_hourly')

        # Deleting model 'Monthly'
        db.delete_table('schedules_monthly')

        # Deleting model 'Weekly'
        db.delete_table('schedules_weekly')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'schedules.daily': {
            'Meta': {'object_name': 'Daily'},
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': "'25'"}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.Schedule']"})
        },
        'schedules.hourly': {
            'Meta': {'object_name': 'Hourly'},
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': "'25'"}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.Schedule']"})
        },
        'schedules.monthly': {
            'Meta': {'object_name': 'Monthly'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': "'25'"}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.Schedule']"})
        },
        'schedules.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'schedules.weekly': {
            'Meta': {'object_name': 'Weekly'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': "'25'"}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.Schedule']"})
        }
    }

    complete_apps = ['schedules']
