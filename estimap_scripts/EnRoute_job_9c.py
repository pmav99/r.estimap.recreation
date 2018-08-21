#!/usr/bin/env python
#this class prepares opportunity spectrum
#inputs features to enjoy and to reach

import os
import sys
import subprocess

class work_on_ros:
    def __init__(self):

        pass

    def ros_component(self, name_city,ms):
        #ms = 'LU'
        newlocation = 'EnRoute_' + ms #sys parameter

        ########### ########### ########### ########### ########### ########### ########### ########### ###########
        # path to the GRASS GIS launch script
        # Linux
        grass7bin_lin = 'grass'
        # DATA
        # define GRASS DATABASE # add your path to grassdata (GRASS GIS database) directory "~
        gisdb = os.path.join(os.path.expanduser("/SERVER_DATA/"), "grassdata")
        # specify (existing) location and mapset
        location = newlocation #"EnRoute"
        mapset = "in_data"

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
        import psycopg2

        # import the working functions
        from functions import *
        import numpy as np
        from numpy import array
        ###########
        # launch session
        gsetup.init(gisbase,
                    gisdb, location, mapset)

        gscript.message('Current GRASS GIS 7 environment:')
        # print gscript.gisenv()

        # gscript.message('Available raster maps:')
        rasterL = []
        for rast in gscript.list_strings(type='rast'):
            rasterL.append(rast)

        vectlist = []
        for vect in gscript.list_strings(type='vect'):
            vectlist.append(vect)

        vectlist = [vect.replace('@'+mapset, '') for vect in vectlist]

        fua = name_city
        allFUA = 'URAU_RG_2011_2014_F'
        # for fua in list_FUAS:
        deleterlist=[]
        print fua

        # # #################################################################
        # # ###prepare  facilities to reach ->roads
        # # #################################################################
        # #
        grass.use_temp_region()
        grass.run_command('g.region', flags='a', res = 50, vector = 'FUA_' + fua)
        mask = 'lakesmask_' + fua
        list_final=[]
        raster_reach=[]
        for rast in gscript.list_strings(type='rast', pattern="r345*"+fua):
            raster_reach.append(rast)
        for rast in gscript.list_strings(type='rast', pattern="r6*"+fua):
            min = grass.raster_info(rast)['min']
            if min > 0:
                raster_reach.append(rast)
            else:
                pass

        for rast in gscript.list_strings(type='rast', pattern="r7*"+fua):
            min = grass.raster_info(rast)['min']
            if min > 0:
                raster_reach.append(rast)
            else:
                pass
        print raster_reach

        if len(raster_reach)>0:
            myString = " + ".join(raster_reach)
            print myString
            ftr = 'ftr00' + fua +'= (' + myString + ')*'+mask
            print ftr
            grass.mapcalc(ftr, quiet=False, verbose=False, overwrite=True)

            roundvalue('ftr00' + fua, 'ftr0' + fua)
            normalize('ftr0' + fua, 'ftr' + fua)
            list_final.append('ftr' + fua)


        # # #################################################################
        # # ###prepare  facilities to enjoy ->osm paths and opportunities
        # # #################################################################


        raster_enjoy=[]

        for rast in gscript.list_strings(type='rast', pattern="osm_lw*"+fua):
            raster_enjoy.append(rast)

        for rast in gscript.list_strings(type='rast', pattern="osm_o08*"+fua):
            raster_enjoy.append(rast)

        for rast in gscript.list_strings(type='rast', pattern="bf_w*"+fua):
            min = grass.raster_info(rast)['min']
            if min > 0:
                raster_enjoy.append(rast)
            else:
                pass
        print raster_enjoy

        if len(raster_enjoy)>0:
            myString = " + ".join(raster_enjoy)
            print myString
            fte = 'fte00' + fua +'= (' + myString + ')*'+mask
            print fte
            grass.mapcalc(fte, quiet=False, verbose=False, overwrite=True)

            roundvalue('fte00' + fua, 'fte0' + fua)
            normalize('fte0' + fua, 'fte' + fua)
            list_final.append('fte' + fua)


        myString = " + ".join(list_final)
        print myString
        exp_final = 'OS00' + fua +'= (' + myString + ')'
        grass.mapcalc(exp_final, quiet=False, verbose=False, overwrite=True)
        setnull_0if('OS00' + fua, 'OS0' + fua, '0.0003')
        normalize('OS0' + fua, 'OS' + fua)
        #

        # paths to rules
        inlist=[]
        recode_path = '/SERVER_DATA/parameters/job9/'


        grass.run_command("r.recode", input='OS' + fua, output='OSr' + fua, rules=recode_path+'recodeOS.txt', overwrite=True)

        grass.run_command("r.recode", input='RPn' + fua, output='RPnr' + fua, rules=recode_path + 'recodeRP.txt', overwrite=True)

        exp04 = 'ROS' + fua + ' = (if(' + 'RPnr' + fua + ' == 1 &  ' + 'OSr' + fua + '  == 1, 1,\
        			if(' + 'RPnr' + fua + ' == 1 &  ' + 'OSr' + fua + '  == 2, 2, \
        			if(' + 'RPnr' + fua + ' == 1 &  ' + 'OSr' + fua + '  == 3, 3, \
        			if(' + 'RPnr' + fua + ' == 2 &  ' + 'OSr' + fua + '  == 1, 4, \
        			if(' + 'RPnr' + fua + ' == 2 &  ' + 'OSr' + fua + '  == 2, 5, \
        			if(' + 'RPnr' + fua + ' == 2 &  ' + 'OSr' + fua + '  == 3, 6, \
        			if(' + 'RPnr' + fua + ' == 3 &  ' + 'OSr' + fua + '  == 1, 7, \
        			if(' + 'RPnr' + fua + ' == 3 &  ' + 'OSr' + fua + '  == 2, 8, \
        			if(' + 'RPnr' + fua + ' == 3 &  ' + 'OSr' + fua + '  == 3, 9))))))))))'
        grass.mapcalc(exp04, quiet=False, verbose=False, overwrite=True)


        #----------------------------------------------------------------------
        # Production of Recreation Opportunity Spectrum ends here
        # ---------------------------------------------------------------------



        # grass.run_command("r.recode", input='ROS' + fua , output='ROS_9' + fua, rules=recode_path + 'ROS9.txt',
        #                   overwrite=True)

        # grass.run_command("r.grow.distance", input='ROS_9' + fua, distance='ROS_9d' + fua,
        #                   metric="euclidean", overwrite=True)


        # f_d_euclidean('ROS_9d' + fua, 'ROS_9w500' + fua, '5', '0.01101', '0.8')  # 500 m function


        # Deleterfiles = ",".join(deleterlist)
        # grass.run_command('g.remove', flags='f', type='raster', name=Deleterfiles, quiet=True)



















        # inlist.append('RPnr' + fua)
        # inlist.append('OSr' + fua)
        # print inlist
        # grass.run_command('r.cross', input=inlist, output='ROS0' + fua, overwrite=True)  # , flags= 'z'  # with 'z' flag: it doesn't consider 1 category. with out flags we need a work around to reclassifie the results
        # deleterlist.append('ROS00' + fua)
        #
        # expFR = 'ROS00' + fua+ '= ROS0'+fua+' * 1'
        #
        # grass.mapcalc(expFR, quiet=False, verbose=False, overwrite=True)
        #
        # deleterlist.append('ROS00' + fua)

