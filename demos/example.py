"""
Example notification using prowl.
"""
import prowlpy

apikey = '1234567890123456789012345678901234567890' #Dummy API-key)
p = prowlpy.Prowl(apikey)
try:
    print p.verify()
    print p.add('TestApp','Server Down',"The Web Box isn't responding to a ping")
except Exception,msg:
    print msg
