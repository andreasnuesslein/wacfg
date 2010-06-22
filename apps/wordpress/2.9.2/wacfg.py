from WaCfg import main, WaCfg, tools

class WordPressHandler(WaCfg):
    __version__ = 0.1

#def src_unpack(self):
#    tools.archive_unpack('wordpress-2.9.2')

main(WordPressHandler,
        source = "wordpress-2.9.2")
