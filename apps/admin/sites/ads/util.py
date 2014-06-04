import re

def parse_adform_script_destination(script):
    return re.findall(r'(\<a href=\")(.+?)(\")', script)[0][1]
