# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Switch.label'
        db.alter_column('gargoyle_switch', 'label', self.gf('django.db.models.fields.CharField')(max_length=64, null=True))

        # Changing field 'Switch.key'
        db.alter_column('gargoyle_switch', 'key', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True))

    def backwards(self, orm):

        # Changing field 'Switch.label'
        db.alter_column('gargoyle_switch', 'label', self.gf('django.db.models.fields.CharField')(max_length=32, null=True))

        # Changing field 'Switch.key'
        db.alter_column('gargoyle_switch', 'key', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True))

    models = {
        'gargoyle.switch': {
            'Meta': {'object_name': 'Switch'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'value': ('jsonfield.fields.JSONField', [], {'default': "'{}'"})
        }
    }

    complete_apps = ['gargoyle']