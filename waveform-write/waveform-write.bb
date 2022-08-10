
# This file is based on the rfdc-data-write-example recipe.
#

SUMMARY = "Waveform input for DAC according to .txt file"
SECTION = "PETALINUX/apps"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " file://board.h \
	   file://rfdc_interface.h \
	   file://common.h \
	   file://rfdc_functions.h \
	   file://data_interface.h \
	   file://clock_interface.h \
	   file://rfdc_interface.c \
	   file://common.c \
	   file://gpio.c \
	   file://gpio.h \
	   file://rfdc_functions.c \
	   file://data_interface.c \
	   file://clock_interface.c \
	   file://waveform-write.c \
	   file://Makefile \
         "

S = "${WORKDIR}"

TARGET_CC_ARCH += "${LDFLAGS}"

DEPENDS = "libmetal"
DEPENDS = "rfdc"

do_install() {
	     install -d ${D}/${bindir}
	     install -m 0755 ${S}/waveform-write ${D}/${bindir}
}
