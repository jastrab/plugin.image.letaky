# -*- coding: utf-8 -*-
import os
sys.path.append( os.path.join ( os.path.dirname(__file__),'resources','lib') )

import letaky
import sys

if __name__ == '__main__':
    letaky.router(sys.argv[2][1:])