#!/usr/bin/env python
from wacfg import main, WaCfg, tools

class MyApp(WaCfg):
    def src_config(self):
        #tools.chmod("0750", "temp", recursive=True)
        #tools.chmod("0050", "logs", recursive=True)
        tools.server_own(recursive=True)



main(MyApp, source="%(PN)smail-%(PV)s.tar.gz")

print("""
Post install instructions:
- Create a new database and a database user for RoundCube (see DATABASE SETUP)
- Point your browser to http://url-to-roundcube/installer/
- Follow the instructions of the install script (or see MANUAL CONFIGURATION)
- After creating and testing the configuration, remove the installer directory
""")
