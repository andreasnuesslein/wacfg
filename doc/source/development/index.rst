=========================
Development documentation
=========================
| Writing wacfg-configfiles is *easy*!
| All you need to do is, create a python-file, specifying 1 or 2 variables and you're good to go.
|
| Check out :ref:`this example <wordpress-example>` of wordpress.
| 


.. _wordpress-example:

Example: wordpress-3.0.1.wa
---------------------------

Create a temporary folder you will be using to test your new webapp:

.. code-block:: bash

  mkdir -p ~/tmp/wordpress/
  cd ~/tmp/wordpress/

In this folder, create another folder named *sources* and put your sources inside:

.. code-block:: bash

  mkdir sources/

  wget -O sources/wordpress-3.0.1.tar.gz "http://wordpress.org/latest.tar.gz"
  #or if you have them on your harddrive:
  cp /path/to/sources/wordpress-3.0.1.tar.gz sources/wordpress-3.0.1.tar.gz

Create **wordpress-3.0.1.wa**:

.. code-block:: python

  #!/usr/bin/env python
  from wacfg import main

  main(sources="%(P)s.tar.gz")

and make it executable:

.. code-block:: bash

  chmod +x wordpress-3.0.1.wa


That's it. You can now execute your file in the usual manner:

.. code-block:: bash

  ./wordpress-3.0.1.wa install --vhost example.com


.. _definitions:

Function definitions for the WaCfg class
----------------------------------------
If you need to change certain steps of the build process, you can create your own class extending "WaCfg":

.. code-block:: python

  #!/usr/bin/env python
  from wacfg import main, WaCfg

  class MyApp(WaCfg):
      def src_unpack(self):
          tools.archive_unpack()
      def src_config(self):
          tools.server_own(recursive=True)
      def src_install(self):
          tools.archive_install()
      def post_install(self):
          pass

  main(MyApp, source="sourcefile.tar.gz")

This example is the default behavior of WaCfg. You can specify as many or as little of these functions as you want.

In the following section is a list of possible tools to use:

Tools and Variables
-----------------------
These tools are currently available:

.. code-block:: python

  tools.mv(self, frompath, topath, wd="")
  tools.cp(self, frompath, topath, wd="")
  tools.rm(self, rmpath, wd="", recursive=False)
  tools.rsync(self, frompath, topath, wd="")
  tools.wget(self, path)
  tools.chmod(self, mode, path="", recursive=False)
  tools.chown(self, owner, group=None, path="", recursive=False)
  tools.server_own(self, path="", recursive=False)
  tools.archive_unpack(self)
  tools.archive_install(self)

The following variables can be used within the custom class:

.. code-block:: python

  class Env:
      p = "Package name and version, e.g. mywebapp-0.1"
      pn = "Package name"
      pv = "Package version"
      sboxpath = "The root-directory in the 'sandbox', e.g. /var/tmp/webapps/mywebapp/"
      vhost = "Specified vhost, defaulting to 'localhost'"
      installdir = "The relative path, the webapp is going to be installed to"
      wwwroot = "Default: '/var/www/'"
      destpath = "wwwroot + vhost + 'htdocs' + installdir"


.. code-block:: python

  #example
  class MyApp(WaCfg):
      print(Env.pn)
      def src_config(self):
          print(self.Env.wwwroot)

.

