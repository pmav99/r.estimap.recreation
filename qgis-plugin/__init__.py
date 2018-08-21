# -*- coding: utf-8 -*-
"""
/***************************************************************************
 estimap
                                 A QGIS plugin
 Implementation of ESTIMAP to support mapping and modelling of ecosystem services (Zulian, 2014)
                             -------------------
        begin                : 2018-07-27
        copyright            : (C) 2018 by Nikos Alexandris
        email                : nik@nikosalexandris.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load estimap class from file estimap.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .estimap import estimap
    return estimap(iface)
