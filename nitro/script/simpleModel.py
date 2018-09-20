#
# simpleModel
#
# Designed to create a 3D structural Model given:
#    a) The PIR formated alignment between the query sequence and the template structure
#
# USAGE WARNING!: The name of the structures specifyed in the alignment should be THE SAME
#                    as the name of the PDB files; otherwise it won't work
#
#Jbonet @ Oliva's Lab '09
#

##
##Supporting Functions
##
import os                           #Import Module
import sys                          #Import Module
import re                           #Import Module

def fileExist (file):               #Checks if a file exists AND is a file
    
    return os.path.exists(file) and os.path.isfile(file)

def getKnownStr (file, seq):        #From the alignment takes the ID of the templates
    
    if not fileExist(file=file):    #Checking for the alignment file
        print "%s can't be found or does not exist" %(file)
        sys.exit()
    
    outString = []
    regex = re.compile("^>\w+\;(\S+)")  #Creating a regular expression to catch the name
    file_fd = open(file,'r')            #Opening the alignment file
    for line in file_fd:
        m = regex.match(line)           #Searching for the RegEx
        if m:
            if m.group(1) != seq:
                outString.append(m.group(1))    #Keeping the match
                pdbName = m.group(1) + '.pdb'
                if not fileExist(file=pdbName): #We check that the PDB exists
                    print "%s can't be found or does not exist" %(pdbName)
                    sys.exit()
                
    if (len(outString) == 1):           #Return for 1 single template
        return outString[0]
    else:
        return tuple(outString)                               #Return for multiple template

##
##Parsing Input Options
##
from optparse import OptionParser   # Import Module
parser = OptionParser()             # Declare Options Parser Object
    #Getting the alignment sequence
parser.add_option("--alignment", dest="ali", action="store",
                     help="PIR formated alignment to guide the model construction", metavar="PIR_FILE")
    #Getting the name of the query protein
parser.add_option("--sequence", dest="seqName", action="store",
                     help="Name of the Query Sequence that is going to be modelled", metavar="SEQ_NAME")
    #Getting the number of models to be done
parser.add_option("--models", dest="numMod", action="store", default=5, type="int",
                     help="Number of models to be done (min: 1) [Default: 5]", metavar="MOD_NUM")
    #Optimization
parser.add_option("--optimize", dest="optimize", action="store_true", default=False,
                     help="Activate optimization")
    #STDOUT and STDERR redirection
parser.add_option("--output", dest="out", action="store", default='seqNAME',
                     help="Prefix for the log and error file defaul:[sequenceNAME]",
                     metavar="OUT_PREFIX")

(options, args) = parser.parse_args()   # Input Options stored in options object

    #We get the name of the template structures
knownStr = getKnownStr(file=options.ali, seq=options.seqName)

    #If not said otherwise we set the output as the name of the query sequence
if options.out is 'seqNAME':
    options.out = options.seqName

    #We redirect STDOUT and STDERR to output files
sys.stdout = open(options.out + '.log', 'w')
sys.stderr = open(options.out + '.err', 'w')

##
##MODELLER Commands
##
from modeller import *              # Import Module
from modeller.automodel import *    # Import Module

log.verbose()                       # Commands MODELLER to display all log output
env = environ()                     # Initializes the 'environment' for this modeling run

env.io.hetatm = True

a = automodel(env,                                          # Loading the environment
              alnfile=options.ali,                          # Assigning the PIR alignment to the model
              knowns=knownStr,                              # Listing the known structures
              sequence=options.seqName,                     # Identify the Query Sequence
              assess_methods=(assess.DOPE, assess.GA341))   # Energy evaluation methods

a.starting_model = 1                    # Setting Starting and Ending Model number
a.ending_model = options.numMod

if options.optimize:
    # Very thorough VTFM optimization:
    a.library_schedule = autosched.slow
    a.max_var_iterations = 300

    # Thorough MD optimization:
    a.md_level = refine.slow

    # Repeat the whole cycle 2 times and do not stop unless obj.func. > 1E6
    a.repeat_optimization = 2
    a.max_molpdf = 1e6

a.make()                                # Create the Model

a.final_malign3d = True
##
##Python: Restore standard values
##

sys.stdout = sys.__stdout__  # restore stdout back to normal
sys.stderr = sys.__stderr__  # restore stdout back to normal

    #We delete the error file if no error has occurred
ERRsize = os.path.getsize(options.out + '.err')
if int(ERRsize) is 0:
    os.remove(options.out + '.err')
