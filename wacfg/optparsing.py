
def waopts():
    from optparse import OptionParser, OptionGroup
    parser = OptionParser()

    group = OptionGroup(parser, 'Install location')

#    group.add_option("-i", "--install", action="store_true", dest="install",
#            default=False, help="Install package")
#    group.add_option("-u", "--upgrade", action="store_true", dest="upgrade",
#            default=False, help="Update or install package")
#    group.add_option("-r", "--remove", action="store_true", dest="remove",
#            default=False, help="Remove package while leaving manually changed files intact")
#    group.add_option("-p", "--purge", action="store_true", dest="purge",
#            default=False, help="Purge package - remove the whole directory")



    group.add_option("-H", "--vhost", dest="vhost",
            help="Specify the vhost, default is localhost")

    group.add_option("-d", "--dir", dest="installdir",
            help="Specify another install directory")

    group.add_option("-s", "--server", dest="server",
            default=None, help="Which server to use. If multiple are installed, apache will be used")

    group.add_option("-W", "--wwwroot", dest="wwwroot",
            default="/var/www", help="Specify the wwwroot. Default is '/var/www/'")

    parser.add_option_group(group)

    group = OptionGroup(parser, "Information Options")
    group.add_option("-v", action="count", dest="verbosity",
            help="Increase verbosity")
    parser.add_option_group(group)

    return parser


