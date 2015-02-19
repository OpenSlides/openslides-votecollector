=================================
 OpenSlides VoteCollector Plugin
=================================

Overview
========

This plugin connects OpenSlides with the software "VoteCollector" to
provide electronic voting for motions with Keypads from `Voteworks
<http://www.voteworks.de>`_.

The OpenSlides VoteCollector Plugin was contracted by the German company
Voteworks GmbH. It was initially developed by the core authors of
OpenSlides, Oskar Hahn and Emanuel Schütze (`Intevation GmbH
<http://www.intevation.de/>`_), in April 2012. Currently, it is maintained
by Emanuel Schütze.


Requirements
============

- OpenSlides 1.7.x
- VoteCollector 1.3.4


Install
=======

I. Installation on Windows (with OpenSlides portable version)
-------------------------------------------------------------

1. Install and run VoteCollector

   Download VoteColletor from http://files.softwein.de/VoteCollector.zip

   To use VoteCollector in simulation mode (no keypads required)
   please run from command line::

     VoteCollector.exe -s

   Note: You have to buy a license key for VoteCollector to use more than 5 keypads.
   See http://www.voteworks.de/TedSystem-Anwendungen/Mitgliederversammlungen/VoteCollector-OpenSlides.html

2. Get latest VoteCollector plugin release from:

   https://github.com/OpenSlides/openslides-votecollector/tags

3. Move the (extracted) subdirectory 'openslides_votecollector' to::

     '<path-to-openslides-portable>/openslides/plugins/'

5. Start openslides.exe.


Now the plugin installation is finished. You can open the new menu
item 'VoteCollector' in the main navigation of OpenSlides.

Change settings of plugin under 'Configuration > VoteCollector'.


II. Installation on GNU/Linux and MacOSX
----------------------------------------

1. Install and run VoteCollector (on Windows only, e.g. in a VirtualBox machine)

   Download VoteColletor from http://files.softwein.de/VoteCollector.zip

   To use VoteCollector in simulation mode (no keypads required)
   please run from command line::

     VoteCollector.exe -s

   Note: You have to buy a license key for VoteCollector to use more than 5 keypads.
   See http://www.voteworks.de/TedSystem-Anwendungen/Mitgliederversammlungen/VoteCollector-OpenSlides.html

2. Setup and activate a virtual environment::

    $ virtualenv .virtualenv

    $ source .virtualenv/bin/activate

3. Install OpenSlides and VoteCollector plugin from the Python Package Index (PyPI)::

    $ pip install openslides openslides-votecollector

    OpenSlides and all required python packages will be installed.

4. Start OpenSlides::

    $ openslides


Now the plugin installation is finished. You can open the new menu
item 'VoteCollector' in the main navigation of OpenSlides.

Change settings of plugin under 'Configuration > VoteCollector'.


Seating plan
============

To change the seating plan edit ``openslides_votecollector/seating_plan.py``
and change the creation of Seat objects in the setup_default_plan() function.


License and authors
===================

This plugin is Free/Libre Open Source Software and distributed under the
MIT License, see LICENSE file. The authors are mentioned in the AUTHORS file.


Changelog
=========

Next version (unreleased)
-------------------------


Version 1.1 (2015-01-23)
------------------------
* Updated to OpenSlides 1.7.x/1.6.x.
* Updated for VoteCollector 1.3.4.
* Added personal and anonymous voting.
* New config options for live mode and seating plan.
* Show keypad serial number in list.
* Updated motion poll slides.


Version 1.0.4 (2013-12-04)
--------------------------
* Updated to OpenSlides 1.5.x.
* Added README and requirements.txt.
* Added fabfile and unit tests.
* Changed license to MIT.


Version 1.0.3 (2012-12-14)
--------------------------
* Updated INSTALL.txt.
* Added setup.py for easier install.


Version 1.0.2 (2012-12-12)
--------------------------
* Updated to OpenSlides 1.3.x.


Version 1.0.1 (2012-07-25)
--------------------------
* Updated to OpenSlides 1.2.x.


Version 1.0 (2012-05-21)
------------------------
* First release of this plugin for OpenSlides 1.1.x.
