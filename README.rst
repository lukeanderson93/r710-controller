r710-controller
========================

Installation
------------
Install ipmitool and clone the repository

.. code-block:: bash

    $ apt install ipmitool
    $ git clone git@github.com:huberu/r710-controller.git

Usage
-----


.. code:: python

    from controller import Server
    s = Server(host='192.168.1.6', username='root', password='********')
    s.power_on(fan_speed_pct=10)

Output:

.. code:: bash

    [IPMI] - (192.168.1.6), User: root, Password: **********
    [IPMI] - (192.168.1.6) - Turning on.
    [IPMI] - (192.168.1.6) - Activating manual fan control, fan speed: 10%.
    
.. code:: python
 
    print(s.get_power_status())

Output:

.. code:: bash


.. code:: python
 
    print(s.do_cmd('sdr list'))

Output:

.. code:: bash


.. code:: python
 
    s.set_fan_speed_manual(fan_speed_pct=30)
    s.set_fan_speed_auto()
    s.get_fan_speed()

Output:

.. code:: bash

    

.. code:: python

    print(s.get_temp())
    s.power_off_soft()

Output:

.. code:: bash

    [IPMI] - (192.168.1.6), User: root, Password: **********
    [IPMI] - (192.168.1.6) - Executing graceful shutdown.




License
-------
Copyright © 2019 `Luke Anderson`_, released under The `MIT License`_.

.. _Luke Anderson: luke@lukeanderson.co.uk
.. _MIT License: http://mit-license.org
