# -*-
# @project: fabAlzheimer
# @file:    pdbsearch.py
#
# @author: jaume.bonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.cat
#
# @date:   2016-09-13 17:15:41
#
# @last modified by:   jaume.bonet
# @last modified time: 2016-10-16 11:54:26
#
# -*-

import urllib2
import os
import sys
import json
import xmltodict

# Get FAB XML-formated query
workdir   = os.path.dirname(os.path.realpath(__file__))
queryfile = os.path.join(workdir, "pdb_fab_search.xml")
query     = "".join(open(queryfile).readlines())

# Execute FAB query
pdbrest = "http://www.rcsb.org/pdb/rest/"
try:
    req     = urllib2.Request(pdbrest + "search" , data=query)
    f       = urllib2.urlopen(req)
    result  = f.read()
except Exception as e:
    print(e.message)
    sys.exit(-1)

# Analyze FAB results
fab_matches   = {}
light_matches = {}
heavy_matches = {}
if result:
    print "Found number of PDB entries:", result.count('\n')
    fd = open('fab_search.txt', 'w')
    for hit in result.split("\n"):
        if hit.strip() != '':
            req  = urllib2.Request(pdbrest + "describeMol?structureId=" + hit)
            f    = urllib2.urlopen(req)
            info = xmltodict.parse(f.read(), process_namespaces=True)
            fab_matches.setdefault(hit, {})
            fab_matches[hit].setdefault('full', {})
            fab_matches[hit]['full'] = info['molDescription']['structureId']
            fd.write(json.dumps(fab_matches[hit]['full'], indent=2))
            if not isinstance(fab_matches[hit]['full']['polymer'], list): continue
            for chain in fab_matches[hit]['full']['polymer']:
                if chain['@type'].lower() != 'protein': continue
                if 'LIGHT' in chain['polymerDescription']['@description']:
                    fab_matches[hit]['light'] = chain['chain'][0]['@id'] if isinstance(chain['chain'], list) else chain['chain']['@id']
                    light_matches.setdefault('{0}.{1}'.format(hit, fab_matches[hit]['light']), [])
                if 'HEAVY' in chain['polymerDescription']['@description']:
                    fab_matches[hit]['heavy'] = chain['chain'][0]['@id'] if isinstance(chain['chain'], list) else chain['chain']['@id']
                    heavy_matches.setdefault('{0}.{1}'.format(hit, fab_matches[hit]['heavy']), [])
            if 'light' not in fab_matches[hit]: del(fab_matches[hit])
    fd.close()
    if len(light_matches) > 0:
        if not os.path.isdir('light_homologs'): os.mkdir('light_homologs')
        for light in light_matches:
            req = urllib2.Request(pdbrest + "sequenceCluster?cluster=70&structureId=" + light)
            f    = urllib2.urlopen(req)
            info = xmltodict.parse(f.read(), process_namespaces=True)
            fd = open(os.path.join('light_homologs', '{0}.txt'.format(light)), 'w')
            fd.write(json.dumps(info, indent=2))
            fd.close()
            light_matches[light] = [str(x['@name']) for x in info['sequenceCluster']['pdbChain']]
            light_matches[light] = list(set(light_matches[light]).intersection(set(light_matches.keys())).difference(set([light])))
        fd = open('light_homologs.txt', 'w')
        fd.write(json.dumps(light_matches, indent=2))
        fd.close()
    if len(heavy_matches) > 0:
        if not os.path.isdir('heavy_homologs'): os.mkdir('heavy_homologs')
        for heavy in heavy_matches:
            req = urllib2.Request(pdbrest + "sequenceCluster?cluster=70&structureId=" + heavy)
            f    = urllib2.urlopen(req)
            info = xmltodict.parse(f.read(), process_namespaces=True)
            fd = open(os.path.join('heavy_homologs', '{0}.txt'.format(heavy)), 'w')
            fd.write(json.dumps(info, indent=2))
            fd.close()
            heavy_matches[heavy] = [str(x['@name']) for x in info['sequenceCluster']['pdbChain']]
            heavy_matches[heavy] = list(set(heavy_matches[heavy]).intersection(set(heavy_matches.keys())).difference(set([heavy])))
        fd = open('heavy_homologs.txt', 'w')
        fd.write(json.dumps(heavy_matches, indent=2))
        fd.close()

else:
    print "Failed to retrieve results"
