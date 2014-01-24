# encoding: utf-8
from django.contrib.gis.db import models
from django.core.cache import cache

from datetime import datetime, date, timedelta
import json

# Sometimes we'll need to reference foreninger directly by ID. We'll store the IDs we know and need here.
DNT_OSLO_ID = 2
DNT_UNG_OSLO_ID = 152

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
    orgnr = models.CharField(db_column='gr_orgnr', max_length=20, blank=True)
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
            locations = set([Location.get_active().get(code=l) for l in self.locations.split('|') if l != ''])
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

    class Meta:
        db_table = u'location2'

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
    sql_id = models.IntegerField(db_column='id')
    object_id = models.CharField(db_column='oid', max_length=24, unique=True)
    type = models.CharField(max_length=1)

    class Meta:
        db_table = 'ntb_id'
