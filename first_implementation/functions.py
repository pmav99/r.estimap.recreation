#!/usr/bin/python\<nl>\
# -*- coding: utf-8 -*-

"""
"""
# this contains useful functions that I use in all scripts

# required

# globals
import os
import grass.script as gscript
import grass.script.setup as gsetup
import grass.script as grass
# from core import *
# from utils import try_remove
from grass.exceptions import CalledModuleError

# helpers
#this function set the region from a vector data
def set_v_region(flags, resolution, reference_vdata, **kwargs):
    grass.run_command('g.region', flags=flags, res=resolution, vector=reference_vdata)
    pass

#this function set the region from a raster data
def set_r_region(flags, resolution, reference_rdata, **kwargs):
    grass.run_command('g.region', flags=flags, res=resolution, raster=reference_rdata)
    pass

#this function runs the recode module from grass
def run_recode(input_raster, output_raster, rules_file, **kwargs):
    gscript.run_command('r.recode', input= input_raster, output= output_raster, rules = rules_file, overwrite=True)
    pass

#this function normalize data
def normalize(inras, outras):
    min = grass.raster_info(inras)['min']
    max = grass.raster_info(inras)['max']
    grass.mapcalc("$outras = float(($inras -$valuem) / ($valueM-$valuem))", inras=inras, outras=outras, valuem=min,
                  valueM=max, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
    pass
# # this function set 0 to null
def setnull_0(inras, outras):
    zero = 0
    grass.mapcalc("$outras = float(if(isnull($inras),$zeroV,$inras))", inras=inras, outras=outras, zeroV=zero,
                  overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
    pass

# # this function setnull to 1
def setnull_1(inras, outras):
    uno = 1
    grass.mapcalc("$outras = float(if(isnull($inras),$unoV,$inras))", inras=inras, outras=outras, unoV=uno,
                  overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
    pass
# # this function compute the f(d) on the euclidean distance
def f_d_euclidean(inras, outras, alpha, kappa, score):
    uno = 1
    grass.mapcalc("$outras = float(($alpha + $unoV) / ($alpha + exp($inras * $kappa)) * $score)", inras=inras,
                  outras=outras, unoV=uno, kappa=kappa, alpha=alpha, score=score, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

# this function clip out with a mask = 1
def mask(inras, outras, mask):
    grass.mapcalc("$outras = float($inras * $mask)", inras=inras, outras=outras, mask=mask, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

# raster integer map to float raster map
def float_1(inras, outras):
    grass.mapcalc("$outras = float($inras)", inras=inras, outras=outras,overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
#rescale a raster map 0:100 ->0:1
def rescale0_1(inras, outras):
    zero = 100
    grass.mapcalc("$outras = float($inras / $zeroV)", inras=inras, outras=outras, zeroV=zero, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def if0_1(inras, outras):
    uno = 1
    grass.mapcalc("$outras = if($inras > $unoV,$unoV,$inras)", inras=inras, outras=outras, unoV=uno, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

# # this function setnull to 1
def setnull_0if(inras, outras, value):
    zero = 0

    grass.mapcalc("$outras = if($inras < $value,$zeroV,$inras)", inras=inras, outras=outras, zeroV=zero, value=value,
                  overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
    pass

def maskout(maskout, inras, outras):
    zero = 0
    grass.mapcalc("$outras = if($maskout == $zeroV, $zeroV, $inras)", inras=inras, outras=outras, zeroV=zero,
                  maskout=maskout, overwrite=True)
# add 1 to a raster map
def add_1(inras, outras):
    valore = 1
    grass.mapcalc("$outras = $inras + $valoreV", inras=inras, outras=outras, valoreV=valore, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def by_1(inras, outras):
    valore = 1
    grass.mapcalc("$outras = $inras * $valoreV", inras=inras, outras=outras, valoreV=valore, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

#this function import feature classes from a file *.gdb
def import_vect_fromgdb(path_to_origin, feature_class, output, flag, **kwargs):
    grass.run_command("v.import", input=path_to_origin, layer=feature_class, output=output, flags=flag)

    pass
#this function compute the f(d) on the euclidean distance
def f_d_euclidean (inras,outras,alpha,kappa,score):
    uno = 1
    grass.mapcalc("$outras = float(($alpha + $unoV) / ($alpha + exp($inras * $kappa)) * $score)", inras = inras, outras = outras, unoV = uno, kappa = kappa, alpha = alpha, score =score, overwrite=True)
#    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def roundvalue(inras, outras):
    zerom = 0.0001
    zero = 0
    grass.mapcalc("$outras = if($inras < $zeromV, $zeroV, $inras)", inras=inras, outras=outras, zeroV=zero, zeromV=zerom, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

def if0_1(inras, outras):
    uno = 1
    grass.mapcalc("$outras = if($inras > $unoV,$unoV,$inras)", inras=inras, outras=outras, unoV=uno, overwrite=True)
    grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)

import re
import itertools
# This function weights lines or points according to a function of the distance
def weightPL(Ilist, outr, field, region, mask):
    deleterwlist = []
    zero = str(0)
    # this can be in the parameters
    alpha = str(0.01101)
    kappa = str(5)
    uno = str(1)

    listfinal = []
    for vect in Ilist:

        totscores = grass.read_command('v.db.select', map=vect, columns=field, separator=',', flags='c')
        ident = totscores.split('\n')
        ident = [i.split(',') for i in ident]
        # list of the scores
        scores = list(itertools.chain(*ident))
        scores = filter(None, scores)  # filter e' piu' veloce di remove    scores.remove('')

        listdata = []
        deleterlist = []

        dictionary = get_cnt(scores)

        for key in dictionary:
            grass.run_command('g.region', flags='p', rast=region)
            scoren = str(key)

            scor = str(key)
            suffix = urlify(scoren)

            grass.run_command("v.extract", overwrite=True, input=vect, output=vect + "_" + suffix,
                              where=field + "=" + scor)

            grass.run_command("v.to.rast", input=vect + "_" + suffix, output="r_" + vect + "_" + suffix, use="cat", overwrite=True)
            deleterlist.append("r_" + vect + "_" + suffix)
            grass.run_command("r.grow.distance", input="r_" + vect + "_" + suffix, distance="r_d" + vect + "_" + suffix,
                              metric="euclidean", overwrite=True)
            deleterlist.append ("r_d"+vect+"_"+suffix)
            expw = vect + '_w' + suffix + '= ((' + kappa + '+' + uno + ')/(' + kappa + '+ exp(r_d' + vect + "_" + suffix + '*' + alpha + ' ))) *' + scor


            grass.mapcalc(expw, quiet=False, verbose=False, overwrite=True)
            deleterlist.append(vect + '_w' + suffix)

            Deleterfiles = ",".join(deleterlist)  # create a string from a list

            listdata.append(vect + '_w' + suffix)

        dic = get_cnt(listdata)
        inputd = ''
        for key in dic:
            expr = inputd + key

        myString = " + ".join(listdata)
        Deletefiles = ",".join(listdata)

        expwt = vect + 'w_t = (' + myString + ')*' + mask

        grass.mapcalc(expwt, quiet=False, verbose=False, overwrite=True)
        listfinal.append(vect + 'w_t')
        print Deletefiles
        grass.run_command('g.remove', flags='f', type='raster', name=Deleterfiles, quiet=True)
        grass.run_command('g.remove', flags='f', type='vector', name=vect + "_" + suffix, quiet=True)

        grass.run_command('g.remove', flags='f', type='raster', name=Deletefiles, quiet=True)

    dic = get_cnt(listfinal)
    inputd = ''

    for key in dic:

        expr = inputd + key

    myString = " + ".join(listfinal)
    deleterwlist = ",".join(listfinal)
    expFIPS_I = outr + ' = (' + myString + ')'

    grass.mapcalc(expFIPS_I, quiet=False, verbose=False, overwrite=True)


    grass.run_command('g.remove', flags='f', type='raster', name=deleterwlist, quiet=True)

###################################################################






def db_table_exist(table, **args):
    """Check if table exists. https://grass.osgeo.org/grass70/manuals/libpython/_modules/script/db.html

    If no driver or database are given, then default settings is used
    (check db_connection()).

    >>> run_command('g.copy', vector='firestations,myfirestations')
    0
    >>> db_table_exist('myfirestations')
    True
    >>> run_command('g.remove', flags='f', type='vector', name='myfirestations')
    0

    :param str table: table name
    :param args:

    :return: True for success, False otherwise
    """
    nuldev = file(os.devnull, 'w+')
    ok = True
    try:
        grass.run_command('db.describe', flags='c', table=table,
                    stdout=nuldev, stderr=nuldev, **args)
    except CalledModuleError:
        ok = False
    finally:
        nuldev.close()

    return ok

#utilities
def get_cnt(lVals):
    d = dict(zip(lVals, [0] * len(lVals)))
    for x in lVals:
        d[x] += 1
    return d
def urlify(s):
    s = re.sub(r"[^\w\s]", '', s)  # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"\s+", '-', s)  # Replace all runs of whitespace with a single dash
    return s

#split string when there is an underscore
def split_at(s, c, n):
    words = s.split(c)
    return c.join(words[:n]), c.join(words[n:])

#remove first entry in a list
def remove_first_a(t):
    return t[1:]



# main

# def main():
#     """
#     """
#     print "Some name is:", SOMENAME
#     printsomething()
#
# # exit
# if __name__ == "__main__":
#     main()
