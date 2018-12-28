#!/usr/bin/env python

import os
import sys
import subprocess

########### ########### ########### ########### ########### ########### ########### ########### ###########
########### ########### ########### ########### ########### ########### ########### ########### ###########
# path to the GRASS GIS launch script
# Linux
grass7bin_lin = 'grass'
# DATA
# define GRASS DATABASE # add your path to grassdata (GRASS GIS database) directory "~
gisdb = os.path.join(os.path.expanduser("/DATA2/"), "grassdata")
# specify (existing) location and mapset
location = "INCA_R"
mapset = "recreation"

########### SOFTWARE
if sys.platform.startswith('linux'):
    # we assume that the GRASS GIS start script is available and in the PATH
    # query GRASS 7 itself for its GISBASE
    grass7bin = grass7bin_lin

# query GRASS 7 itself for its GISBASE
startcmd = [grass7bin, '--config', 'path']

p = subprocess.Popen(startcmd, shell=False,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print >> sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)
gisbase = out.strip('\n\r')

# Set GISBASE environment variable
os.environ['GISBASE'] = gisbase
# the following not needed with trunk
os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)
########### ########### ########### ########### ########### ########### ########### ########### ###########

# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb

# looking(script, '*command*')
# import GRASS Python bindings (see also pygrass)
import grass.script as gscript
import grass.script.setup as gsetup
import grass.script as grass

###########
# launch session
gsetup.init(gisbase,
            gisdb, location, mapset)

gscript.message('Current GRASS GIS 7 environment:')
print gscript.gisenv()

gscript.message('Available raster maps:')

rasterL = []
for rast in gscript.list_strings(type='rast'):
    rasterL.append(rast)
rasterL = [rast.replace('@recreation', '') for rast in rasterL]
print rasterL
vectlist = []
for vect in gscript.list_strings(type='vect'):
    vectlist.append(vect)

vectlist = [vect.replace('@recreation', '') for vect in vectlist]


# this function nomalizes a file and delete the input####
def normalize(inras, outras):
    min = grass.raster_info(inras)['min']
    max = grass.raster_info(inras)['max']
    grass.mapcalc("$outras = float(($inras -$valuem) / ($valueM-$valuem))", inras=inras, outras=outras, valuem=min,
                  valueM=max, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)


# this function set 0 to null
def setnull_0(inras, outras):
    zero = 0
    grass.mapcalc("$outras = float(if(isnull($inras),$zeroV,$inras))", inras=inras, outras=outras, zeroV=zero,
                  overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)


# this function setnull to 1
def setnull_1(inras, outras):
    uno = 1
    grass.mapcalc("$outras = float(if(isnull($inras),$unoV,$inras))", inras=inras, outras=outras, unoV=uno,
                  overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)


# this function compute the f(d) on the euclidean distance
def f_d_euclidean(inras, outras, alpha, kappa, score):
    uno = 1
    grass.mapcalc("$outras = float(($alpha + $unoV) / ($alpha + exp($inras * $kappa)) * $score)", inras=inras,
                  outras=outras, unoV=uno, kappa=kappa, alpha=alpha, score=score, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)


def mask(inras, outras, mask):
    grass.mapcalc("$outras = float($inras * $mask)", inras=inras, outras=outras, mask=mask, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)


def get_cnt(lVals):
    d = dict(zip(lVals, [0] * len(lVals)))
    for x in lVals:
        d[x] += 1
    return d


def urlify(s):
    s = re.sub(r"[^\w\s]", '', s)  # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"\s+", '-', s)  # Replace all runs of whitespace with a single dash
    return s


def maskout(maskout, inras, outras):
    zero = 0
    grass.mapcalc("$outras = if($maskout == $zeroV, $zeroV, $inras)", inras=inras, outras=outras, zeroV=zero,
                  maskout=maskout, overwrite=True)


def mask(inras, outras, mask):
    grass.mapcalc("$outras = float($inras * $mask)", inras=inras, outras=outras, mask=mask, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)


# LC = "LUse"
# SLSRA_rules = "/DATA4/python_codes/ES/CdF/recode_recreation.txt"
# SLSCA_rules = "/DATA4/python_codes/ES/CdF/recode_cultural.txt"


# This function makes a dictionary with scores and count
def get_cnt(lVals):
    d = dict(zip(lVals, [0] * len(lVals)))
    for x in lVals:
        d[x] += 1
    return d

# ###############################################################################
# ############################ PATHS TO RULES ###################################
# ###############################################################################
urban_rules = "/DATA2/grassdata/INCA_R/scores/recode_urban.txt"
recodeRP_rules = "/DATA2/grassdata/INCA_R/scores/recode_RP2.txt"
proximity_rules = "/DATA2/grassdata/INCA_R/scores/recode_proximity.txt"
#
# # recodeRP_rules = "/media/grazia/Data/python_codes/Caingorms/recode_RP2.txt"#recode rules for Lurban distance ROS1recode_RP
# # roads = 'roads'
# #
# # RP='RP_01'
# # CP='CP_01'
RroadD_rec = 'prox_rd'
mask = 'lakes3'#'Buff80kmM'
# mask = 'testmasksea2'
grass.run_command('g.region', flags='p', rast=mask)
deletef = []

