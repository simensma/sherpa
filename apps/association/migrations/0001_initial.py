# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("core", "0007_rename_user_tables"),
    )

    def forwards(self, orm):
        
        # Adding model 'Association'
        db.create_table('association_association', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['association.Association'], null=True)),
            ('focus_id', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('group_type', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('post_address', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('visit_address', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('zipcode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Zipcode'], null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('email', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('organization_no', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('gmap_url', self.gf('django.db.models.fields.CharField')(default='', max_length=2048)),
            ('facebook_url', self.gf('django.db.models.fields.CharField')(default='', max_length=2048)),
        ))
        db.send_create_signal('association', ['Association'])

        # Adding M2M table for field counties on 'Association'
        db.create_table('association_association_counties', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('association', models.ForeignKey(orm['association.association'], null=False)),
            ('county', models.ForeignKey(orm['core.county'], null=False))
        ))
        db.create_unique('association_association_counties', ['association_id', 'county_id'])


    def backwards(self, orm):
        
        # Deleting model 'Association'
        db.delete_table('association_association')

        # Removing M2M table for field counties on 'Association'
        db.delete_table('association_association_counties')


    models = {
        'association.association': {
            'Meta': {'object_name': 'Association'},
            'counties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'associations'", 'symmetrical': 'False', 'to': "orm['core.County']"}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'facebook_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'focus_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'gmap_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization_no': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['association.Association']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Zipcode']", 'null': 'True'})
        },
        'core.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sherpa_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'core.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        }
    }

    complete_apps = ['association']
