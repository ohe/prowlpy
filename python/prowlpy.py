#/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prowlpy V0.5 originally written by Jacob Burch, modified by Olivier Hervieu.

Python Prowlpy is a python module that implement the public api of Prowl to
send push notification to iPhones.

See http://prowl.weks.net for information about Prowl.

The prowlpy module respect the API of prowl. So prowlpy provides a Prowl class
which implements two methods :
- add, to push a notification to an iPhone,
- verify, to verify an API key.

Note : one things is missing in prowlpy; add currently can't send multiple 
prowl notification.

"""

__author__          = 'Jacob Burch@gmail.com'
__author_email__    = 'jacoburch@gmail.com'
__maintener__       = 'Olivier Hervieu'
__maintener_email__ = 'olivier.hervieu@gmail.com'
__version__         = 0.5

from httplib import HTTPSConnection as Https
from urllib  import urlencode
from xml.dom import minidom

API_DOMAIN = 'prowl.weks.net'

class Prowl(object):

    def __init__(self, apikey):
        """
        Initialize a Prowl instance.
        """
        self.apikey = apikey

        # Set User-Agent
        self.headers = {'User-Agent': "Prowlpy/%s" % str(__version__),
                        'Content-type': "application/x-www-form-urlencoded"}

        # Aliasing for backward compatibility
        self.post = self.add
        self.verify_key = self.verify

        # Members
        self._last_error = ''

    def add(self, application=None, event=None, description=None, priority=0, 
            providerkey=None):
        """
        Add a notification for a particular user.

        You must provide either event or description or both.
        
        The parameters are : 
        -   application ; The name of your application or the application 
            generating the event.
        -   providerkey (optional) : your provider API key. 
            Only necessary if you have been whitelisted.
        -   priority (optional) : default value of 0 if not provided. 
            An integer value ranging [-2, 2] representing:
              -2. Very Low
              -1. Moderate
               0. Normal
               1. High
               2. Emergency (note : emergency priority messages may bypass 
                             quiet hours according to the user's settings)
        -   event : the name of the event or subject of the notification.
        -   description : a description of the event, generally terse.
        """
        # Create the http object
        h = Https(API_DOMAIN)
        
        # Perform the request and get the response headers and content
        data = {
            'apikey': self.apikey,
            'application': application,
            'event': event,
            'description': description,
            'priority': priority

        }
        if providerkey is not None:
            data['providerkey'] = providerkey

        h.request(  "POST",
                    "/publicapi/add", 
                    headers=self.headers, 
                    body=urlencode(data))
        
        res = self._parse_prowl_response(h.getresponse().read())

        self._last_error = '' if res['code'] != 200 else res['message']
        return res

    def verify(self, providerkey=None):
        """
        Verify if the API key is valid.

        The parameters are :
        -   providerkey (optional) : your provider API key. 
            Only necessary if you have been whitelisted.
        """
        h = Https(API_DOMAIN)

        data = {'apikey' : self.apikey}

        if providerkey is not None:
            data['providerkey'] = providerkey

        h.request(  "GET",
                    "/publicapi/verify?"+ urlencode(data), 
                    headers=self.headers)
        
        res = self._parse_prowl_response(h.getresponse().read())

        self._last_error = '' if res['code'] != 200 else res['message']
        return res
   
    def get_last_error(self):
        return self._last_error

    def _parse_prowl_response(self, response):
        """
        Parse the prowl response.

        Doctest Purpose:
        >>> Prowl('dummykey')._parse_prowl_response('')
        {u'resetdate': None, u'message': None, u'code': None, u'remaining': None}
        >>> Prowl('dummykey')._parse_prowl_response('<?xml version="1.0" encoding="UTF-8"?>\\n<prowl>\\n<error code="401">Invalid API key(s).</error>\\n</prowl>')
        {u'resetdate': None, u'message': u'Invalid API key(s).', u'code': u'401', u'remaining': None}
        """
        
        response_as_dict = {    u'code'      : None, 
                                u'remaining' : None, 
                                u'resetdate' : None, 
                                u'message'   : None}

        dict_attr = {}

        try:
            parsed_response = minidom.parseString(response)
            #Is there a prowl response in?
            dom_elem_list = parsed_response.getElementsByTagName("prowl")
            if len(dom_elem_list)>0:
                for item in ["success","error"]:
                    dom_elem_list = parsed_response.getElementsByTagName(item)
                    if len(dom_elem_list) == 1:
                        dom_elem = dom_elem_list[0]
                        dict_attr = dict(dom_elem.attributes.items())
                        if dom_elem.hasChildNodes():
                            childs = dom_elem.childNodes
                            if len(childs)==1:
                                dict_attr[u'message'] = childs[0].data 
        except : pass 

        for attr in dict_attr :
            response_as_dict[attr]=dict_attr[attr]

        #DEBUG
        #print response_as_dict

        return response_as_dict

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
