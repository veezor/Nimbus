# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ComputerGroup'
        db.create_table('computers_computergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('computers', ['ComputerGroup'])

        # Adding model 'CryptoInfo'
        db.create_table('computers_cryptoinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('certificate', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('pem', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal('computers', ['CryptoInfo'])

        # Adding model 'Computer'
        db.create_table('computers_computer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.UUID'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('address', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15)),
            ('operation_system', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1024, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(default='ET5LBv7z1oZDR9pQwSv9', max_length=255)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('crypto_info', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['computers.CryptoInfo'], unique=True)),
        ))
        db.send_create_signal('computers', ['Computer'])

        # Adding M2M table for field groups on 'Computer'
        db.create_table('computers_computer_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('computer', models.ForeignKey(orm['computers.computer'], null=False)),
            ('computergroup', models.ForeignKey(orm['computers.computergroup'], null=False))
        ))
        db.create_unique('computers_computer_groups', ['computer_id', 'computergroup_id'])


    def backwards(self, orm):
        
        # Deleting model 'ComputerGroup'
        db.delete_table('computers_computergroup')

        # Deleting model 'CryptoInfo'
        db.delete_table('computers_cryptoinfo')

        # Deleting model 'Computer'
        db.delete_table('computers_computer')

        # Removing M2M table for field groups on 'Computer'
        db.delete_table('computers_computer_groups')


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
            'password': ('django.db.models.fields.CharField', [], {'default': "'8jltvj3xjmZQX3p9ORAW'", 'max_length': '255'}),
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
        }
    }

    complete_apps = ['computers']
