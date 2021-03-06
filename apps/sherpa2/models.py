# encoding: utf-8
from datetime import datetime, date, timedelta
from cStringIO import StringIO
import json
import re

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.conf import settings
from django.core.cache import cache

import requests
import PIL.Image

from admin.models import Image, Album
from admin.images.util import upload_image
from core.models import County, Tag
from sherpa2.util import SHERPA2_COUNTIES_SET1
from sherpa2.exceptions import ConversionImpossible, OwnerDoesNotExist, NoOwners, DateWithoutStartDate, \
    DateWithInvalidStartDate, DateWithoutEndDate, DateWithInvalidEndDate

class Forening(models.Model):
    id = models.IntegerField(db_column='gr_id', primary_key=True)
    focus_id = models.IntegerField(db_column='gr_my_id', null=True, blank=True)
    parent = models.IntegerField(db_column='gr_parent', null=True, blank=True)
    fo_id = models.IntegerField(db_column='gr_fo_id', null=True, blank=True)
    name = models.CharField(db_column='gr_name', max_length=100, blank=True)
    content = models.TextField(db_column='gr_content', blank=True)
    phone = models.CharField(db_column='gr_phone', max_length=30, blank=True)
    fax = models.CharField(db_column='gr_fax', max_length=30, blank=True)
    email = models.CharField(db_column='gr_email', max_length=100, blank=True)
    member_email = models.CharField(db_column='gr_member_email', max_length=100, blank=True)
    url = models.CharField(db_column='gr_url', max_length=255, blank=True)
    legal_url = models.CharField(db_column='gr_legal_url', max_length=255, blank=True)
    post_address = models.CharField(db_column='gr_adress1', max_length=255, blank=True)
    visit_address = models.CharField(db_column='gr_adress2', max_length=255, blank=True)
    zipcode = models.CharField(db_column='gr_zip', max_length=12, blank=True)
    ziparea = models.CharField(db_column='gr_ziparea', max_length=50, blank=True)
    country = models.CharField(db_column='gr_country', max_length=50, blank=True)
    organization_no = models.CharField(db_column='gr_orgnr', max_length=20, blank=True)
    account = models.CharField(db_column='gr_account', max_length=50, blank=True)
    employees = models.DecimalField(db_column='gr_employees', null=True, max_digits=5, decimal_places=2, blank=True)
    visible = models.IntegerField(db_column='gr_visible', null=True, blank=True)
    path = models.CharField(db_column='gr_path', max_length=100, blank=True)
    date = models.CharField(db_column='gr_date', max_length=12, blank=True)
    type = models.CharField(db_column='gr_type', max_length=50, blank=True)
    status = models.CharField(db_column='gr_status', max_length=20, blank=True)
    online = models.IntegerField(db_column='gr_online', null=True, blank=True)
    lang = models.CharField(db_column='gr_lang', max_length=3, blank=True)
    county = models.TextField(db_column='gr_county', blank=True)
    facebook = models.TextField(db_column='gr_facebook', blank=True)
    risk_url = models.TextField(db_column='gr_risk_url', blank=True)
    map = models.TextField(db_column='gr_map', blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_focus_id(self):
        focus_id = s2a.focus_id
        if focus_id == 0:
            focus_id = None
        return focus_id

    def get_name(self):
        return self.name.strip()

    def get_post_address(self):
        return self.post_address.strip()

    def get_visit_address(self):
        return self.visit_address.strip()

    def get_phone(self):
        return self.phone.strip()

    def get_email(self):
        return self.email.strip()

    def get_organization_no(self):
        return self.organization_no.strip()

    def get_url(self):
        if self.url is None:
            return ''
        else:
            return self.url.strip()

    def get_gmap_url(self):
        if self.map is None:
            return ''
        else:
            return self.map.strip()

    def get_facebook_url(self):
        if self.facebook is None:
            return ''
        else:
            return self.facebook.strip()

    class Meta:
        db_table = u'groups'

class Cabin(models.Model):
    id = models.IntegerField(db_column=u'ca_id', primary_key=True)
    nr = models.IntegerField(db_column=u'ca_nr', null=True, blank=True)
    name = models.TextField(db_column=u'ca_name', )
    name_official = models.TextField(db_column=u'ca_name_official', blank=True)
    alias = models.TextField(db_column=u'ca_alias', blank=True)

    # service er "tjenestegrad", betjent/ubetjent/etc
    # B - Betjent
    # S - Selvbetjent
    # U - Ubetjent
    # C - Servering
    # D - Dagshytte
    # N - Nødsbu
    # X - Stengt
    service = models.TextField(db_column=u'ca_service', blank=True)

    # type er om det er DNT-hytte eller privateid hytte
    # D - DNT-hytte
    # P - Privat
    # R - Privat rabatthytte
    type = models.TextField(db_column=u'ca_type', blank=True)

    built = models.TextField(db_column=u'ca_built', blank=True)
    content = models.TextField(db_column=u'ca_content', blank=True)
    content_extended = models.TextField(db_column=u'ca_content_extended', blank=True)
    owner = models.IntegerField(db_column=u'ca_owner', )
    maintainer = models.IntegerField(db_column=u'ca_maintainer', )
    beds_b = models.IntegerField(db_column=u'ca_beds_b', null=True, blank=True)
    beds_s = models.IntegerField(db_column=u'ca_beds_s', null=True, blank=True)
    beds_u = models.IntegerField(db_column=u'ca_beds_u', null=True, blank=True)
    beds_winter = models.IntegerField(db_column=u'ca_beds_winter', null=True, blank=True)
    beds_extras = models.IntegerField(db_column=u'ca_beds_extras', null=True, blank=True)
    location = models.TextField(db_column=u'ca_location', blank=True)
    altitude = models.IntegerField(db_column=u'ca_altitude', null=True, blank=True)
    utm = models.TextField(db_column=u'ca_utm', blank=True)
    utm_gps = models.TextField(db_column=u'ca_utm_gps', blank=True)
    m711 = models.TextField(db_column=u'ca_m711', blank=True)
    m711_nb = models.TextField(db_column=u'ca_m711_nb', blank=True)
    map = models.TextField(db_column=u'ca_map', blank=True)
    map_nb = models.TextField(db_column=u'ca_map_nb', blank=True)
    lon = models.DecimalField(db_column=u'ca_lon', null=True, max_digits=65535, decimal_places=65535, blank=True)
    lat = models.DecimalField(db_column=u'ca_lat', null=True, max_digits=65535, decimal_places=65535, blank=True)
    ssr_id = models.IntegerField(db_column=u'ca_ssr_id', null=True, blank=True)
    ssr_obj_id = models.IntegerField(db_column=u'ca_ssr_obj_id', null=True, blank=True)
    ssr_type_id = models.IntegerField(db_column=u'ca_ssr_type_id', null=True, blank=True)
    ssr_type = models.TextField(db_column=u'ca_ssr_type', blank=True)
    municipality_id = models.IntegerField(db_column=u'ca_municipality_id', null=True, blank=True)
    municipality = models.TextField(db_column=u'ca_municipality', blank=True)
    county = models.TextField(db_column=u'ca_county', blank=True)
    yr_url = models.TextField(db_column=u'ca_yr_url', blank=True)
    contact_in_season = models.TextField(db_column=u'ca_contact_in_season', blank=True)
    address_in_season = models.TextField(db_column=u'ca_address_in_season', blank=True)
    mobile_in_season = models.TextField(db_column=u'ca_mobile_in_season', blank=True)
    phone_in_season = models.TextField(db_column=u'ca_phone_in_season', blank=True)
    fax_in_season = models.TextField(db_column=u'ca_fax_in_season', blank=True)
    email_in_season = models.TextField(db_column=u'ca_email_in_season', blank=True)
    contact_out_of_season = models.TextField(db_column=u'ca_contact_out_of_season', blank=True)
    address_out_of_season = models.TextField(db_column=u'ca_address_out_of_season', blank=True)
    mobile_out_of_season = models.TextField(db_column=u'ca_mobile_out_of_season', blank=True)
    phone_out_of_season = models.TextField(db_column=u'ca_phone_out_of_season', blank=True)
    fax_out_of_season = models.TextField(db_column=u'ca_fax_out_of_season', blank=True)
    email_out_of_season = models.TextField(db_column=u'ca_email_out_of_season', blank=True)
    url = models.TextField(db_column=u'ca_url', blank=True)
    content_nno = models.TextField(db_column=u'ca_content_nno', blank=True)
    content_eng = models.TextField(db_column=u'ca_content_eng', blank=True)
    content_ger = models.TextField(db_column=u'ca_content_ger', blank=True)
    access_summer = models.TextField(db_column=u'ca_access_summer', blank=True)
    access_winter = models.TextField(db_column=u'ca_access_winter', blank=True)
    access = models.TextField(db_column=u'ca_access', blank=True)
    price = models.TextField(db_column=u'ca_price', blank=True)
    album = models.TextField(db_column=u'ca_album', blank=True)
    startdate = models.TextField(db_column=u'ca_startdate', blank=True)
    extras = models.TextField(db_column=u'ca_extras', blank=True)
    source = models.TextField(db_column=u'ca_source', blank=True)
    status = models.TextField(db_column=u'ca_status', blank=True)
    modified = models.DateTimeField(db_column=u'ca_modified', null=True, blank=True)
    online = models.IntegerField(db_column=u'ca_online', null=True, blank=True)
    modified_by = models.IntegerField(db_column=u'ca_modified_by', null=True, blank=True)
    content_fre = models.TextField(db_column=u'ca_content_fre', blank=True)
    booking_url = models.TextField(db_column=u'ca_booking_url', blank=True)
    url_ut = models.TextField(db_column=u'ca_url_ut', blank=True)
    the_geom = models.GeometryField(blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'cabin2'

class Article(models.Model):
    id = models.IntegerField(db_column='ar_id', primary_key=True)
    owner = models.IntegerField(db_column='ar_owner', null=True, blank=True)
    name = models.CharField(db_column='ar_name', max_length=100, blank=True)
    lede = models.TextField(db_column='ar_ingress', blank=True)
    content = models.TextField(db_column='ar_content', blank=True)
    author = models.CharField(db_column='ar_author', max_length=100, blank=True)
    author_email = models.CharField(db_column='ar_author_email', max_length=100, blank=True)
    date = models.CharField(db_column='ar_date', max_length=12, blank=True)
    date_in = models.CharField(db_column='ar_date_in', max_length=12, blank=True)
    date_out = models.CharField(db_column='ar_date_out', max_length=12, blank=True)
    status = models.CharField(db_column='ar_status', max_length=20, blank=True)
    orig_id = models.IntegerField(db_column='ar_orig_id', null=True, blank=True)
    online = models.IntegerField(db_column='ar_online', null=True, blank=True)
    rel_cabins = models.TextField(db_column='ar_rel_cabins', blank=True)
    rel_locations = models.TextField(db_column='ar_rel_locations', blank=True)
    priority = models.IntegerField(db_column='ar_priority', null=True, blank=True)
    folders = models.ManyToManyField('sherpa2.Folder', related_name='articles', through='FolderArticle')

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'article'

class Folder(models.Model):
    id = models.IntegerField(db_column='fo_id', primary_key=True)
    parent = models.IntegerField(db_column='fo_parent', null=True, blank=True)
    owner = models.IntegerField(db_column='fo_owner', null=True, blank=True)
    name = models.CharField(db_column='fo_name', max_length=100, blank=True)
    content = models.TextField(db_column='fo_content', blank=True)
    sequence = models.IntegerField(db_column='fo_sequence', null=True, blank=True)
    url = models.CharField(db_column='fo_url', max_length=255, blank=True)
    clickable = models.IntegerField(db_column='fo_clickable', null=True, blank=True)
    in_menu = models.IntegerField(db_column='fo_in_menu', null=True, blank=True)
    status = models.CharField(db_column='fo_status', max_length=20, blank=True)
    path = models.CharField(db_column='fo_path', max_length=100, blank=True)
    online = models.IntegerField(db_column='fo_online', null=True, blank=True)
    show_rel_articles = models.IntegerField(db_column='fo_show_rel_articles')
    cols = models.IntegerField(db_column='fo_cols', null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'folder'

class FolderArticle(models.Model):
    folder = models.ForeignKey('sherpa2.Folder', db_column='fo_id')
    article = models.ForeignKey('sherpa2.Article', db_column='ar_id')
    status = models.CharField(db_column='fa_status', max_length=20, blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'folder_article'

class Condition(models.Model):
    id = models.IntegerField(db_column='co_id', primary_key=True)
    locations = models.CharField(db_column='co_lo_id', max_length=200, blank=True)
    content = models.TextField(db_column='co_content', blank=True)
    date_created = models.CharField(db_column='co_date_created', max_length=14)
    date_changed = models.CharField(db_column='co_date_changed', max_length=14)
    date_observed = models.CharField(db_column='co_date_observed', max_length=8)
    author_name = models.CharField(db_column='co_author_name', max_length=200, blank=True)
    author_email = models.CharField(db_column='co_author_email', max_length=200, blank=True)
    gr_id = models.IntegerField(db_column='co_gr_id', null=True, blank=True)
    online = models.IntegerField(db_column='co_online', null=True, blank=True)
    deleted = models.IntegerField(db_column='co_deleted')

    def __unicode__(self):
        return u'%s' % self.pk

    def get_date_observed(self):
        return datetime.strptime(self.date_observed, "%Y%m%d").date()

    def get_locations(self):
        locations = cache.get('conditions.locations.%s' % self.id)
        if locations is None:
            # Note that we're not filtering on active locations since sherpa2 doesn't, and some conditions may be
            # related to locations marked as not online
            locations = set([Location.objects.get(code=l) for l in self.locations.split('|') if l != ''])
            cache.set('conditions.locations.%s' % self.id, locations, 60 * 60 * 12)
        return locations

    def get_comma_separated_locations(self):
        return ', '.join([l.name for l in self.get_locations()])

    def get_location_ids_json(self):
        return json.dumps(["%s" % l.id for l in self.get_locations()])

    @staticmethod
    def get_all():
        return Condition.objects.filter(online=1, deleted=0)

    @staticmethod
    def get_ordered_recent():
        # We've defined 'recent' as up to 2 weeks old
        two_weeks_ago = date.today() - timedelta(days=14)
        # Note that the ordering works even though the date is stored as a CharField.
        return [c for c in Condition.get_all().order_by('-date_observed') if c.get_date_observed() >= two_weeks_ago]

    class Meta:
        db_table = u'conditions'

class Location(models.Model):
    id = models.IntegerField(db_column='lo_id', primary_key=True)
    name = models.TextField(db_column='lo_name')
    code = models.TextField(db_column='lo_code')
    alias = models.TextField(db_column='lo_alias')
    album = models.TextField(db_column='lo_album')
    maintainer = models.TextField(db_column='lo_maintainer')
    mapshop = models.TextField(db_column='lo_mapshop')
    online = models.IntegerField(db_column='lo_online', null=True)
    county = models.TextField(db_column='lo_county')
    municipality = models.TextField(db_column='lo_municipality')
    terrain = models.TextField(db_column='lo_terrain')
    maps = models.TextField(db_column='lo_maps')
    coordinates = models.TextField(db_column='lo_coordinates') # This field type is a guess.
    content_nor = models.TextField(db_column='lo_content_nor')
    content_nno = models.TextField(db_column='lo_content_nno')
    content_eng = models.TextField(db_column='lo_content_eng')
    content_ger = models.TextField(db_column='lo_content_ger')
    content_fre = models.TextField(db_column='lo_content_fre')
    modified = models.DateTimeField(db_column='lo_modified', null=True)
    modified_by = models.IntegerField(db_column='lo_modified_by', null=True)
    created = models.DateTimeField(db_column='lo_created', null=True)
    created_by = models.IntegerField(db_column='lo_created_by', null=True)
    order = models.IntegerField(db_column='lo_order', null=True)
    parent = models.TextField(db_column='lo_parent')
    yr_url = models.TextField(db_column='lo_yr_url')
    meta = models.IntegerField(db_column='lo_meta', null=True)
    geom = models.MultiPolygonField(db_column='the_geom', null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def get_active():
        return Location.objects.filter(online=1)

    @staticmethod
    def get_active_cached():
        locations = cache.get('sherpa2.locations')
        if locations is None:
            locations = Location.get_active()
            cache.set('sherpa2.locations', locations, 60 * 60 * 24 * 7)
        return locations

    class Meta:
        db_table = u'location2'
        ordering = ['name']

class Turforslag(models.Model):
    id = models.IntegerField(db_column='tp_id', primary_key=True)
    season = models.TextField(db_column='tp_season', blank=True)
    owner = models.CharField(db_column='tp_owner', max_length=20, blank=True)
    name = models.CharField(db_column='tp_name', max_length=100, blank=True)
    ingress = models.TextField(db_column='tp_ingress', blank=True)
    content = models.TextField(db_column='tp_content', blank=True)
    author = models.CharField(db_column='tp_author', max_length=100, blank=True)
    author_email = models.CharField(db_column='tp_author_email', max_length=100, blank=True)
    location = models.CharField(db_column='tp_location', max_length=100, blank=True)
    extras = models.CharField(db_column='tp_extras', max_length=255, blank=True)
    status = models.CharField(db_column='tp_status', max_length=20, blank=True)
    online = models.IntegerField(db_column='tp_online', null=True, blank=True)
    name_nno = models.CharField(db_column='tp_name_nno', max_length=100, blank=True)
    ingress_nno = models.TextField(db_column='tp_ingress_nno', blank=True)
    content_nno = models.TextField(db_column='tp_content_nno', blank=True)
    name_eng = models.CharField(db_column='tp_name_eng', max_length=100, blank=True)
    ingress_eng = models.TextField(db_column='tp_ingress_eng', blank=True)
    content_eng = models.TextField(db_column='tp_content_eng', blank=True)
    name_ger = models.CharField(db_column='tp_name_ger', max_length=100, blank=True)
    ingress_ger = models.TextField(db_column='tp_ingress_ger', blank=True)
    content_ger = models.TextField(db_column='tp_content_ger', blank=True)
    days = models.CharField(db_column='tp_days', max_length=8191, blank=True)
    type = models.CharField(db_column='tp_type', max_length=8191, blank=True)
    modified = models.DateTimeField(db_column='tp_modified', null=True, blank=True)
    modified_by = models.IntegerField(db_column='tp_modified_by', null=True, blank=True)
    created = models.DateTimeField(db_column='tp_created', null=True, blank=True)
    created_by = models.IntegerField(db_column='tp_created_by', null=True, blank=True)
    terrain = models.TextField(db_column='tp_terrain', blank=True)
    difficulty = models.TextField(db_column='tp_difficulty', blank=True)
    suits = models.TextField(db_column='tp_suits', blank=True)
    album = models.TextField(db_column='tp_album', blank=True)
    content2 = models.TextField(db_column='tp_content2', blank=True)
    content2_eng = models.TextField(db_column='tp_content2_eng', blank=True)
    content2_ger = models.TextField(db_column='tp_content2_ger', blank=True)
    content2_nno = models.TextField(db_column='tp_content2_nno', blank=True)
    access = models.TextField(db_column='tp_access', blank=True)
    access_eng = models.TextField(db_column='tp_access_eng', blank=True)
    access_ger = models.TextField(db_column='tp_access_ger', blank=True)
    access_nno = models.TextField(db_column='tp_access_nno', blank=True)
    county = models.IntegerField(db_column='tp_county', null=True, blank=True)
    municipality = models.IntegerField(db_column='tp_municipality', null=True, blank=True)
    map = models.TextField(db_column='tp_map', blank=True)
    name_fre = models.TextField(db_column='tp_name_fre', blank=True)
    content2_fre = models.TextField(db_column='tp_content2_fre', blank=True)
    access_fre = models.TextField(db_column='tp_access_fre', blank=True)
    lat = models.DecimalField(null=True, max_digits=65535, decimal_places=65535, blank=True)
    lon = models.DecimalField(null=True, max_digits=65535, decimal_places=65535, blank=True)
    the_geom = models.GeometryField(blank=True)
    time = models.TextField(db_column='tp_time', blank=True)
    km = models.TextField(db_column='tp_km', blank=True)
    season2 = models.TextField(db_column='tp_season2', blank=True)
    geojson = models.TextField(blank=True)
    group = models.CharField(db_column='tp_group', max_length=100, blank=True)
    mail_sent = models.IntegerField(null=True, blank=True)
    geojson_ok = models.IntegerField(null=True, blank=True)
    eta_modified_by = models.TextField(db_column='tp_eta_modified_by', blank=True)
    links = models.TextField(db_column='tp_links', blank=True)
    auth_uri = models.CharField(max_length=256, blank=True)
    hash = models.CharField(db_column='tp_hash', max_length=256, blank=True)
    type2 = models.CharField(db_column='tp_type2', max_length=8191, blank=True)
    difficulty = models.TextField(blank=True)
    ut_url = models.TextField(blank=True)

    def get_object_id(self):
        return NtbId.objects.get(sql_id=self.id, type='T').object_id

    class Meta:
        db_table = u'trip'

class NtbId(models.Model):
    # Note that although the sql_id is absolutely not the primary key, we need to mark it as such to have Django allow
    # us to reference 'id'. Note also that this will make certain operations dependent on the PK not work. This table
    # should only be used for simple lookups on both ids and type explicitly.
    sql_id = models.IntegerField(db_column='id', primary_key=True)
    object_id = models.CharField(db_column='oid', max_length=24, unique=True)
    type = models.CharField(max_length=1)

    class Meta:
        db_table = 'ntb_id'

class Activity(models.Model):
    id = models.IntegerField(db_column='ac_id', primary_key=True)
    code = models.TextField(db_column='ac_code', blank=True)
    owner = models.TextField(db_column='ac_owner', blank=True)
    name = models.TextField(db_column='ac_name', blank=True)
    ingress = models.TextField(db_column='ac_ingress', blank=True)
    content = models.TextField(db_column='ac_content', blank=True)
    info = models.TextField(db_column='ac_info', blank=True)
    author = models.TextField(db_column='ac_author', blank=True)
    author_email = models.TextField(db_column='ac_author_email', blank=True)
    date_from = models.TextField(db_column='ac_date_from', blank=True)
    date_to = models.TextField(db_column='ac_date_to', blank=True)
    deposit = models.DecimalField(db_column='ac_deposit', null=True, max_digits=6, decimal_places=2, blank=True)
    cancel_valid = models.DecimalField(db_column='ac_cancel_valid', null=True, max_digits=6, decimal_places=2, blank=True)
    cancel_invalid = models.DecimalField(db_column='ac_cancel_invalid', null=True, max_digits=6, decimal_places=2, blank=True)
    days = models.IntegerField(db_column='ac_days', null=True, blank=True)
    location = models.TextField(db_column='ac_location', blank=True)
    type = models.TextField(db_column='ac_type', blank=True)
    extras = models.TextField(db_column='ac_extras', blank=True)
    status = models.TextField(db_column='ac_status', blank=True)
    online = models.IntegerField(db_column='ac_online', null=True, blank=True)
    lang = models.TextField(db_column='ac_lang', blank=True)
    author_phone = models.TextField(db_column='ac_author_phone', blank=True)
    name_nno = models.TextField(db_column='ac_name_nno', blank=True)
    ingress_nno = models.TextField(db_column='ac_ingress_nno', blank=True)
    content_nno = models.TextField(db_column='ac_content_nno', blank=True)
    name_eng = models.TextField(db_column='ac_name_eng', blank=True)
    ingress_eng = models.TextField(db_column='ac_ingress_eng', blank=True)
    content_eng = models.TextField(db_column='ac_content_eng', blank=True)
    name_ger = models.TextField(db_column='ac_name_ger', blank=True)
    ingress_ger = models.TextField(db_column='ac_ingress_ger', blank=True)
    content_ger = models.TextField(db_column='ac_content_ger', blank=True)
    county = models.TextField(db_column='ac_county', blank=True)
    cat = models.TextField(db_column='ac_cat', blank=True)
    lat = models.DecimalField(db_column='ac_lat', null=True, max_digits=65535, decimal_places=65535, blank=True)
    lon = models.DecimalField(db_column='ac_lon', null=True, max_digits=65535, decimal_places=65535, blank=True)
    pub_date = models.TextField(db_column='ac_publish_date', blank=True)

    def get_owner_ids(self):
        if self.owner is None or self.owner.strip() == '':
            return []
        return [int(id) for id in self.owner.split('|') if id.strip() != '']

    def get_counties(self):
        if self.county is None:
            return []
        return [County.objects.get(code=SHERPA2_COUNTIES_SET1[int(id)]) for id in self.county.split('|') if id != '']

    def get_locations(self):
        locations = []
        for location_code in self.location.split('|'):
            if location_code == '':
                continue

            try:
                locations.append(Location.get_active().get(code=location_code))
            except Location.DoesNotExist:
                if Location.objects.filter(code=location_code).exists():
                    # The Location exists, it's just not active - ignore it
                    pass
                else:
                    # The Location code doesn't exist, we'll need to find out why and handle this
                    raise
        return locations

    def get_extras(self):
        return [extra.strip() for extra in self.extras.split('|') if extra.strip() != '']

    def get_categories(self):
        if self.cat is None:
            return []
        return [c.strip() for c in self.cat.split('|') if c.strip() != '']

    def get_pub_date(self):
        return datetime.strptime(self.pub_date, "%Y-%m-%d").date()

    def get_start_point(self):
        if self.lat is None or self.lon is None:
            return None

        return Point(float(self.lat), float(self.lon))

    def occurs_in_future(self):
        return any([d.get_date_from() >= date.today() for d in self.dates.all()])

    #
    # Conversion to sherpa 3
    #

    DIFFICULTY_CONVERSION_TABLE = {
        'Va_1': 'easy',
        'Va_2': 'easy',
        'Va_3': 'medium',
        'Va_4': 'hard',
        'Va_5': 'hard',
        'Va_6': 'expert',
    }

    AUDIENCE_CONVERSION_TABLE = {
        'Tl_adult': 'adults',
        'Tl_children': 'children',
        'Tl_youth': 'youth',
        'Tl_senior': 'senior',
        'Tl_mountaineers': 'mountaineers',
        'Tl_disabled': 'disabled',
    }

    def convert(self, aktivitet=None):
        """Converts this aktivitet from sherpa2 to a new aktivitet. If aktivitet is provided, that object will be used
        instead of a new one.

        raises ConversionImpossible if the old aktivitet data is in a state we can't convert from"""
        from aktiviteter.models import Aktivitet, AktivitetImage, ConversionFailure

        if aktivitet is None:
            aktivitet = Aktivitet()

        # Delete any existing conversion failure object
        ConversionFailure.objects.filter(sherpa2_id=self.id).delete()

        # Perform conversions - these may throw exceptions
        foreninger = self.convert_foreninger()
        description = self.convert_description()
        pub_date = self.convert_pub_date()
        omrader = self.convert_omrader()
        difficulty = self.convert_difficulty()
        audiences = self.convert_audiences()
        category, category_type, category_tags = self.convert_categories()
        converted_images = self.convert_images()

        # Conversions succeeded, save the data to the model object
        aktivitet.forening = foreninger['main:forening']
        aktivitet.forening_cabin = foreninger['main:cabin']
        aktivitet.sherpa2_id = self.id
        aktivitet.code = self.code.strip()
        aktivitet.title = self.name.strip()
        aktivitet.description = description
        aktivitet.category = category
        aktivitet.category_type = category_type
        aktivitet.pub_date = pub_date
        aktivitet.start_point = self.get_start_point()
        aktivitet.omrader = omrader
        aktivitet.difficulty = difficulty
        aktivitet.published = True
        aktivitet.private = False

        # Save before updating relational fields in case this was a new object without a PK
        aktivitet.save()

        aktivitet.co_foreninger = foreninger['rest:forening']
        aktivitet.co_foreninger_cabin = foreninger['rest:cabin']
        aktivitet.counties = self.get_counties()
        aktivitet.category_tags.clear()
        aktivitet.audiences = audiences
        for tag in category_tags:
            obj, created = Tag.objects.get_or_create(name=tag)
            aktivitet.category_tags.add(obj)

        # Remove all existing images by default
        images_to_delete = [image.id for image in aktivitet.images.all()]

        for order, old_image in enumerate(converted_images):
            # Check if this image has already been imported
            try:
                # Theoretically, there shouldn't be any duplicate images, but for some reason we found some
                # occurrences of this, so just handle it and delete any extra images.
                aktivitet_images = aktivitet.images.filter(sherpa2_url=old_image['url'])
                for extra_image in aktivitet_images[1:]:
                    extra_image.delete()
                aktivitet_image = aktivitet_images[0]

                # Yeah, it already exists - just update the order and text, and don't remove it
                images_to_delete.remove(aktivitet_image.id)
                aktivitet_image.order = order
                aktivitet_image.text = old_image['title']
                aktivitet_image.save()
            except ValueError:
                # Might occur if some sherpa2 activity has multiple occurrences of the same image, and the converted
                # aktivitet has only one - would attempt to remove the id twice, which we can ignore since we don't
                # want to add the image twice
                pass
            except IndexError:
                # Doesn't exist - download the image and create it in our image archive
                try:
                    downloaded_image = requests.get(old_image['url'])
                    content_type = downloaded_image.headers.get('Content-Type', '')
                    if not content_type.startswith('image/'):
                        # Might be an incorrect reference, or a HTML 404 page - skip it
                        continue

                    image_data = downloaded_image.content
                    try:
                        extension = old_image['url'].rsplit('.', 1)[1].lower()
                        if extension not in ['jpg', 'jpeg', 'gif', 'png', 'tif', 'tiff']:
                            continue
                    except KeyError:
                        continue

                    # Require a certain dimension size for the image
                    pil_image = PIL.Image.open(StringIO(image_data))
                    if pil_image.size[0] < 100 or pil_image.size[1] < 100:
                        continue

                    image = upload_image(
                        image_data=image_data,
                        extension=extension,
                        description=old_image['title'],
                        album=Album.objects.get(id=Album.IMPORTED_AKTIVITETER_ALBUM_ID),
                        photographer='',
                        credits='',
                        licence='',
                        content_type=content_type,
                        tags=[],
                        uploader=None,
                    )

                    aktivitet.images.add(AktivitetImage(
                        url=image.get_url(),
                        text=image.description,
                        photographer='',
                        order=order,
                        sherpa2_url=old_image['url'],
                    ))
                except requests.ConnectionError:
                    # We're unable to download the referenced image - skip it for now.
                    pass
                except requests.packages.urllib3.exceptions.LocationParseError:
                    # Any problems with the URI might throw this. One example of this:
                    # http://www2.turistforeningen.nofile://server/eva/mail/eudora/attach/017%20Lavendel.jpg
                    # Simply ignore images with this occurence
                    pass

        # All converted images are accounted for; delete all others
        aktivitet.images.filter(id__in=images_to_delete).delete()

        # Save all new relations
        aktivitet.save()

        # Now convert all date objects. We'll try to match start/end date with existing dates and update the object on
        # match - and create/delete any date that doesn't.

        # Put all date objects here and remove them as they're matched
        remaining_date_objects = list(aktivitet.dates.all())

        try:
            for sherpa2_date in self.dates.all():
                matched = False
                try:
                    start_date = sherpa2_date.convert_start_date().date()
                    end_date = sherpa2_date.convert_end_date().date()
                except ConversionImpossible:
                    if sherpa2_date.online != ActivityDate.ONLINE_DISABLED:
                        # Couldn't convert the date and this date is published; raise the exception
                        raise
                    else:
                        # The date isn't published, so ignore it
                        continue

                for sherpa3_date in aktivitet.dates.all():
                    if start_date == sherpa3_date.start_date.date() and end_date == sherpa3_date.end_date.date():
                        # The start/end date matched an existing date - convert into that date object
                        matched = True
                        remaining_date_objects.remove(sherpa3_date)
                        sherpa2_date.convert(aktivitet, sherpa3_date)
                        break

                # If it didn't match any date, create a new one
                if not matched:
                    sherpa2_date.convert(aktivitet)

                # If the date isn't published, unpublish the entire aktivitet
                if aktivitet.published and not sherpa2_date.convert_published():
                    aktivitet.published = False
                    aktivitet.save()

            # Now the remaining date objects weren't matched and any new ones should have been created, so delete the rest
            for date in remaining_date_objects:
                date.delete()

        except ConversionImpossible:
            # One of the dates can't be converted - we're not handling the exception here, but we've already created
            # the Aktivitet-object, so we should delete that
            aktivitet.delete()
            raise

        cache.delete('admin.aktivitet_count')

    def convert_foreninger(self):
        """sherpa2 models foreninger as a flat list, while sherpa3 separates the main forening and co_foreninger.
        We'll assume that the forening with the lowest 'type' (turgruppe/forening/sentral) is the main forening.
        If there are >1 of the same lowest type, we'll have to pick one at random."""
        from foreninger.models import Forening
        from aktiviteter.models import Cabin
        from sherpa2.models import Forening as Sherpa2Forening

        # A list of forening IDs which we're remapping at the time of import
        FORENING_MAPPINGS = {
            165: 724, # DNT ung Trondheim -> DNT ung Trøndelag
            228: 1193, # Dagsturkomitéen -> Voksengruppa (STF)
            223: 1193, # Søndagsturkomitéen -> Voksengruppa (STF)
            211: 1193, # Fjellturkomitéen -> Voksengruppa (STF)
        }

        foreninger = []
        cabins = []
        for id in self.get_owner_ids():
            try:
                if id in FORENING_MAPPINGS:
                    id = FORENING_MAPPINGS[id]
                foreninger.append(Forening.objects.get(id=id))
            except Forening.DoesNotExist:
                # Might be a forening of type 'cabin', check if it exists in our imported Cabin table
                try:
                    cabins.append(Cabin.objects.get(sherpa2_id=id))
                except Cabin.DoesNotExist:
                    if not Sherpa2Forening.objects.filter(id=id).exists():
                        # Ok, this is an age-old Forening; ignore the relation
                        pass
                    else:
                        # One of the owner relations is invalid; this is a problem, but continue in case other ones
                        # are valid, in which case we'll ignore this.
                        pass

        if len(foreninger) == 0 and len(cabins) == 0:
            self.save_conversion_failure(reason='no_owners', include_foreninger=False)
            raise NoOwners("No known owners exist for this activity; need at least 1")

        # Check if there's only cabins and use a random one as main
        if len(foreninger) == 0 and len(cabins) > 0:
            return {
                'main:forening': None,
                'rest:forening': [],
                'main:cabin': cabins[0],
                'rest:cabin': cabins[1:],
            }

        # Not only cabins; figure out the main forening and append cabins to the rest
        foreninger_sorted = Forening.sort(foreninger)
        for type in reversed([t[0] for t in Forening.TYPES]):
            if len(foreninger_sorted[type]) > 0:
                main_forening = foreninger_sorted[type][0]
                rest = [f for f in foreninger if f != main_forening]
                return {
                    'main:forening': main_forening,
                    'rest:forening': rest,
                    'main:cabin': None,
                    'rest:cabin': cabins,
                }

        # Note that we should never reach this code path
        raise Exception("Invalid code path; expected one of the previous clauses to return")

    def convert_description(self):
        def clean_tables(text):
            replacements = []
            for match in re.finditer(r'<table.*?</table>', text, re.DOTALL):
                table = match.group(0)

                # Remove any exising classes and set class only to "table"
                table = re.sub('class=".*?"', '', table)
                table = '%s class="table" %s' % (table[0:len('<table')], table[len('<table'):])

                # Remove any styles and borders
                table = re.sub('style=".*?"', '', table)
                table = re.sub('border=".*?"', '', table)
                table = re.sub('width=".*?"', '', table)
                table = re.sub('height=".*?"', '', table)
                table = re.sub('valign=".*?"', '', table)

                # Now reinsert the new table in the original text
                replacements.append({
                    'start': match.start(0),
                    'end': match.end(0),
                    'table': table
                })

            # Now replace each table with the cleaned one, but keep an offset to know how much we skewed the characters
            # since the indexes are all based on the original string
            offset = 0
            for replacement in replacements:
                original_length = len(text)
                text = "%s%s%s" % (
                    text[:(replacement['start'] + offset)],
                    replacement['table'],
                    text[(replacement['end'] + offset):]
                )
                new_length = len(text)
                offset += new_length - original_length

            return text

        # TODO: Handle HTML
        # Remove all image tags and merge lede/description
        if self.ingress is None:
            clean_lede = ""
        else:
            clean_lede = re.sub('<img.*?>', '', self.ingress)

        if self.content is None:
            clean_description = ""
        else:
            clean_description = re.sub('<img.*?>', '', self.content)

        clean_lede = clean_tables(clean_lede)
        clean_description = clean_tables(clean_description)
        return "%s %s" % (clean_lede, clean_description)

    def convert_images(self):
        # Precompile regular expressions
        img_tags_re = re.compile('<img.*?>')
        img_src_regex = re.compile('src=[\'"](.*?)[\'"]')
        img_title_regex = re.compile('title=[\'"](.*?)[\'"]')

        parsed_images = []
        for text in [self.ingress, self.content]:
            if text is None:
                continue

            for img in img_tags_re.findall(text):
                src_match = img_src_regex.search(img)
                if src_match is None:
                    # Image without a src attribute? Not expecting this to happen
                    continue

                path = src_match.group(1)

                # If thumbnail, use the original (note: assuming that any external images won't contain the ".thumb."
                # pattern)
                path = re.sub('\.thumb\.', '.', path)

                # Handle relative paths
                while path.startswith('../'):
                    path = path[2:]

                # If it still starts with a dot, not sure exactly how it's formatted; skip it
                if path.startswith('.'):
                    continue

                # Some incorrect image references contains base64 data, detect and skip them
                if 'data:image/' in path:
                    continue

                if path.startswith('http'):
                    # Absolute URL; assume correctness
                    url = path
                else:
                    # Assume sherpa2 URL, add old site domain
                    url = "http://%s%s" % (settings.OLD_SITE, path)

                # Strip query parameters
                if '?' in url:
                    url = url[:url.find('?')]
                if '#' in url:
                    url = url[:url.find('#')]

                title_match = img_title_regex.search(img)
                parsed_images.append({
                    'url': url,
                    'title': title_match.group(1) if title_match is not None else '',
                })
        return parsed_images

    def convert_difficulty(self):
        from aktiviteter.models import Aktivitet

        difficulties = [
            Activity.DIFFICULTY_CONVERSION_TABLE[extra]
            for extra in self.get_extras()
            if extra in Activity.DIFFICULTY_CONVERSION_TABLE
        ]

        if len(difficulties) == 0:
            # No difficulty specified - assume medium difficulty
            return 'medium'

        # Use the single highest valued difficulty
        difficulty_priority = {d[1][0]: d[0] for d in enumerate(Aktivitet.DIFFICULTY_CHOICES)}
        highest_difficulty = sorted(difficulties, key=lambda d: difficulty_priority[d])[-1]
        return highest_difficulty

    def convert_audiences(self):
        from aktiviteter.models import AktivitetAudience
        return [
            AktivitetAudience.objects.get(name=Activity.AUDIENCE_CONVERSION_TABLE[extra])
            for extra in self.get_extras() if extra in Activity.AUDIENCE_CONVERSION_TABLE
        ]

    def convert_omrader(self):
        try:
            locations = self.get_locations()
        except Location.DoesNotExist:
            if self.occurs_in_future():
                # Isn't known to occur, so we're not handling it explicitly for now - just re-raise the exception
                raise

            # For passed activities, we have a hardcoded list of locations we know aren't in use anymore and can
            # ignore. Reimplement the get_locations() method and ignore any of tose location codes
            IGNORED_LOCATION_CODES = ['NO_hjelm', 'NO_nordt', 'NO_norfj', 'NO_nordf', 'NO_rana']

            locations = []
            for location_code in self.location.split('|'):
                if location_code == '':
                    continue

                try:
                    locations.append(Location.get_active().get(code=location_code))
                except Location.DoesNotExist:
                    if Location.objects.filter(code=location_code).exists():
                        # The Location exists, it's just not active - ignore it
                        pass
                    else:
                        if location_code in IGNORED_LOCATION_CODES:
                            # Known ignored location code
                            pass
                        else:
                            # Unkown missing location code
                            raise

        # Now convert the locations to turbase object-ids
        return [
            NtbId.objects.get(sql_id=location.id, type='L').object_id
            for location in locations
        ]

    def convert_categories(self):
        """The wrapper for converting category, category type and category types"""
        main_category = self.convert_category()
        # Note that while category_type "semantically" should come before category_tags, we will convert category_tags
        # first here because they will rename some tags, and the category_type logic is more likely to find matches
        # after that conversion is done.
        category_tags = self.convert_category_tags()
        category_type = self.convert_category_type(main_category, category_tags)
        return (main_category, category_type, category_tags)

    def convert_category(self):
        """Figure out the main category"""
        categories = self.get_categories()

        # Try to infer the main category from the given categories

        if 'fellestur' in categories:
            return 'organizedhike'

        course_categories = [
            'brekurs',
            'instruktorkurs',
            'klatrekurs',
            'kurs',
            'skredkurs',
            'turlederkurs',
        ]
        if any([course in categories for course in course_categories]):
            return 'course'

        event_categories = [
            'basecamp',
            'byfjellstrimmen',
            'familiecamp',
            'jubileum',
            'komdegut',
            'medlemsmote',
            'multisport',
            'oppstart',
            'opptur',
            'samling',
            'seminar',
            'temamote',
        ]
        if any([event in categories for event in event_categories]):
            return 'event'

        if 'dugnad' in categories:
            return 'volunteerwork'

        # Couldn't infer the main category from the given categories - fall back to fellestur
        return 'organizedhike'

    def convert_category_tags(self):
        """Convert the flat category list; adapting similar but different categories to the new suggested
        category types"""
        categories = self.get_categories()

        #
        # æøå is now supported - translate these
        #

        norwegian_char_categories = [
            ('battur', u'båttur',),
            ('bertur', u'bærtur',),
            ('instruktorkurs', u'instruktørkurs',),
            ('lopetur', u'løpetur',),
            ('medlemsmote', u'medlemsmøte',),
            ('nertur', u'nærtur',),
            ('skoyter', u'skøyter',),
            ('snohuletur', u'snøhuletur',),
            ('temamote', u'temamøte',),
        ]

        for category in norwegian_char_categories:
            if category[0] in categories:
                categories.remove(category[0])
                categories.append(category[1])

        #
        # Merge kajakk/kano/elvepadling into padletur
        #

        if 'kajakk' in categories or 'kanotur' in categories or 'elvepadling' in categories:
            if 'kajakk' in categories:
                categories.remove('kajakk')
            if 'kanotur' in categories:
                categories.remove('kanotur')
            if 'elvepadling' in categories:
                categories.remove('elvepadling')
            categories.append('padletur')

        #
        # Other renamed categories
        #

        renamed_categories = [
            ('klatring', u'klatretur',),
            ('komdegut', u'kom-deg-ut-dagen',),
            ('sykkel', u'sykkeltur',),
        ]

        for category in renamed_categories:
            if category[0] in categories:
                categories.remove(category[0])
                categories.append(category[1])

        return categories

    def convert_category_type(self, category, category_tags):
        """Applies the category type based on the main category and converted category types"""
        from aktiviteter.models import Aktivitet

        category_type = '' # This empty value will be used if no matches are found
        for category in Aktivitet.CATEGORY_TYPES[category]:
            if category in category_tags:
                # Note that we'll overwrite the type if several defined categories matches the category type suggestions
                category_type = category

        return category_type

    def convert_pub_date(self):
        if self.pub_date is None or self.pub_date.strip() == '':
            return date.today()
        return self.get_pub_date()

    def save_conversion_failure(self, reason, include_foreninger=True):
        """Should be called if a conversion for this activity failed.
        include_foreninger can be set to False if foreninger were part of the reason for failure, in which
        case these relations won't be saved. Otherwise, we'll try to save a reference to the owners in order to
        filter on failures later."""
        from aktiviteter.models import ConversionFailure
        if include_foreninger:
            converted = self.convert_foreninger()
            foreninger = converted['rest:forening']
            if converted['main:forening'] is not None:
                foreninger.append(converted['main:forening'])
            cabins = converted['rest:cabin']
            if converted['main:cabin'] is not None:
                cabins.append(converted['main:cabin'])
        else:
            foreninger = []
            cabins = []

        # If any date objects are parseable, save the latest known date
        latest_date = None
        for date in self.dates.all():
            try:
                new_date = date.get_date_from()
                if latest_date is None or new_date > latest_date:
                    latest_date = new_date
            except:
                pass

        failure = ConversionFailure(
            sherpa2_id=self.id,
            name=self.name.strip(),
            reason=reason,
            latest_date=latest_date,
        )
        failure.save()
        failure.foreninger = foreninger
        failure.cabins = cabins

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)

    @staticmethod
    def synchronize():
        from aktiviteter.models import Aktivitet, SynchronizationDate

        # Use the sherpa2 changelog to figure out what we should synchronize.
        # Use sets for avoiding duplicates
        # TODO: This won't detect new/changed participants when participant conversion is implemented, since that
        # isn't logged in the changelog!
        last_synchronization = SynchronizationDate.objects.get().date
        new_and_changed_aktiviteter = set()
        deleted_aktiviteter = set()

        for log in Log.objects.filter(object='activity', timestamp__gte=last_synchronization):
            if log.action in ['insert', 'duplicate', 'update']:
                new_and_changed_aktiviteter.add(log.object_id)
            elif log.action == 'delete':
                deleted_aktiviteter.add(log.object_id)

        # Convert new and changed aktiviteter...
        for sherpa2_aktivitet in Activity.objects.filter(id__in=new_and_changed_aktiviteter).prefetch_related('dates').order_by('id'):
            try:
                sherpa3_aktivitet = Aktivitet.objects.prefetch_related('dates').get(sherpa2_id=sherpa2_aktivitet.id)
            except Aktivitet.DoesNotExist:
                sherpa3_aktivitet = None

            try:
                sherpa2_aktivitet.convert(sherpa3_aktivitet)
            except ConversionImpossible:
                # Ignore anything that can't be imported for now.
                pass

        # Now delete all the deleted ones
        Aktivitet.objects.filter(sherpa2_id__in=deleted_aktiviteter).delete()

    class Meta:
        db_table = u'activity'

class ActivityDate(models.Model):
    activity = models.ForeignKey(Activity, db_column='ac_id', related_name='dates')

    # Note that we're pretending that this column is the primary key, because Django *needs* a PK column and this
    # table doesn't have one. Note that this has ramifications for queryset.distinct().count() and instance
    # comparisons. Additionally, you should NOT call save() on this model (db_routers is configured to disallow it).
    date_from = models.CharField(db_column='ac_date_from', max_length=12, primary_key=True)
    date_to = models.CharField(db_column='ac_date_to', max_length=12)
    date_reg = models.CharField(db_column='ac_date_reg', max_length=12, blank=True)
    date_cancel = models.CharField(db_column='ac_date_cancel', max_length=12, blank=True)
    date_billing = models.CharField(db_column='ac_date_billing', max_length=12, blank=True)
    leader = models.CharField(db_column='ac_leader', max_length=255, blank=True)
    booking = models.IntegerField(db_column='ac_booking', null=True, blank=True)
    status = models.CharField(db_column='ac_status', max_length=20, blank=True)

    # The 'online' field decides what type of signup is enabled for this date, these are the known values:
    ONLINE_NO_SIGNUP = 3
    ONLINE_SIGNUP_REBUS = 2
    ONLINE_SIGNUP_MONTIS = 10
    ONLINE_SIGNUP_PAYMENT = 4
    ONLINE_SIGNUP_PAYMENT_ALT = 6 # Not sure why there are 2 separate values for online payment
    ONLINE_SIGNUP = 9
    ONLINE_DISABLED = 0
    ONLINE_DISABLED_SIGNUP_PAYMENT = -1
    online = models.IntegerField(db_column='ac_online', null=True, blank=True)

    signup_date_from = models.TextField(db_column='ac_signup_date_from', blank=True)
    signup_date_to = models.TextField(db_column='ac_signup_date_to', blank=True)

    def get_date_from(self):
        return datetime.strptime(self.date_from.strip(), "%Y-%m-%d").date()

    def get_date_to(self):
        return datetime.strptime(self.date_to.strip(), "%Y-%m-%d").date()

    def get_date_cancel(self):
        return datetime.strptime(self.date_cancel.strip(), "%Y-%m-%d").date()

    def get_signup_date_from(self):
        return datetime.strptime(self.signup_date_from.strip(), "%Y-%m-%d").date()

    def get_signup_date_to(self):
        return datetime.strptime(self.signup_date_to.strip(), "%Y-%m-%d").date()

    def is_fully_booked(self):
        """Returns True if this date is fully booked, and any subsequent bookings would be put on a waitinglist"""
        return self.participant_count() >= self.booking

    def participant_count(self):
        return ContractItem.objects.filter(
            prod_type='activity',
            prod_id=self.activity.id,
            prod_version=self.date_from.strip(),
            status=u'Påmeldt',
        ).count()

    #
    # Conversion
    #

    def convert(self, aktivitet, date=None):
        from aktiviteter.models import AktivitetDate

        if date is None:
            date = AktivitetDate()

        date.aktivitet = aktivitet
        try:
            date.start_date = self.convert_start_date()
            date.end_date = self.convert_end_date()
        except ConversionImpossible:
            if self.online == ActivityDate.ONLINE_DISABLED:
                # Couldn't convert the start/end date, but this date object isn't online anyway, so ignore it
                if date.id is not None:
                    date.delete()
                return
            else:
                raise

        if self.convert_signup_enabled():
            date.signup_enabled = True
            date.signup_montis = self.convert_signup_montis(date.aktivitet.code)
            date.max_participants = self.convert_max_participants()
            date.signup_start = self.convert_signup_start()
            date.signup_deadline = self.convert_signup_deadline()
            date.cancel_deadline = self.convert_cancel_deadline()
        else:
            date.signup_enabled = False
            date.signup_montis = False
            date.max_participants = None
            date.signup_start = None
            date.signup_deadline = None
            date.cancel_deadline = None

        date.signup_simple_allowed = False

        date.save()

    def convert_start_date(self):
        # Note that on conversion failure, we'll only record the failure if the date is published. If not, it's
        # expected to be skipped.
        try:
            if self.date_from is None or self.date_from.strip() == '':
                if self.online != ActivityDate.ONLINE_DISABLED:
                    self.activity.save_conversion_failure(reason='date_without_start_date')
                raise DateWithoutStartDate("Date entry has no start date")
            return datetime.combine(self.get_date_from(), datetime.min.time())
        except ValueError:
            if self.online != ActivityDate.ONLINE_DISABLED:
                self.activity.save_conversion_failure(reason='date_with_invalid_start_date')
            raise DateWithInvalidStartDate("Invalid date_from: '%s'" % self.date_from.strip())

    def convert_end_date(self):
        # Note that on conversion failure, we'll only record the failure if the date is published. If not, it's
        # expected to be skipped.
        try:
            if self.date_to is None or self.date_to.strip() == '':
                # End date isn't defined even though it has to be!
                if self.get_date_from() < date.today():
                    # This was an event in the past, so we'll let this slide and just set end date to the same as start
                    return datetime.combine(self.get_date_from(), datetime.min.time())
                else:
                    if self.online != ActivityDate.ONLINE_DISABLED:
                        self.activity.save_conversion_failure(reason='date_without_end_date')
                    raise DateWithoutEndDate("Future aktivitet with no end date")
            return datetime.combine(self.get_date_to(), datetime.min.time())
        except ValueError:
            if self.online != ActivityDate.ONLINE_DISABLED:
                self.activity.save_conversion_failure(reason='date_with_invalid_end_date')
            raise DateWithInvalidEndDate("Invalid date_to: '%s'" % self.date_to.strip())

    def convert_signup_enabled(self):
        return self.online in [
            ActivityDate.ONLINE_SIGNUP,
            ActivityDate.ONLINE_SIGNUP_PAYMENT,
            ActivityDate.ONLINE_SIGNUP_PAYMENT_ALT,
            ActivityDate.ONLINE_SIGNUP_REBUS,
            ActivityDate.ONLINE_SIGNUP_MONTIS,
        ]

    def convert_signup_montis(self, code):
        return code and self.online == ActivityDate.ONLINE_SIGNUP_MONTIS

    def convert_signup_start(self):
        try:
            if self.signup_date_from is None or self.signup_date_from.strip() == '':
                return None
            return self.get_signup_date_from()
        except ValueError:
            return None

    def convert_signup_deadline(self):
        try:
            if self.signup_date_to is None or self.signup_date_to.strip() == '':
                return None
            return self.get_signup_date_to()
        except ValueError:
            return None

    def convert_cancel_deadline(self):
        try:
            if self.date_cancel is None or self.date_cancel.strip() == '':
                return None
            return self.get_date_cancel()
        except ValueError:
            return None

    def convert_max_participants(self):
        if self.booking == 0:
            return None
        if self.booking < 0:
            # Yes, there are cases of a negative number of signups being stored - assume no limit
            return None
        return self.booking

    def convert_published(self):
        """Converts published for the *aktivitet* object, not the date."""
        return self.online not in [ActivityDate.ONLINE_DISABLED, ActivityDate.ONLINE_DISABLED_SIGNUP_PAYMENT]

    class Meta:
        db_table = u'activity_date'

class ContractItem(models.Model):
    id = models.IntegerField(db_column=u'ci_co_id', primary_key=True)
    item = models.IntegerField(db_column=u'ci_item', null=True, blank=True)
    type = models.IntegerField(db_column=u'ci_type', null=True, blank=True)
    pe_id = models.IntegerField(db_column=u'ci_pe_id', null=True, blank=True)
    gr_id = models.IntegerField(db_column=u'ci_gr_id', null=True, blank=True)
    prod_type = models.CharField(db_column=u'ci_prod_type', max_length=50, blank=True)
    prod_id = models.CharField(db_column=u'ci_prod_id', max_length=50, blank=True)
    prod_version = models.CharField(db_column=u'ci_prod_version', max_length=50, blank=True)
    date_reg = models.CharField(db_column=u'ci_date_reg', max_length=12, blank=True)
    date_from = models.CharField(db_column=u'ci_date_from', max_length=12, blank=True)
    date_to = models.CharField(db_column=u'ci_date_to', max_length=12, blank=True)
    status = models.CharField(db_column=u'ci_status', max_length=25, blank=True)
    extra = models.IntegerField(db_column=u'ci_extra', null=True, blank=True)

    class Meta:
        db_table = u'contract_item'

class Log(models.Model):
    id = models.IntegerField(db_column='lg_id', primary_key=True)
    object = models.TextField(db_column='lg_object', blank=True)
    object_id = models.TextField(db_column='lg_object_id', blank=True)
    timestamp = models.DateTimeField(db_column='lg_timestamp', null=True, blank=True)
    user = models.IntegerField(db_column='lg_us_id', null=True, blank=True)
    action = models.TextField(db_column='lg_action', blank=True)
    data = models.TextField(db_column='lg_data', blank=True)

    class Meta:
        db_table = u'log'
