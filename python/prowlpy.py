#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009, Jaccob Burch
# Copyright (c) 2009, Olivier Hervieu
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Prowlpy V0.5 originally written by Jacob Burch, modified by Olivier Hervieu.

Python Prowlpy is a python module that implement the public api of Prowl to
send push notification to iPhones.

See http://prowl.weks.net for information about Prowl.

Prowlpy is avalaible both for python2.x and python3.x

The prowlpy module respect the API of prowl. So prowlpy provides a Prowl class
which implements two methods :
- add, to push a notification to an iPhone,
- verify, to verify an API key.

Note : one things is missing in prowlpy; add currently can't send multiple 
prowl notification.

"""

__author__           = 'Jacob Burch@gmail.com'
__author_email__     = 'jacoburch@gmail.com'
__maintainer__       = 'Olivier Hervieu'
__maintainer_email__ = 'olivier.hervieu@gmail.com'
__version__          = '0.5.1'

from sys import version as _python_version

#Detecting python version
if _python_version[0] == '2':
    from httplib import HTTPSConnection as Https
    from urllib  import urlencode
elif _python_version[0] == '3':
    from http.client import HTTPSConnection as Https
    from urllib.parse import urlencode
from xml.dom import minidom

API_DOMAIN = 'prowl.weks.net'

class Prowl(object):

    def __init__(self, apikey):
        """
        Initialize a Prowl instance. It need an apikey.
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
        >>> EXPECTED_RESULT = { 'resetdate': None, 
        ...                     'message': None, 
        ...                     'code': None, 
        ...                     'remaining': None}
        >>> Prowl('dummykey')._parse_prowl_response('') == EXPECTED_RESULT
        True
        >>> EXPECTED_RESULT = { 'resetdate': None, 
        ...                     'message': 'Invalid API key(s).', 
        ...                     'code': '401', 
        ...                     'remaining': None}
        >>> TEST_STRING = '<?xml version="1.0" encoding="UTF-8"?>\\n<prowl>\\n<error code="401">Invalid API key(s).</error>\\n</prowl>'
        >>> Prowl('dummykey')._parse_prowl_response(TEST_STRING) == EXPECTED_RESULT
        True
        """
        
        response_as_dict = {    'code'      : None, 
                                'remaining' : None, 
                                'resetdate' : None, 
                                'message'   : None}

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
                                dict_attr['message'] = childs[0].data 
        except : pass 

        for attr in dict_attr :
            response_as_dict[attr]=dict_attr[attr]

        #DEBUG
        #print(response_as_dict)

        return response_as_dict

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
