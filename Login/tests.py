from django.test import TestCase
import re
Password="Subhyoyo@34"
# Create your tests here.
regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
if len(Password)<8 or bool(re(r'/d',Password))==False or regex.search(Password)==None:
    print(True)