computationlist = []
for i, r in enumerate(rasterL):
    if r == 'clc2006': #r[:4] == 'CLC_'
        computationlist.append(r)
    else:
        pass
print computationlist
for r in computationlist:
    year = r[-4:]
    print year

    grass.run_command("r.reclass", input= r, output="urban"+year, rules = urban_rules,overwrite = True)
    deletef.append('urban'+year)
#
    grass.run_command("r.grow.distance", input= "urban"+year, distance = "dist_ur"+year, metric = "euclidean", overwrite = True)
    deletef.append('dist_ur'+year)
    grass.run_command("r.recode", input= "dist_ur"+year, output="dist_urR"+year, rules =proximity_rules, overwrite = True)
#     deletef.append('dist_ur'+year)
#     #
#     grass.run_command("r.recode", input= 'RP00NV3'+year, output="RP_rec"+year, rules =recodeRP_rules, overwrite = True) #input for ROS2
#     deletef.append('RP_rec')
#
#
#     #    exp03 = 'ROS1' + year +  ' =  if('+'dist_urR' + year + ' <= 2 & prox_rd <= 2, 1, if(('+'dist_urR' + year+' == 3 & prox_rd <= 3 | '+'dist_urR' + year+' == 1 & prox_rd <= 3 | '+'dist_urR' + year+' == 2 & prox_rd <= 3), 2, if(('+'dist_urR' + year+' => 4 & prox_rd <= 1 | '+'dist_urR' + year+' == 4 & prox_rd == 2 | '+'dist_urR' + year+' <= 2 & prox_rd == 4), 3, if(('+'dist_urR' + year+' == 2 & prox_rd == 2 | '+'dist_urR' + year+' >= 4 & prox_rd == 3 | '+'dist_urR' + year+' == 3 & prox_rd == 4 | '+'dist_urR' + year+' <= 2 & prox_rd == 5 | '+'dist_urR' + year+' == 5 & prox_rd == 2), 4, if(('+'dist_urR' + year+' >= 4 & prox_rd == 4 | '+'dist_urR' + year+' >= 3 & prox_rd == 5), 5)))))'
#     #    print exp03
#     exp03 = 'ROS1' + year + ' =  if(' + 'dist_urR' + year + ' <= 2 & prox_rd <= 2, 1, \
#                                        if(' + 'dist_urR' + year + ' == 3 & prox_rd <= 3 | ' + 'dist_urR' + year + ' == 1 & prox_rd == 3 | ' + 'dist_urR' + year + ' == 2 & prox_rd == 3, 2, \
#                                        if(' + 'dist_urR' + year + ' >= 4 & prox_rd <= 2 | ' + 'dist_urR' + year + ' == 4 & prox_rd == 2 | ' + 'dist_urR' + year + ' <= 2 & prox_rd == 4, 3, \
#                                        if(' + 'dist_urR' + year + ' == 5 & prox_rd == 2 | ' + 'dist_urR' + year + ' >= 4 & prox_rd == 3 | ' + 'dist_urR' + year + ' == 3 & prox_rd == 4 | ' + 'dist_urR' + year + ' <= 2 & prox_rd == 5, 4, \
#                                        if(' + 'dist_urR' + year + ' >= 4 & prox_rd == 4 | ' + 'dist_urR' + year + ' >= 3 & prox_rd == 5), 5))))'
#
#     #
#
#     grass.mapcalc(exp03, quiet=False, verbose=False, overwrite=True)
#     ##
#     ##
#     exp04 = 'ROS2' + year + ' = (if(' + 'ROS1' + year + ' >= 4 &  ' + 'RP_rec' + year + '  == 1 | ' + 'ROS1' + year + ' == 5 & ' + 'RP_rec' + year + '  == 2, 1,\
#                                            if(' + 'ROS1' + year + ' == 3 & ' + 'RP_rec' + year + ' <= 2, 2, \
#                                            if(' + 'ROS1' + year + ' <= 2 & ' + 'RP_rec' + year + ' == 1, 3, \
#                                            if(' + 'ROS1' + year + ' >= 4 & ' + 'RP_rec' + year + ' == 3 | ' + 'ROS1' + year + ' == 4 & ' + 'RP_rec' + year + '  == 2, 4, \
#                                            if(' + 'ROS1' + year + ' == 2 & ' + 'RP_rec' + year + ' == 2 | ' + 'ROS1' + year + ' == 2 & ' + 'RP_rec' + year + '  == 3, 5, \
#                                            if(' + 'ROS1' + year + ' == 1 & ' + 'RP_rec' + year + ' == 2 | ' + 'ROS1' + year + ' == 1 & ' + 'RP_rec' + year + '  == 3, 6, \
#                                            if(' + 'ROS1' + year + ' >= 4 & ' + 'RP_rec' + year + ' == 4, 7, \
#                                            if(' + 'ROS1' + year + ' == 3 & ' + 'RP_rec' + year + '  >= 3, 8, \
#                                            if(' + 'ROS1' + year + ' <= 2 & ' + 'RP_rec' + year + '  == 4,9))))))))))'
#
#     grass.mapcalc(exp04, quiet=False, verbose=False, overwrite=True)
# #
# Deletefiles = ",".join(deletef)
# grass.run_command('g.remove', flags='f', type='raster', name=deletef, quiet=True)

print "end"