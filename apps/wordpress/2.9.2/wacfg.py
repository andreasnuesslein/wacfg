from WaCfg import main, WaCfg, tools, Env

class WordPressHandler(WaCfg):
    __version__ = 0.1

#    def src_unpack(self):
#        tools.archive_unpack('wordpress-2.9.2')
#
#    def src_config(self):

main(WordPressHandler,
#main(
        source = "wordpress-2.9.2")
