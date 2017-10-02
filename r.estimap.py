#!/usr/bin/python\<nl>\
# -*- coding: utf-8 -*-

"""
 MODULE:       r.estimap.recreation

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>

               Grazia Zulian <Grazia.Zulian@ec.europa.eu>
               First implementation in Python

 PURPOSE:      An implementation of the Ecosystem Services Mapping Tool
               (ESTIMAP). ESTIMAP is a collection of spatially explicit models
               to support mapping and modelling of ecosystem services
               at European scale.

 COPYRIGHT:    (C) 2017 by the GRASS Development Team

               This program is free software under the GNU General Public
               License (>=v2). Read the file COPYING that comes with GRASS
               for details.
"""


#%Module
#%  description:  Implementation of ESTIMAP to support mapping and modelling of ecosystem services (Zulian, 2014)
#%  keywords: estimap
#%  keywords: ecosystem services
#%  keywords: recreation
#%End

#%option G_OPT_R_INPUT
#% key: bathing
#% key_desc: filename
#% description: Bathing Water Quality Index
#% required : yes
#%end

#%option G_OPT_R_INPUT
#% key: coast
#% key_desc: filename
#% description: Score of access to coast based on a distance function
#% required : yes
#%end

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: filename
#% description: Sore of access to lakes based on a distance function
#% required : yes
#%end

#%option G_OPT_R_INPUT
#% key: geomorphology
#% key_desc: filename
#% description: Score of coastal geomorphology to support recreation activities
#% required : yes
#%end



# This can be optional if an already recoded map is provided

#%option G_OPT_F_INPUT
#% key: slsra
#% key_desc: filename
#% description: Reclassification rules for the CORINE land cover
#% required: yes
#%end

#%option G_OPT_R_OUTPUT
#% key: emissivity_out
#% key_desc: name
#% description: Name for output emissivity map | For re-use as "emissivity=" input in subsequent trials with different spatial window sizes
#% required: no
#%end

# required librairies
import os
import sys
import subprocess
import datetime, time

import atexit
import grass.script as grass
from grass.exceptions import CalledModuleError
from grass.pygrass.modules.shortcuts import general as g

from scoring_schemes import corine

# helper functions
def cleanup():
    """
    Clean up temporary maps
    """
    grass.run_command('g.remove', flags='f', type="rast",
                      pattern='tmp.{pid}*'.format(pid=os.getpid()), quiet=True)

def run(cmd, **kwargs):
    """
    Pass required arguments to grass commands (?)
    """
    grass.run_command(cmd, quiet=True, **kwargs)

def normalize (inras,outras):
    """
    This function nomalizes a file and deletes the input
    """
    minimum =  grass.raster_info(inras)['min']
    maximum =  grass.raster_info(inras)['max']

    grass.mapcalc("$outras = float(($inras -$valuem) / ($valueM - $valuem))", inras = inras, outras = outras, valuem = min,valueM = max, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def main():
    """
    Main program: get names for input, output suffix, options and flags
    """

    # ?

    slsra_rules = options['image'].split(',')


    # 1

    mask = "mask" #'lakes3' #"
    #mask = 'testmask'

    # 2

    listfinalNATURE =[]
    deleterlist=[]
    deletevlist=[]

    # 3

    computationlist=['clc2012']

    # 4 -- DONE --

    # --------------------------------------------------------------------------
    grass.use_temp_region()  # to safely modify the region
    run('g.region', flags='p', rast=mask) # Set region to 'mask'
    g.message("|! Region's resolution matched to mask's ({p})".format(p=mask))
    # --------------------------------------------------------------------------

    # 5 # Suitability of Land to support recreation activities

    SLSRA_rules = "/natcapes_nfs/grassdb/INCA_R/scores/recodeCLC.txt"#reclass rules for corine land cover
    # land_suitability_rules = ""

    # 6

    for raster in computationlist:

        # Fix Me
        year = raster[-4:]

        # ?
        SLSRA = 'SLSRA_'+year

        #recode CLC
        grass.run_command("r.recode", input= r, output= SLSRA, rules = SLSRA_rules, overwrite=True)
        setnull_0('SLSRA_'+year, 'SLSRA0_'+year)
        # masklak('SLSRA0_'+year,'SLSRA1_'+year,mask)

    # 7 # mask RA with recode industry

    for r in computationlist:

        WaterL =[]

        # Fix Me
        year = r[-4:]
        print year

        # WaterL.append('F_statagperc1') add bathing water here
        WaterL.append('bathing_water_quality_2006_gscores') 
        WaterL.append('fd_coastD')
        WaterL.append('Lake_D')
        WaterL.append('geo_coast')

        laststring = " + ".join(WaterL)
        water = 'Wat'+year+' = ('+ laststring+') * lakes3'

        grass.mapcalc(water, quiet=False, verbose=False, overwrite=True)

        normalize ('Wat'+year,'Wat_N'+year)

    # 8 # final inputs for Recreation Potential

    for r in computationlist:

        finalRP=[]

        # Fix Me
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


# Inputs

## Land Use
## Water

### Coast:  Score access to the coast as a distance function
### Coast Geomorphology: Score coastal areas as a function of their geomorphology
### Lakes:  Score access to lakes as a distance function
### Bathin Waters:  Score access to bathing waters as a distance function

## Natural Protected Areas

# Inter
if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())

