from SBI.structure import PDB
import SBI.core as SBIc
import sys

SBIc.set_option('data', 'strict', False)
ids = [x.strip() for x in open('PDB.match').readlines()]

for name in ids:
    sys.stdout.write('>{}\n'.format(name))
    sys.stdout.write((PDB('fetch:{}'.format(name),
                          clean=True).chains[0]
                                     .protein_sequence) + '\n')
    sys.stdout.flush()
