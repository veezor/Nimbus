# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FileSet'
        db.create_table('filesets_fileset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('filesets', ['FileSet'])

        # Adding model 'FilePath'
        db.create_table('filesets_filepath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('nimbus.shared.fields.ModelPathField')(max_length=2048)),
        ))
        db.send_create_signal('filesets', ['FilePath'])

        # Adding M2M table for field filesets on 'FilePath'
        db.create_table('filesets_filepath_filesets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filepath', models.ForeignKey(orm['filesets.filepath'], null=False)),
            ('fileset', models.ForeignKey(orm['filesets.fileset'], null=False))
        ))
        db.create_unique('filesets_filepath_filesets', ['filepath_id', 'fileset_id'])


    def backwards(self, orm):
        
        # Deleting model 'FileSet'
        db.delete_table('filesets_fileset')

        # Deleting model 'FilePath'
        db.delete_table('filesets_filepath')

        # Removing M2M table for field filesets on 'FilePath'
        db.delete_table('filesets_filepath_filesets')


    models = {
        'base.uuid': {
            'Meta': {'object_name': 'UUID'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_hex': ('django.db.models.fields.CharField', [], {'default': "'none'", 'unique': 'True', 'max_length': '255'})
        },
        'filesets.filepath': {
            'Meta': {'object_name': 'FilePath'},
            'filesets': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['filesets.FileSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('nimbus.shared.fields.ModelPathField', [], {'max_length': '2048'})
        },
        'filesets.fileset': {
            'Meta': {'object_name': 'FileSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.UUID']"})
        }
    }

    complete_apps = ['filesets']
