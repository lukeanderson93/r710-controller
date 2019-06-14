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

    [IPMI] - (192.168.1.6) - User: root, Password: **********
    [IPMI] - (192.168.1.6) - Powering on.
    [IPMI] - (192.168.1.6) - Activating manual fan control, fan speed: 10%.

Getting sensor data:

.. code:: python
 
    print(f'Power status: {s.get_power_status()}')
    print(f'Fan speed: {s.get_fan_speed()}')
    print(f'Ambient temp: {s.get_temp()}')
    
Output:

.. code:: bash

    [IPMI] - (192.168.1.6) - User: root, Password: **********
    Power status: ON
    Fan speed: 2400
    Ambient temp: 23

A simple script to keep fanspeed low. Not recommended for servers with high CPU usage.

.. code:: python

    import time
    from controller import Server
    
    s = Server(host='192.168.1.6', username='root', password='********')
    s.power_on(fan_speed_pct=10)
    
    while True:
        temp = s.get_temp()
        print(f'Current temp: {temp}')

        # if the ambient temp is above 27, set the fanspeed back to automatic
        if temp > 27:
            s.set_fan_speed_auto()
        time.sleep(60)

Alternatively, set the fan speed based on the current temperature (could be set up as system service, or cron job).

.. code:: python

    import time
    from controller import Server
    
    MIN_TEMP = 21
    MAX_TEMP = 30
    
    s = Server(host='192.168.1.6', username='root', password='********')
    s.power_on(fan_speed_pct=10)
    
    while True:
        temp = s.get_temp()
        
        # if the temp is in the current range, check
        if MIN_TEMP <= temp <= MAX_TEMP:
            pct = int((temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP) * 100)
            pct = 100 if pct>100 else pct
            pct = 1 if pct<1 else pct
            print(f'Setting fanspeed to {pct}%.')
            s.set_fan_speed_manual(fan_speed_pct=pct)
        else:
            # raise an error, send an email, do an alert, etc.
            pass
        time.sleep(60)

Powering down:

.. code:: python
    
    s.power_off_soft()

Output:

.. code:: bash

    [IPMI] - (192.168.1.6) - Executing graceful shutdown.

Submitting raw commands:

.. code:: python

    print(s.do_cmd('sdr list'))

.. code:: bash

    [IPMI] - (192.168.1.6) - User: root, Password: **********
    Temp             | disabled          | ns
    Temp             | disabled          | ns
    Temp             | disabled          | ns
    Temp             | disabled          | ns
    Ambient Temp     | 24 degrees C      | ok
    Planar Temp      | disabled          | ns
    CMOS Battery     | 0x00              | ok
    VCORE PG         | 0x00              | ok
    VCORE PG         | 0x00              | ok
    0.75 VTT CPU2 PG | 0x00              | ok
    [...]


.. code:: python

    print(s.do_cmd('chassis power'))

.. code:: bash

    [IPMI] - (192.168.1.6) - User: root, Password: **********
    chassis power Commands: status, on, off, cycle, reset, diag, soft

License
-------
Copyright © 2019 `Luke Anderson`_, released under The `MIT License`_.

.. _Luke Anderson: luke@lukeanderson.co.uk
.. _MIT License: http://mit-license.org
