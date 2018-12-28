#!/usr/bin/env python
#Infrastructures



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
gisdb = os.path.join(os.path.expanduser("/DATA4/"), "grassdata")
# specify (existing) location and mapset
location = "Trento"
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
# print gscript.gisenv()

gscript.message('Available raster maps:')
rasterL = []
for rast in gscript.list_strings(type='rast'):
    rasterL.append(rast)

vectlist = []
for vect in gscript.list_strings(type='vect'):
    vectlist.append(vect)

vectlist = [vect.replace('@recreation', '') for vect in vectlist]
print vectlist

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


# test = "test"
LC = "mask"


LC_vect= 'LANDUSE' #'Cas_LULC'

grass.run_command('g.region', flags='a', rast='mask')

listInf = []

############ ########### ########### ########### ########### #####
###this computes the scores  - Facilities to enjoy Recreation Potential Areas
############ ########### ########### ########### ########### #####
computationlist_FE = []
listFacilitiesE = []

for i, val in enumerate(vectlist):
    if val == 'INFR_U_line':  # elem_naturali-punti
        computationlist_FE.append(val)
    if val == 'INFR_U_point':  # elem_naturali-linee
        computationlist_FE.append(val)
    else:
        pass
#
alpha = str(0.01101)
kappa = str(5)
uno = str(1)
import re
import itertools

listfinal = []
#
for vect in computationlist_FE:

    totscores = grass.read_command('v.db.select', map=vect, columns="score_G", separator=',', flags='c')
    ident = totscores.split('\n')
    ident = [i.split(',') for i in ident]

    # list of the scores
    scores = list(itertools.chain(*ident))
    scores = filter(None, scores)  # filter e' piu' veloce di remove    scores.remove('')

    listdata = []
    deleterlist = []
    deletevlist = []
    Deletevfiles = []
    Deleterfiles = []

    dictionary = get_cnt(scores)

    for key in dictionary:
        scoren = str(key)
        scor = str(key)
        suffix = urlify(scoren)
        grass.run_command('g.region', flags='p', rast=LC)

        grass.run_command("v.extract", overwrite=True, input=vect, output=vect + "_" + suffix, where="score_G =" + scor)
        deletevlist.append(vect + "_" + suffix)

        grass.run_command("v.to.rast", overwrite=True, input=vect + "_" + suffix, output="r_" + vect + "_" + suffix,
                          use="cat")
        deleterlist.append("r_" + vect + "_" + suffix)

        grass.run_command("r.grow.distance", input="r_" + vect + "_" + suffix, distance="r_d" + vect + "_" + suffix,
                          metric="euclidean", overwrite=True)
        deleterlist.append("r_d" + vect + "_" + suffix)
        expw = vect + '_w' + suffix + '= ((' + kappa + '+' + uno + ')/(' + kappa + '+ exp(r_d' + vect + "_" + suffix + '*' + alpha + ' ))) *' + scor
        grass.mapcalc(expw, quiet=False, verbose=False, overwrite=True)
        deleterlist.append(vect + '_w' + suffix)

        listFacilitiesE.append(vect + '_w' + suffix)
print listFacilitiesE

# #polygons
# computationlist_FE2 = []
# for i, val in enumerate(vectlist):
#
#     if val == 'NAT_poly':  # Elementi naturali aree  NO AREE PROTETTE
#         computationlist_FE2.append(val)
#     else:
#         pass
#
# for vect in computationlist_FE2:
#     print
#     vect
#     grass.run_command('g.region', flags='p', rast=LC)
#     grass.run_command("v.to.rast", overwrite=True, input=vect, output="raster_" + vect, use='attr',
#                       attrcolumn="score_G")
#     #
#     setnull_0("raster_" + vect, "raster_0_" + vect)
#     listFacilitiesE.append("raster_0_" + vect)

##
myString = " + ".join(listFacilitiesE)
Deletefiles = ",".join(listFacilitiesE)
print listFacilitiesE
expFE = 'FEw = (' + myString + ')'

grass.mapcalc(expFE, quiet=False, verbose=False, overwrite=True)

grass.run_command('g.remove', flags='f', type='raster', name=Deletefiles, quiet=True)
normalize('FEw', 'FEwn')
listInf.append('FEwn')

########### ########### ########### ########### ########### #####
##this computes the scores  - Facilities to reach Recreation Potential Areas
########### ########### ########### ########### ########### #####
computationlist_FR = []
listFacilitiesR = []

