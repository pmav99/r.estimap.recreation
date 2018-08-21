#!/usr/bin/env python

#%module
#% description: Generates PyQt GUI of module
#%end
#%option module
#% key: module
#% description: Module to be interfaced
#% required: yes
#%end

import sys
from subprocess import PIPE

import grass.script as grass

from forms import NewGUI

def main():
    NewGUI(options['module'])

if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
