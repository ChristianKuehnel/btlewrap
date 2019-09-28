btlewrap
========

Bluetooth LowEnergy wrapper for different python backends. This gives you a nice API so that you can use different Bluetooth implementations on different platforms.

This library was initially implemented as part of the `miflora <https://github.com/open-homeautomation/miflora>`_ library, but then refactored out, so that it can be used on other projects as well.

contribution
============
.. image:: https://travis-ci.org/ChristianKuehnel/btlewrap.svg?branch=master
    :target: https://travis-ci.org/ChristianKuehnel/btlewrap

.. image:: https://coveralls.io/repos/github/ChristianKuehnel/btlewrap/badge.svg?branch=master
    :target: https://coveralls.io/github/ChristianKuehnel/btlewrap?branch=master

Backends
========
As there is unfortunately no universally working Bluetooth Low Energy library for Python, the project currently 
offers support for three Bluetooth implementations:

* bluepy library (recommended library)
* bluez tools (via a wrapper around gatttool)
* pygatt for Bluegiga BLED112-based devices

bluepy
------
To use the `bluepy <https://github.com/IanHarvey/bluepy>`_ library you have to install it on your machine, in most cases this can be done via: 

:: 

    pip3 install bluepy
    
This is the recommended backend to be used. In comparision to the gatttool wrapper, it is much faster in getting the data and also more stable.
    
    
bluez/gatttool wrapper
----------------------
To use the bluez wrapper, you need to install the bluez tools on your machine. No additional python 
libraries are required. Some distrubutions moved the gatttool binary to a separate package. Make sure you have this 
binaray available on your machine.




pygatt
------
If you have a Blue Giga based device that is supported by `pygatt <https://github.com/peplin/pygatt>`_, you have to
install the bluepy library on your machine. In most cases this can be done via: 

::

    pip3 install pygatt

Usage
=====
See the depending projects below on how to use the library.

Depending projects
==================
These projects are using btlewrap:

* `miflora <https://github.com/open-homeautomation/miflora>`_
* `mitemp <https://github.com/flavio20002/mitemp_bt>`_
