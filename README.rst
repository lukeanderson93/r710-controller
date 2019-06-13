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

.. code-block:: python
    from controller import Server
    
    if __name__ == '__main__':
    
        # set environment variable: IDRAC_PASSWORD, or provide it here.
        s = Server(host='192.168.1.6', username='root', password='********')
        s.power_on(fan_speed_pct=10)
        
        print(s.get_power_status())
        print(s.do_cmd('sdr list'))
        
        s.set_fan_speed_manual(fan_speed_pct=30)
        s.set_fan_speed_auto()
        s.get_fan_speed()
        
        print(s.get_temp())
        
        s.power_off_soft()

License
-------
Copyright © 2019 `Luke Anderson`_, released under The `MIT License`_.

.. _Luke Anderson: luke@lukeanderson.co.uk
.. _MIT License: http://mit-license.org
