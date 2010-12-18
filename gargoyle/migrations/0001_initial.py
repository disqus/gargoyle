# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Switch'
        db.create_table('gargoyle_switch', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('value', self.gf('jsonfield.fields.JSONField')(default='{}')),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
        ))
        db.send_create_signal('gargoyle', ['Switch'])


    def backwards(self, orm):
        
        # Deleting model 'Switch'
        db.delete_table('gargoyle_switch')


    models = {
        'gargoyle.switch': {
            'Meta': {'object_name': 'Switch'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'value': ('jsonfield.fields.JSONField', [], {'default': "'{}'"})
        }
    }

    complete_apps = ['gargoyle']
