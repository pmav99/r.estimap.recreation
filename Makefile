MODULE_TOPDIR = ../..

PGM = r.estimap.recreation

ETCFILES = colors constants labels

include $(MODULE_TOPDIR)/include/Make/Script.make
include $(MODULE_TOPDIR)/include/Make/Python.make

default: script
