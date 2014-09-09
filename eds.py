# -*- coding: utf-8 -*-
'''
Created on 10.03.2010
Mod 5.06.2011
@author Leszek Tarkowski
or only EDSavg.py - this way it will process all csv files in directory

uses uncertainty library to keep track of errors
'''
from uncertainties import ufloat
from uncertainties.umath import sqrt

def main():
    pass

def umean(list):
    """mean value of a list of 'numbers'"""
    if len(list) == 0:
        return float('nan')
    return sum(list)/len(list)

def ustd(list):
    """standard deviation"""
    if len(list) < 1:
        return float('nan')
    mean = umean(list)
    n = len(list)
    std = sqrt(sum([(x - mean)**2 for x in list])/( n*(n-1) ))
    return std*t_n(len(list))

def loadEDSdata(csvfile):
    """process csv file from EDS-Philips system
    creates dictionary of elements containing wt at and vol fractions"""
    elements = {}
    try:
        #fname = csvfile.toUtf8()
        #print type(fname)
        #print csvfile
        csv = open(csvfile, 'rU')
    except KeyError:
         print "error opening file {0}".format(csvfile)
    lines = csv.readlines()
    for line in lines[13:]:
        print line
        tmp = line.split(",")
        if len(tmp) == 7:
            ct = {}
            # position 1 - wt percent, 2 - atomic percent
            _wt = float(tmp[1].strip())
            _at = float(tmp[2].strip())
            ct["wt"] = ufloat((_wt,EDSerror(_wt)*_wt))
            ct["at"] = ufloat((_at,EDSerror(_wt)*_at))
            ct["vol"] = ufloat((0.0, 0.0)) # to be calculated later...
            # element content
            elements[tmp[0][:-1].strip()] = ct
    #return elements
    return recalcFromWt(elements)

def calcAl2O3(elements):
    # calculate Al2O3 wt content from Al content by
    # simply (26.982*2 + 15.999 *3)/(26.982*2)
    al2o3 = elements['Al']["wt"] * 1.8894262841894596
    # also simple 47.997 / 101.961
    # to get O content in Al2O3
    o2inal2o3 = al2o3 * 0.4707388118986671
    # usually oxygen content is false - we assume that correct
    # value is a stechiometric one - so we correct total mass
    total_mass = 100 - elements['O']["wt"] + o2inal2o3
    elements.pop('Al')
    elements.pop('O')
    tmp = {}
    tmp["wt"] = al2o3
    tmp["at"] = ufloat((0.0,0.0))
    elements["Al2O3"] = tmp
    for key in elements.keys():
        elements[key]["wt"] = elements[key]["wt"] / total_mass * 100
    return recalcFromWt(elements)

def calcZrO2(elements):
    # calculate Al2O3 wt content from Al content by
    # simply (91.224 + 15.999*2)/91.224
    zro2 = elements['Zr']["wt"] * 1.3507629571165483
    # also simple (15.999*2)/123.22200000000001
    # to get O content in ZrO2
    o2inZro2 = zro2 * 0.2596776549642109
    # usually oxygen content is false - we assume that correct
    # value is a stechiometric one - so we correct total mass
    total_mass = 100 - elements['O']["wt"] + o2inZro2
    elements.pop('Zr')
    elements.pop('O')
    tmp = {}
    tmp["wt"] = zro2
    tmp["at"] = ufloat((0.0,0.0))
    elements["ZrO2"] = tmp
    for key in elements.keys():
        elements[key]["wt"] = elements[key]["wt"] / total_mass * 100
    return recalcFromWt(elements)

def recalcFromWt(elements):
    #definitions
    density = { 'Ni': 8.908, 'W': 19.25, 'Al': 2.70,
                'Al2O3' :  4.05, 'O' : 0.000001, 'Mo' : 10.28,
                'Fe' : 7.874, 'Zr' : 6.52, 'ZrO2' : 5.68 }
    molMass = { 'Ni': 58.693, 'W': 183.84, 'Al': 26.982,
                'O': 15.999, 'Al2O3' :  101.961, 'Mo' : 95.96,
                'Fe' : 55.845, 'Zr' : 91.224, 'ZrO2' : 123.222 }
    mtotal = 0
    #calc of atomic percentage
    for key in elements.keys():
        elements[key]["at"] = elements[key]["wt"] / molMass[key]
        mtotal += elements[key]["at"]
    for key in elements.keys():
        elements[key]["at"] = 100*elements[key]["at"]/mtotal
    #calc of volume concentration
    vtotal = 0
    for key in elements.keys():
        elements[key]["vol"] = elements[key]["wt"] / density[key]
        vtotal += elements[key]["vol"]
    for key in elements.keys():
        elements[key]["vol"] = 100 * elements[key]["vol"] / vtotal
    return elements

def calcStatistics(samples):
    elements = {}
    stats = {}
    stats["wt"] = 0
    stats["vol"] = 0
    stats["at"] = 0
    for sample in samples.keys():
        for element in samples[sample].keys():
            if element in elements:
                elements[element]["wt"].append(samples[sample][element]["wt"])
                elements[element]["at"].append(samples[sample][element]["at"])
                elements[element]["vol"].append(samples[sample][element]["vol"])
            else:
                elements[element] = {}
                elements[element]["wt"] = [samples[sample][element]["wt"]]
                elements[element]["at"] = [samples[sample][element]["at"]]
                elements[element]["vol"] = [samples[sample][element]["vol"]]
    for el in elements.keys():
        stats[el] = {"wt":{}, "at":{}, "vol":{}}
        stats[el]["wt"]["mean"] = umean(elements[el]["wt"])
        stats[el]["wt"]["std"] = ustd(elements[el]["wt"])
        stats[el]["at"]["mean"] = umean(elements[el]["at"])
        stats[el]["at"]["std"] = ustd(elements[el]["at"])
        stats[el]["vol"]["mean"] = umean(elements[el]["vol"])
        stats[el]["vol"]["std"] = ustd(elements[el]["vol"])
    return stats

def t_n(n):
    table_t_n = [ 0, 0,  1.8367, 1.3210, 1.1966, 1.1414, 1.1103, 1.0903, 1.0765, 1.0663, 1.0585,
           1.0524, 1.0474, 1.0432, 1.0398, 1.0368, 1.0343, 1.0320, 1.0301, 1.0284, 1.0268]
    if n <= 20: return table_t_n[n]
    else: return 1.0


def EDSerror(wt):
    err = 0.02
    if wt < 20:
        err = 0.04
    elif wt < 5:
        err = 0.10
    elif wt < 1:
        err = 0.50
    elif wt < 0.2:
        err = wt
    return err

if __name__ == "__main__":
    main()