# #create the reclass file for each possible combination
#         p = grass.pipe_command('r.category', map='ROS0'+fua, separator=';', quiet=True)
#         rowL = []
#         for line in p.stdout:
#             line2 = line.split(';')
#             rowL.append(line2)
#             rowL2 = remove_first_a(rowL)
#         print rowL2
#
#         rowL3=[]
#         for r in rowL2:
#              primo =r[0]
#              secondo =r[1]
#              terzo =r[2]
#
#              if (secondo == 'no data') or (terzo[-2] =='a'):
#                  print secondo
#                  print terzo
#              else:
#
#                  rowL3.append(int(primo))
#                  rowL3.append(int(secondo[-1]))
#                  rowL3.append(int(terzo[-2]))
#
#              i = 0
#              new_list = []
#              while i < len(rowL3):
#                  new_list.append(rowL3[i:i + 3])
#                  i += 3
#              score_array = np.array(new_list)
#              punteggi = []
#
#              for x in score_array:
#                  recode = str(x[0]) + ':' + str(x[0]) + ':'
#
#                  if (x[1] == 1) and (x[2] == 1):
#                      punteggi.append(recode + '1')
#                  elif (x[1] == 1) and (x[2] == 2):
#                      punteggi.append(recode + '2')
#                  elif (x[1] == 1) and (x[2] == 3):
#                      punteggi.append(recode + '3')
#                  elif (x[1] == 2) and (x[2] == 1):
#                      punteggi.append(recode + '4')
#                  elif (x[1] == 2) and (x[2] == 2):
#                      punteggi.append(recode + '5')
#                  elif (x[1] == 2) and (x[2] == 3):
#                      punteggi.append(recode + '6')
#                  elif (x[1] == 3) and (x[2] == 1):
#                      punteggi.append(recode + '7')
#                  elif (x[1] == 3) and (x[2] == 2):
#                      punteggi.append(recode + '8')
#                  elif (x[1] == 3) and (x[2] == 3):
#                      punteggi.append(recode + '9')
#
#              if len(punteggi) == 0:
#
#                  pass
#              else:
#
#                  with open(recode_path + "recodeROS" + fua + ".txt", 'w') as fo:
#                      for row in punteggi:
#
#                          fo.write(str(row) + '\n')
#                  fo.close()

        # grass.run_command("r.recode", input='ROS00' + fua, output='ROS' + fua,rules=recode_path + "recodeROS" + fua + ".txt", overwrite=True)
