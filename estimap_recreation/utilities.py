#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author Nikos Alexandris |
"""

def merge_two_dictionaries(first, second):
    """Merge two dictionaries in via shallow copy.
    Source: https://stackoverflow.com/a/26853961/1172302"""
    merged_dictionary = first.copy()
    merged_dictionary.update(second)
    return merged_dictionary


def dictionary_to_csv(filename, dictionary):
    """Write a Python dictionary as CSV named 'filename'

    Parameters
    ----------
    filename :
        Name for output file

    dictionary :
        Name of input Python dictionary to write to 'filename'

    Returns
    -------
        This function does not return anything

    Examples
    --------
    """
    f = open(filename, "wb")
    w = csv.writer(f)

    # write a header
    w.writerow(["category", "label", "value"])

    # terminology: from 'base' and 'cover' maps
    for base_key, value in dictionary.items():
        base_category = base_key[0]
        base_label = base_key[1]  # .decode('utf-8')
        if value is None or value == "":
            continue
        w.writerow([base_category, base_label, value])

    f.close()


def nested_dictionary_to_csv(filename, dictionary):
    """Write out a nested Python dictionary as CSV named 'filename'

    Parameters
    ----------
    filename :
        Name for output file

    dictionary :
        Name of the input Python dictionary
    """
    f = open(filename, "wb")
    w = csv.writer(f)

    # write a header
    w.writerow(
        ["base", "base_label", "cover", "cover_label", "area", "count", "percents"]
    )

    # terminology: from 'base' and 'cover' maps
    for base_key, inner_dictionary in dictionary.items():
        base_category = base_key[0]
        base_label = base_key[1]  # .decode('utf-8')

        for cover_category, inner_value in inner_dictionary.items():
            if inner_value is None or inner_value == "":
                continue
            cover_label = inner_value[0]
            area = inner_value[1]
            pixel_count = inner_value[2]
            pixel_percentage = inner_value[3]
            w.writerow(
                [
                    base_category,
                    base_label,
                    cover_category,
                    cover_label,
                    area,
                    pixel_count,
                    pixel_percentage,
                ]
            )

    f.close()


def append_map_to_component(raster, component_name, component_list):
    """Appends raster map to given list of components

    Parameters
    ----------
    raster :
        Input raster map name

    component_name :
        Name of the component to add the raster map to

    component_list :
        List of raster maps to add the input 'raster' map

    Returns
    -------

    Examples
    --------
    ...
    """
    component_list.append(raster)
    msg = "Map {name} included in the '{component}' component"
    msg = msg.format(name=raster, component=component_name)
    grass.verbose(_(msg))


