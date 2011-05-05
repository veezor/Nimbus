# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BackupLevel'
        db.create_table('schedules_backuplevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('schedules', ['BackupLevel'])

        # Adding model 'Schedule'
        db.create_table('schedules_schedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('schedules', ['Schedule'])

        # Adding model 'Month'
        db.create_table('schedules_month', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('schedule', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['schedules.Schedule'], unique=True)),
            ('days', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=255)),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.BackupLevel'])),
        ))
        db.send_create_signal('schedules', ['Month'])

        # Adding model 'Week'
        db.create_table('schedules_week', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('schedule', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['schedules.Schedule'], unique=True)),
            ('days', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=255)),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.BackupLevel'])),
        ))
        db.send_create_signal('schedules', ['Week'])

        # Adding model 'Day'
        db.create_table('schedules_day', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('schedule', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['schedules.Schedule'], unique=True)),
            ('hour', self.gf('django.db.models.fields.TimeField')()),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.BackupLevel'])),
        ))
        db.send_create_signal('schedules', ['Day'])

        # Adding model 'Hour'
        db.create_table('schedules_hour', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('schedule', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['schedules.Schedule'], unique=True)),
            ('minute', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedules.BackupLevel'])),
        ))
        db.send_create_signal('schedules', ['Hour'])


    def backwards(self, orm):
        
        # Deleting model 'BackupLevel'
        db.delete_table('schedules_backuplevel')

        # Deleting model 'Schedule'
        db.delete_table('schedules_schedule')

        # Deleting model 'Month'
        db.delete_table('schedules_month')

        # Deleting model 'Week'
        db.delete_table('schedules_week')

        # Deleting model 'Day'
        db.delete_table('schedules_day')

        # Deleting model 'Hour'
        db.delete_table('schedules_hour')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'schedules.backuplevel': {
            'Meta': {'object_name': 'BackupLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'schedules.day': {
            'Meta': {'object_name': 'Day'},
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.BackupLevel']"}),
            'schedule': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['schedules.Schedule']", 'unique': 'True'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'schedules.hour': {
            'Meta': {'object_name': 'Hour'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.BackupLevel']"}),
            'minute': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'schedule': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['schedules.Schedule']", 'unique': 'True'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'schedules.month': {
            'Meta': {'object_name': 'Month'},
            'days': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255'}),
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.BackupLevel']"}),
            'schedule': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['schedules.Schedule']", 'unique': 'True'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'schedules.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        },
        'schedules.week': {
            'Meta': {'object_name': 'Week'},
            'days': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255'}),
            'hour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedules.BackupLevel']"}),
            'schedule': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['schedules.Schedule']", 'unique': 'True'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['schedules']
