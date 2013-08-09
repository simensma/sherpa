from core.models import County, FocusCountry, Zipcode
from focus.models import FocusZipcode

# This is a cleaner interface to an Actors address, based on Focus' ActorAddress model.
# It has three address fields (field{1,3}), a 'country' field ('core.models.FocusCountry').
# If the country is Norway, it also has a 'zipcode' field ('core.models.Zipcode') and a
# 'county' field ('core.models.County').
# The class has utility methods for typical formatting of addresses (with newlines, and for
# one line with commas).
class ActorAddressClean:
    def __init__(self, address):
        # Add fields, replacing NULL values with the empty string
        self.field1 = address.a1.strip() if address.a1 is not None else ''
        self.field2 = address.a2.strip() if address.a2 is not None else ''
        self.field3 = address.a3.strip() if address.a3 is not None else ''

        # Set the actual country object
        # Uppercase the country code (just in case - you never know with Focus)
        self.country = FocusCountry.objects.get(code=address.country_code.upper())

        if self.country.code == 'NO':
            # Norwegians - set the actual zipcode object
            try:
                self.zipcode = Zipcode.objects.get(zipcode=address.zipcode)
            except Zipcode.DoesNotExist:
                # Some addresses have NULL in the zipcode field for some reason.
                # Use a zipcode object with empty fields.
                self.zipcode = Zipcode()

            # Set the actual County object based on the zipcode
            if self.zipcode.zipcode != '':
                county_code = FocusZipcode.objects.get(zipcode=self.zipcode.zipcode).county_code
                if county_code == '99':
                    # International addresses have county code 99 in Focus. Define the county as None for now.
                    self.county = None
                else:
                    self.county = County.objects.get(code=county_code)
            else:
                self.county = None

        else:
            # Foreigners - ignore zipcode/area
            # Remove country code prefixes
            if self.field1.lower().startswith("%s-" % self.country.code.lower()):
                self.field1 = self.field1[len(self.country.code) + 1:].strip()
            if self.field2.lower().startswith("%s-" % self.country.code.lower()):
                self.field2 = self.field2[len(self.country.code) + 1:].strip()
            if self.field3.lower().startswith("%s-" % self.country.code.lower()):
                self.field3 = self.field3[len(self.country.code) + 1:].strip()

    # This is adapted for user page account details right now - if norwegian,
    # this doesn't display country, if foreigner, it does. If rewritten, account
    # for that and add parameters or something for that usage.
    def format_with_newlines(self):
        if self.country.code == 'NO':
            address_string = self.field1
            if self.field2 != '':
                address_string += '\n%s' % self.field2
            if self.field3 != '':
                address_string += '\n%s' % self.field3
            address_string += '\n%s %s' % (self.zipcode.zipcode, self.zipcode.area.title())
        else:
            address_string = ''
            if self.field1 != '':
                address_string += '%s\n' % self.field1
            if self.field2 != '':
                address_string += '%s\n' % self.field2
            if self.field3 != '':
                address_string += '%s\n' % self.field3
            address_string += "%s, %s" % (self.country.name, self.country.code)
        return address_string

    # This is adapted for NOR-WAY bus tickets emails right now. If rewritten,
    # account for that and add parameters or something for that usage.
    def format_for_oneline(self):
        address_string = self.field1
        if self.field2 != '':
            address_string += ', %s' % self.field2
        if self.field3 != '':
            address_string += ', %s' % self.field3

        if self.country.code == 'NO':
            address_string += ', %s %s' % (self.zipcode.zipcode, self.zipcode.area.title())
        else:
            address_string += ' (%s, %s)' % (self.country.name, self.country.code)
        return address_string
