import os, sys

class WaCfg:
    def src_unpack(self):
        packet = os.path.basename(os.path.abspath(os.path.curdir))
        print(packet)





def main(Handler):
    Handler().src_unpack()
