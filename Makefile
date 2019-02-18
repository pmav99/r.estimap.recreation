MODULE_TOPDIR = ../..

PGM = r.estimap.recreation

SUBDIRS = estimap_recreation

include $(MODULE_TOPDIR)/include/Make/Script.make
include $(MODULE_TOPDIR)/include/Make/Dir.make

default: parsubdirs htmldir script

install: installsubdirs
	$(INSTALL_DATA) $(PGM).html $(INST_DIR)/docs/html/
