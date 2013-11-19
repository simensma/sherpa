# We will now define two sets of sherpa2-county mappings.
# Both are defined in sherpa2/langs/nor_public.php, but they differ slightly
# in that the second set combines the two counties 'Oslo' and 'Akershus' into one.
# The mappings will look up county code based on sherpa2 id.
# The reverse mappings will look up sherpa2 id based on county code.

# This first set is defined in $lang['activity']['counties'] and known usages are:
# - Activities
# - Associations
# - Probably more, add them here if you find any.
SHERPA2_COUNTIES_SET1 = {
     1: '01',
     2: '03',
     3: '04',
     4: '05',
     5: '06',
     6: '07',
     7: '08',
     8: '09',
     9: '10',
    10: '11',
    11: '12',
    12: '14',
    13: '15',
    14: '16',
    15: '17',
    16: '18',
    17: '19',
    18: '20',
    19: '02',
}
# The reverse mapping - looks up sherpa2 id based on county code
COUNTIES_SHERPA2_SET1 = {v: k for k, v in SHERPA2_COUNTIES_SET1.iteritems()}

# This second set is defined in in $lang['lists']['counties'] and known usages are:
# - Fjelltreffen-annonser.
# - Maybe more, add them here if you find any.
#
# Also note: The following sherpa2 keys have special meanings and will raise a KeyError:
#  0: The entire country
#  2: Defined as both Oslo and Akershus
# 99: International
# This means that the reverse mapping for counties '02/Akershus' and '03/Oslo' also will give KeyError.
SHERPA2_COUNTIES_SET2 = {
     1: '01',
     3: '04',
     4: '05',
     5: '06',
     6: '07',
     7: '08',
     8: '09',
     9: '10',
    10: '11',
    11: '12',
    12: '14',
    13: '15',
    14: '16',
    15: '17',
    16: '18',
    17: '19',
    18: '20',
}
# The reverse mapping - looks up sherpa2 id based on county code
COUNTIES_SHERPA2_SET2 = {v: k for k, v in SHERPA2_COUNTIES_SET2.iteritems()}
