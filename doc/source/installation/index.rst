.. _installation:

============
Installation
============
Using layman
------------
To use wacfg and the new ebuilds you will need to use the wacfg overlay, provided through layman:

.. code-block:: bash

  USE="git" emerge layman
  layman -f && layman -a wacfg
  emerge wacfg

Once wacfg has been successfully installed, you can emerge your desired $webapp from the overlay and deploy it with wacfg:

.. code-block:: bash

  emerge $webapp
  wacfg install $webapp --vhost my.example.com


