=======
Prowlpy
=======

Orignally written by Jacob Burch, modified by Olivier Hervieu.

Python Prowlpy is a python module that implement the public api of Prowl to
send push notification to iPhones.

See http://prowl.weks.net for information about Prowl.

Prowlpy is avalaible both for python2.x and python3.x

The prowlpy module respect the API of prowl. So prowlpy provides a Prowl class
which implements two methods :
- add, to push a notification to an iPhone,
- verify, to verify an API key.


Dependencies 
============

- httplib/urllib (python internal's module)
- The socket module must be compiled with SSL support

Change Log
==========

V0.5
----

- Add python3 compatibility
- Parse prowls returned XML results
- Modification in the API to get better results 
  (error code, prowls message, remaining notifications...)
- Remove dependencies to httplib2 and replace it by httplib. 
  So prowlpy do not need externals python modules.
- Add a pythonic installer based on distutils.

V0.42
-----

- Got rid of Now-uncessary URL Encoding
- Working on incorporating forked changes while not totally breaking backward 
  compatibility with the vanilla add function

V0.41
-----

- Adding priority setting
- Removed debug code

V0.4
----

- Added Prowl.add alias for Post
- Switched post to use (oddly enough) POST instead of GET
- Added a Prowl.veryify_key method

V0.3
----

- Changed to handle the new API system

V0.2
----

- Basic working module

Todo
----

- Test against character-limits
- allow multiple apikey in Prowl constructor
- Add more test unit