for i, val in enumerate(vectlist):
    if val == 'INFR_A_point':  # infrastructures_points
        computationlist_FR.append(val)
    if val == 'INFR_A_line':  # infrastructures lines (road network)
        computationlist_FR.append(val)

    else:
        pass
#
alpha = str(0.01101)
kappa = str(5)
uno = str(1)
import re
import itertools

listfinal = []
#
for vect in computationlist_FR:

    totscores = grass.read_command('v.db.select', map=vect, columns="score_G", separator=',', flags='c')
    ident = totscores.split('\n')
    ident = [i.split(',') for i in ident]

    # list of the scores
    scores = list(itertools.chain(*ident))
    scores = filter(None, scores)  # filter e' piu' veloce di remove    scores.remove('')

    listdata = []
    deleterlist = []
    deletevlist = []
    Deletevfiles = []
    Deleterfiles = []

    dictionary = get_cnt(scores)

    for key in dictionary:
        scoren = str(key)
        scor = str(key)
        suffix = urlify(scoren)
        grass.run_command('g.region', flags='p', rast=LC)

        grass.run_command("v.extract", overwrite=True, input=vect, output=vect + "_" + suffix, where="score_G =" + scor)
        deletevlist.append(vect + "_" + suffix)

        grass.run_command("v.to.rast", overwrite=True, input=vect + "_" + suffix, output="r_" + vect + "_" + suffix,
                          use="cat")
        deleterlist.append("r_" + vect + "_" + suffix)

        grass.run_command("r.grow.distance", input="r_" + vect + "_" + suffix, distance="r_d" + vect + "_" + suffix,
                          metric="euclidean", overwrite=True)
        deleterlist.append("r_d" + vect + "_" + suffix)
        expw = vect + '_w' + suffix + '= ((' + kappa + '+' + uno + ')/(' + kappa + '+ exp(r_d' + vect + "_" + suffix + '*' + alpha + ' ))) *' + scor
        grass.mapcalc(expw, quiet=False, verbose=False, overwrite=True)
        deleterlist.append(vect + '_w' + suffix)

        listFacilitiesR.append(vect + '_w' + suffix)
print listFacilitiesR

#polygons
computationlist_FE2 = []
for i, val in enumerate(vectlist):

    if val == 'NAT_poly':  # Elementi naturali aree  NO AREE PROTETTE
        computationlist_FE2.append(val)
    else:
        pass

for vect in computationlist_FE2:
    print
    vect
    grass.run_command('g.region', flags='p', rast=LC)
    grass.run_command("v.to.rast", overwrite=True, input=vect, output="raster_" + vect, use='attr',
                      attrcolumn="score_G")
    #
    setnull_0("raster_" + vect, "raster_0_" + vect)
    listFacilitiesR.append("raster_0_" + vect)

#
myString = " + ".join(listFacilitiesR)
Deletefiles = ",".join(listFacilitiesR)
print listFacilitiesR
expFR = 'FRw = (' + myString + ')'

grass.mapcalc(expFR, quiet=False, verbose=False, overwrite=True)

grass.run_command('g.remove', flags='f', type='raster', name=Deletefiles, quiet=True)
normalize('FRw', 'FRwn')
listInf.append('FRwn')

# #
myString = " + ".join(listInf)
print myString
myString
exp = 'F = (' + myString + ') * mask' #* Cas_NPArw_m'   # * by the NPA added value (Cas_NPAr * 1.2) increase 20%
grass.mapcalc(exp, quiet=False, verbose=False, overwrite=True)
normalize('F', 'Fn')

grass.run_command("r.recode", input='Fn', output="Fnr", rules='/DATA2/work_2016_2017/Projects/EnRoute/Pillar1/Pillar1_2/Trento_Padova/Recreation/recode_proximity.txt', overwrite=True)


grass.run_command("r.recode", input='RP_sc1_05', output="RP_sc1_05r", rules='/DATA2/work_2016_2017/Projects/EnRoute/Pillar1/Pillar1_2/Trento_Padova/Recreation/recode_RP2.txt', overwrite=True)
inlist =["RP_sc1_05r",'Fnr']
grass.run_command('r.cross', input=inlist, output='ROS2', overwrite = True)

# Deletefiles = ",".join(listInf)
# grass.run_command('g.remove', flags='f', type='raster', name=Deletefiles, quiet=True)



#
# Deleterfiles = ",".join(deleterlist)
# grass.run_command('g.remove', flags='f', type='raster', name=Deleterfiles, quiet=True)
#
# Deletevfiles = ",".join(deletevlist)
# grass.run_command('g.remove', flags='f', type='vector', name=Deletevfiles, quiet=True)