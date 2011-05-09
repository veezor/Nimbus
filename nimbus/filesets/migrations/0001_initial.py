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
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['computers.Computer'])),
            ('path', self.gf('nimbus.shared.fields.ModelPathField')(max_length=2048)),
            ('filesets', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filesets.FileSet'])),
        ))
        db.send_create_signal('filesets', ['FilePath'])


    def backwards(self, orm):
        
        # Deleting model 'FileSet'
        db.delete_table('filesets_fileset')

        # Deleting model 'FilePath'
        db.delete_table('filesets_filepath')


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
            'password': ('django.db.models.fields.CharField', [], {'default': "'rEJF9x7KKnC4Zdh6mlgM'", 'max_length': '255'}),
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
        'filesets.filepath': {
            'Meta': {'object_name': 'FilePath'},
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['computers.Computer']"}),
            'filesets': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filesets.FileSet']"}),
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
