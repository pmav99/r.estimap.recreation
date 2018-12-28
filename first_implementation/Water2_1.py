#!/usr/bin/env python
#compute the water component

import os
import sys
import subprocess
import datetime, time
now = datetime.datetime.now()
StartTime = time.clock()
########### ########### ########### ########### ########### ########### ########### ########### ########### 
########### ########### ########### ########### ########### ########### ########### ########### ########### 
# path to the GRASS GIS launch script
# Linux
grass7bin_lin = 'grass70'
# DATA
# define GRASS DATABASE # add your path to grassdata (GRASS GIS database) directory "~
#("//DATA4/"), "grassdata")
#gisdb = os.path.join(os.path.expanduser("//grassdata/"), "grass") 
gisdb = os.path.join(os.path.expanduser("//DATA4/"), "grassdata") 
# specify (existing) location and mapset
location = "EU_NPA"
mapset   = "recreation"

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
    print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
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


#looking(script, '*command*')
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
rasterL=[]
for rast in gscript.list_strings(type = 'rast'):
    rasterL.append(rast)
rasterL = [rast.replace('@recreation','') for rast in rasterL]
print rasterL

vectlist=[]
for vect in gscript.list_strings(type = 'vect'):
    vectlist.append(vect)

vectlist = [vect.replace('@recreation','') for vect in vectlist]
################################################################################
############################# functions  ###################################
################################################################################
import re
import itertools
import sqlite3
import csv, codecs, cStringIO
#this function nomalizes a file and delete the input####
def normalize (inras,outras):
    min =  grass.raster_info(inras)['min']
    max =  grass.raster_info(inras)['max']
    grass.mapcalc("$outras = float(($inras -$valuem) / ($valueM-$valuem))", inras = inras, outras = outras, valuem = min,valueM = max, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

#this function setnull to 0
def setnull_0(inras,outras):

    zero = 0
    grass.mapcalc("$outras = float(if(isnull($inras),$zeroV,$inras))", inras = inras, outras = outras, zeroV = zero, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def setnull_1(inras,outras):
    uno = 1
    grass.mapcalc("$outras = float(if(isnull($inras),$unoV,$inras))", inras = inras, outras = outras, unoV = uno, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

#this function compute the f(d) on the euclidean distance
def f_d_euclidean (inras,outras,alpha,kappa,score):
    uno = 1
    grass.mapcalc("$outras = float(($alpha + $unoV) / ($alpha + exp($inras * $kappa)) * $score)", inras = inras, outras = outras, unoV = uno, kappa = kappa, alpha = alpha, score =score, overwrite=True)        
#    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def mask(inras,outras,mask):
    grass.mapcalc("$outras = float($inras * $mask)", inras = inras, outras = outras, mask = mask, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def get_cnt(lVals):
    d = dict(zip(lVals, [0]*len(lVals)))
    for x in lVals:
        d[x] += 1
    return d 

def urlify(s):

     s = re.sub(r"[^\w\s]", '', s)  # Remove all non-word characters (everything except numbers and letters)
     s = re.sub(r"\s+", '-', s) # Replace all runs of whitespace with a single dash
     return s
grass.run_command('g.gisenv', set="DEBUG=1")



################################################################################
############################# steps - water ####################################
################################################################################

listfinalWater =[]
deleterlist=[]
deletevlist=[]

grass.run_command('g.region', flags='p', rast='SLSRA_2000')
#grass.run_command('g.region', flags='p', rast='mask')
#LandUseVT_2010_1  

#########################################
###compute value of proximity to lakes###
#########################################

grass.run_command('g.region', flags='p', rast=mask)

#grass.run_command("v.to.rast", input = 'C_lak_EUL', output = 'r_lakes', use = "cat",overwrite = True) 

deleterlist.append('r_lakes')
grass.run_command("r.grow.distance", input= 'r_lakes', distance = 'r_d_lakes', metric = "euclidean", overwrite = True)
f_d_euclidean ('r_d_lakes','Lake_Dtest4','30','0.008','1') #1 km function

setnull_0 ('Lake_Dtest4','Lake_D')

listfinalWater.append('Lake_D')

#Deleterfiles = ",".join(deleterlist) #create a string from a list
#grass.run_command('g.remove', flags='f', type='raster', name=Deleterfiles, quiet=True)



##################################################################################
############################### geomorphology of coast ###########################
##################################################################################
#
grass.run_command('g.region', flags='p', rast=mask)
grass.run_command("v.to.rast", input = "geomorph_for_recr", output = "r_geom_2010", use = "attr", attribute_column="recr_2010", overwrite = True)
deleterlist.append ("r_geom")
grass.run_command("r.grow.distance", input= "r_geom", distance = "coast_d", metric = "euclidean", overwrite = True)   
#
f_d_euclidean ("coast_d","fd_coastD0",'30','0.008','1')
setnull_0 ("fd_coastD0","fd_coastD")
deleterlist.append ("fd_coastD0")
##
grass.run_command("r.neighbors", input="r_geom_2010", output="r_geomneigh_2010", method="mode", size='11', overwrite = True)
##mask = 'mask1'
GeoC = 'GeoCoast = r_geomneigh_2010 * fd_coastD * mask' 
###
grass.mapcalc(GeoC, quiet=False, verbose=False, overwrite=True)
#deleterlist.append ("r_geomneigh")
deleterlist.append ("fd_coastD")
##
setnull_0 ("GeoCoast","GeoCoast_2010")
#listfinalWater.append("GeoCoast0")



##################################################################################
############################### final inputs Water ###############################
##################################################################################
#sostituire con new maskout
#
#laststring = " + ".join(listfinalWater)
#waterF = 'WFix500_10 = ('+ laststring+') * maskout3'
#
#grass.mapcalc(waterF, quiet=False, verbose=False, overwrite=True)

#Deleterfiles = ",".join(deleterlist) #create a string from a list
#Deletevfiles = ",".join(deletevlist)
#grass.run_command('g.remove', flags='f', type='raster', name=Deleterfiles, quiet=True)
#grass.run_command('g.remove', flags='f', type='vector', name=Deletevfiles, quiet=True)


EndTime = time.clock()
print "Finished in %s minutes" % ((EndTime - StartTime)/60)
print "fine"
