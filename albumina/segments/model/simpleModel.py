'''
Given a PIR alignment and a minimal set of parameters generates models
through homology modeling with MODELLER.
[!] The script does not contain any input check.
[!] The simple_model function redirects STDOUT and STDERR to file logs.
    The redirection is terminated before the function ends.
'''
import sys
import os
import re
import warnings
from argparse import (ArgumentParser,
                      ArgumentDefaultsHelpFormatter)

from modeller import *
from modeller.automodel import *


def set_options(*args, **kargs):
    '''
    Set the specific options for this script
    @return: parsed ArgumentParser
    '''
    parser = ArgumentParser(parents=[basic_parser()],
                            conflict_handler='resolve')

    parser.add_argument("--models", dest="numMod",     action="store",
                        type=int,   metavar="MOD_NUM", default=5,
                        help="Number of models to be done (min: 1) "
                             "[Default: 5]")

    parser.add_argument("--optimize",  dest="optimize", action="store_true",
                        default=False, help="Activate optimization")
    return parser.parse_args()


def basic_parser(*args, **kargs):
    '''
    Include those options that most likely are going to be shared
    by all (or most of) the modpy scripts.
    Advantages:
        1) Write less
        2) Homogenization of parameters
    @return: argparse.ArgumentParser object
    '''
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--pir', dest='alignment', type=str, action='store',
                        help="PIR formated alignment", metavar="PIR_FILE")
    parser.add_argument("--out", dest="out", type=str, action="store",
                        default=None, metavar="OUT_PREFIX",
                        help="Prefix for the log and error file")
    parser.add_argument("-v", dest="verbose", action="store_true",
                        default=False, help="Verbose Mode")
    return parser


def identify_pir(filename):
    '''
    Identify known structures and query sequence in the PIR alignment.
    @return: {'str': [str(), ...], 'seq': str()}
    '''
    _idr = re.compile('^>\w+\;(\S+)')
    data = {'str': [], 'seq': None}

    with open(filename) as fd:
        nextline = False
        mcontent = None
        for line in fd:
            m = _idr.match(line)
            if m:
                nextline = True
                mcontent = m.group(1).strip()
                continue
            if nextline and line.startswith('structureX'):
                    data['str'].append(mcontent)
                    nextline, mcontent = False, None
            elif nextline and line.startswith('sequence'):
                    data['seq'] = mcontent
                    nextline, mcontent = False, None
    return data


def simple_model(alignment, instances,
                 output=None, optimize=False, verbose=False):

    contents = identify_pir(alignment)

    # We redirect STDOUT and STDERR to output files
    if output is None:
        output = contents['seq']
    warnings.warn('STDOUT & STDERR will be redirected to log files.')
    sys.stdout = open(output + '.log', 'w')
    sys.stderr = open(output + '.err', 'w')

    if verbose:
        log.verbose()  # Commands MODELLER to display all log output

    env = environ()  # Initializes the 'environment' for this modeling run

    env.io.hetatm = True  # Allow the presence of hetatoms

    a = automodel(env,  # Loading the environment
                  alnfile=alignment,         # Assigning the PIR alignment
                  knowns=contents['str'],    # Listing the known structures
                  sequence=contents['seq'],  # Identify the Query Sequence
                  assess_methods=(assess.DOPE,
                                  assess.GA341,
                                  assess.DOPEHR))  # Energy evaluation methods

    # Setting Starting and Ending Model number
    a.starting_model, a.ending_model = 1, instances

    if optimize:
        # Very thorough VTFM optimization:
        a.library_schedule   = autosched.slow
        a.max_var_iterations = 300

        # Thorough MD optimization:
        a.md_level = refine.slow

        # Repeat the whole cycle 2 times and do not stop unless obj.func. > 1E6
        a.repeat_optimization = 2
        a.max_molpdf          = 1e6

    a.initial_malign3d = True

    a.make()  # Create the Model

    sys.stdout = sys.__stdout__  # restore stdout back to normal
    sys.stderr = sys.__stderr__  # restore stdout back to normal
    warnings.warn('STDOUT & STDERR have been restored.')

    # We delete the error file if no error has occurred
    ERRsize = os.path.getsize(output + '.err')
    if int(ERRsize) is 0:
        os.remove(output + '.err')


if __name__ == '__main__':
    options = set_options()
    simple_model(options.alignment, options.numMod, options.out,
                 options.optimize, options.verbose)
