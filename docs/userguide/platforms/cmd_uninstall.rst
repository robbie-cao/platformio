..  Copyright 2014-present Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _cmd_platforms_uninstall:

platformio platforms uninstall
==============================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platforms uninstall PLATFORM


Description
-----------

Uninstall specified :ref:`platforms`


Examples
--------

.. code-block:: bash

    $ platformio platforms uninstall timsp430
    Uninstalling toolchain-timsp430 package:        [OK]
    Uninstalling tool-mspdebug package:             [OK]
    Uninstalling framework-energiamsp430 package:   [OK]
    The platform 'timsp430' has been successfully uninstalled!
