from WaCfg import main, WaCfg, tools

class WordPressHandler(WaCfg):
    __version__ = 0.1

main(WordPressHandler,
        source = "wordpress-2.9.2")
