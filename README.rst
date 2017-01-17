=============================
edunext-openedx-extensions
=============================

.. image:: https://badge.fury.io/py/edunext-openedx-extensions.png
    :target: https://badge.fury.io/py/edunext-openedx-extensions

.. image:: https://travis-ci.org/jfavellar90/edunext-openedx-extensions.png?branch=master
    :target: https://travis-ci.org/jfavellar90/edunext-openedx-extensions

The separate microsites app for Edunext purposes
A package to extend open-edx modules

Overview
--------

This django application is to be used together with the openedx platform. It
extends some django modules from open-edx platform to ease the building of new features
without touching core platform code and having an isolated testing environment

How to install
--------------
```
git clone https://github.com/eduNEXT/edunext-openedx-extensions.git
cd edunext-openedx-extensions/
mkdir ../VENVS
virtualenv ../VENVS/edunext-openedx-extensions
source ../VENVS/edunext-openedx-extensions/bin/activate
make requirements
```

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.
