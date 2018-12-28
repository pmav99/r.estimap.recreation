#!/usr/bin/env python
#Created on Wed Aug 12 08:34:28 2015

#@author: Gra
#Recreation potential for LUISA EU SCENARIONS



import os
import sys
import subprocess
import datetime, time
now = datetime.datetime.now()
StartTime = time.clock()

#looking(script, '*command*')
# import GRASS Python bindings (see also pygrass)
import grass.script as gscript
import grass.script.setup as gsetup
import grass.script as grass
 
gscript.message('Current GRASS GIS environment:')
 
gscript.message('Available raster maps:')
rasterL=[]
for rast in gscript.list_strings(type = 'rast'):
    rasterL.append(rast)
rasterL = [rast.replace('@recreation','') for rast in rasterL]    


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

def normalize (inras,outras):
    """
    This function nomalizes a file and delete the input####
    """
    min =  grass.raster_info(inras)['min']
    max =  grass.raster_info(inras)['max']
    grass.mapcalc("$outras = float(($inras -$valuem) / ($valueM-$valuem))", inras = inras, outras = outras, valuem = min,valueM = max, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def setnull_0(inras,outras):
    """
    Set NULL to 0
    """
    zero = 0
    grass.mapcalc("$outras = float(if(isnull($inras),$zeroV,$inras))", inras = inras, outras = outras, zeroV = zero, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def setnull_1(inras,outras):
    """
    Set NULL to 1
    """
    uno = 1
    grass.mapcalc("$outras = float(if(isnull($inras),$unoV,$inras))", inras = inras, outras = outras, unoV = uno, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def f_d_euclidean (inras,outras,alpha,kappa,score):
    """
    Compute the f(d) on the euclidean distance
    """
    uno = 1
    grass.mapcalc("$outras = float(($alpha + $unoV) / ($alpha + exp($inras * $kappa)) * $score)", inras = inras, outras = outras, unoV = uno, kappa = kappa, alpha = alpha, score =score, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def masklak(inras,outras,mask):
    """
    """    
    grass.mapcalc("$outras = float($inras * $mask)", inras = inras, outras = outras, mask = mask, overwrite=True)        
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def get_cnt(lVals):
    """
    """
    d = dict(zip(lVals, [0]*len(lVals)))
    for x in lVals:
        d[x] += 1
    return d 

def urlify(s):
    """
    """
    s = re.sub(r"[^\w\s]", '', s)  # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"\s+", '-', s) # Replace all runs of whitespace with a single dash
    return s
     
def maskout(maskout,inras,outras):
    """
    """
    zero = 0
    grass.mapcalc("$outras = if($maskout == $zeroV, $zeroV, $inras)", inras = inras, outras = outras, zeroV = zero, maskout = maskout, overwrite=True)        


################################################################################
############################# inputs    ########################################
################################################################################
mask = "mask" #'lakes3' #"


#mask = 'testmask'
listfinalNATURE =[]
deleterlist=[]
deletevlist=[]


#for land use 

computationlist=['clc2012']
#for i, r in enumerate(rasterL):
#    if r[:4]=='CLC_':
#        computationlist.append( r)
#    else:
#        pass
#print computationlist

grass.run_command('g.region', flags='p', rast=mask)
################################################################################
############################# LAND USE #########################################
################################################################################
SLSRA_rules = "/natcapes_nfs/grassdb/INCA_R/scores/recodeCLC.txt"#reclass rules for corine land cover
#
#
# urbanL = []
# industryL=[]
# SLSRAL=[]
# finalRP=[]
# Deleterfiles=[]
# Deletevfiles=[]
#
for r in computationlist:
    year = r[-4:]
    SLSRA = 'SLSRA_'+year

#recode CLC
    grass.run_command("r.recode", input= r, output= SLSRA, rules = SLSRA_rules, overwrite=True)
    setnull_0('SLSRA_'+year, 'SLSRA0_'+year)
    # masklak('SLSRA0_'+year,'SLSRA1_'+year,mask)

################################################################################
#########################  NPA and NATURE ######################################
################################################################################


#for r in computationlist:
##     
#    NatureL =[]
#    year = r[-4:]    
#    print year
    
    #Natural Protected areas

#    masklak('NPA_scored1'+year,'NPA_scored2'+year,mask)
#    normalize ('NPA_scored2'+year,'NPA_scoredN'+year)


###############################################################################
########################  final water ######################################
###############################################################################

#mask RA with recode industry
#
for r in computationlist:
   WaterL =[]
   year = r[-4:]
   print year
#
#    WaterL.append('F_statagperc1') add bathing water here
   WaterL.append('bathing_water_quality_2006_gscores') 
   WaterL.append('fd_coastD')
   WaterL.append('Lake_D')
   WaterL.append('geo_coast')

   laststring = " + ".join(WaterL)
   water = 'Wat'+year+' = ('+ laststring+') * lakes3'

   grass.mapcalc(water, quiet=False, verbose=False, overwrite=True)

   normalize ('Wat'+year,'Wat_N'+year)

################################################################################
############################# final inputs RP ##################################
################################################################################

for r in computationlist:
    finalRP=[]
    year = r[-4:]

    if year == '2012':
        finalRP.append('SLSRA0_'+year) #land use
        finalRP.append('Wat_N'+year)  #Fresh Water
        finalRP.append('wdpa_2012_gscores')   #Natural Protected areas

        laststring = " + ".join(finalRP)
        RP = 'RP00V3'+year+' = ('+ laststring+')'

        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True)

#        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'
#
#        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True)

        normalize ('RP00V3'+year,'RP00NV3'+year)

#    if year == '1990':       
#        finalRP.append('SLSRA0_'+year) #land use
#        finalRP.append('Wat_N'+year)  #Fresh Water
#        finalRP.append('NPA_grassfixN'+year)   #Natural area
#        finalRP.append('GUA_m0'+year)  #Urban
#
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+') * lakes3 * Buff80kmM'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
##        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
##        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True)
# 
#        normalize ('RP00'+year,'RP00N'+year)


#    if year == '2000':
#        
#        finalRP.append('SLSRA0_'+year) #land use
#        finalRP.append('Wat_N'+year)  #Fresh Water
#        finalRP.append('NPA_grassfixN'+year)   #Natural area
#        finalRP.append('GUA_m0'+year)  #Urban
#
#        
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+') * lakes3 * Buff80kmM'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
##        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
##        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True) 
#        normalize ('RP00'+year,'RP00N'+year)
        
#    if year == '2012':
#        
#        finalRP.append('SLSRA0_'+year) #land use
#        finalRP.append('Wat_N'+year)  #Fresh Water
#        finalRP.append('NPA_grassfixN'+year)   #Natural area
#        finalRP.append('GUA_m0'+year)  #Urban
#
#        
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+') * lakes3 * Buff80kmM'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
##        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
##        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True) 
#        normalize ('RP00'+year,'RP00N'+year)        
        
        
        
        
        
        
        
        
        
        
        
#    if year == '20':
#        
#        finalRP.append('SLSRA0_'+year)
#        finalRP.append('Wat_N'+year)
#        finalRP.append('Nat_N'+year)
#        finalRP.append('GUA_m0'+year)
#        finalRP.append('WC3_10')
#        
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+')'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
#        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
#        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True) 
#        normalize ('RPuu2'+year,'RPuu2N'+year)

#    if year == '30':
#        
#        finalRP.append('SLSRA0_'+year)
#        finalRP.append('Wat_N'+year)
#        finalRP.append('Nat_N'+year)
#        finalRP.append('GUA_m0'+year)
#        finalRP.append('WC3_10')
#        
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+')'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
#        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
#        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True) 
#        normalize ('RPuu2'+year,'RPuu2N'+year)
#
#
#    if year == '40':
#
#        
#        finalRP.append('SLSRA0_'+year)
#        finalRP.append('Wat_N'+year)
#        finalRP.append('Nat_N'+year)
#        finalRP.append('GUA_m0'+year)
#        finalRP.append('WC3_10')
#        
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+')'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
#        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
#        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True) 
#        normalize ('RPuu2'+year,'RPuu2N'+year)
#
#    if year == '50':
#        
#                
#        finalRP.append('SLSRA0_'+year) #land use
#        finalRP.append('Wat_N'+year)  #Fresh Water
#        finalRP.append('Nat_N'+year)   #Natural area
#        finalRP.append('GUA_m0'+year)  #Urban
#        
#        
#        laststring = " + ".join(finalRP)
#        RP = 'RP00'+year+' = ('+ laststring+') * lakes3'        
#        grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True) 
#        
#        RP_u = 'RPuu2'+year +' = (RP00'+year+'*'+ 'mask_u' + year +')'    
#
#        grass.mapcalc(RP_u, quiet=False, verbose=False, overwrite=True) 
#        normalize ('RPuu2'+year,'RPuu2N'+year)
#        
#Deleterfiles = ",".join(deleterlist) #create a string from a list
#Deletevfiles = ",".join(deletevlist)
#grass.run_command('g.remove', flags='f', type='raster', name=Deleterfiles, quiet=True)
#grass.run_command('g.remove', flags='f', type='vector', name=Deletevfiles, quiet=True)

#computationlist=[]
#for i, r in enumerate(rasterL):
#    if r[:6]=='RPuu2N':
#        computationlist.append(r)
#    else:
#        pass
#print computationlist
#
#for r in computationlist:
#    print r
#    year = r[-2:]
#
#    grass.run_command("r.recode", input= r, output= r +'_rec2'+year, rules = demand_recode2, overwrite=True)    
#    grass.run_command("r.recode", input= r, output= r +'_rec4'+year, rules = demand_recode4, overwrite=True)  


EndTime = time.clock()
print "Finished in %s minutes" % ((EndTime - StartTime)/60)
print "fine"

