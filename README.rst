=====
wacfg
=====

:Version: 0.0.1-alpha1
:Web: http://github.com/nutztherookie/wacfg
:Author: Andreas Nüßlein <nutz@noova.de>
:License: CDDL
Using wacfg is as simple as putting a wacfg.py next to your .tar.gz,

    Possible functions to be used:

    - src_unpack()
    - src_config()
    - src_install()
    - post_install()


    Tools:

    - archive_unpack()
    - archive_install()
    - mv(frompath, topath, wd=".")
    - chmod(mode, path="", recursive=False)
    - chown(owner, group=None, path="", recursive=False)
    - server_own(path="", recursive=False)


    Possible variables in source-string:

    - %(PN)s = package name
    - %(PV)s = package version
    - %(P)s  = "%(PN)s-%(PV)s"


