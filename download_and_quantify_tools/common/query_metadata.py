from optparse import OptionParser
import sqlite3
import pkg_resources
from sets import Set
import config
import pkg_resources as pr
import json

#DB_CONN = sqlite3.connect(config.metadatadb_location())

resource_package = __name__
#EXP_TO_ISPAIRED = pr.resource_filename(resource_package, "../metadata/exp_to_ispaired.json") # TODO deprecate
EXP_TO_RUNS_JSON = pr.resource_filename(resource_package, "../metadata/exp_to_runs.json")   # TODO deprecate
#RUN_TO_READTYPES = pr.resource_filename(resource_package, "../metadata/run_to_readtype.json") # TODO deprecate
#EXPERIMENT_TO_READTYPES = pr.resource_filename(resource_package, "../metadata/experiment_to_readtypes.json") # TODO deprecate

EXPERIMENT_TO_LAYOUT_F = pr.resource_filename(resource_package, "../metadata/experiment_to_layout.json")
EXPERIMENT_TO_READ_SPEC_F = pr.resource_filename(resource_package, "../metadata/experiment_to_read_spec.json")
EXPERIMENT_TO_RUNS_F = pr.resource_filename(resource_package, "../metadata/experiment_to_runs.json")

with open(EXPERIMENT_TO_LAYOUT_F, 'r') as f:
    EXPERIMENT_TO_LAYOUT = json.load(f)
with open(EXPERIMENT_TO_READ_SPEC_F, 'r') as f:
    EXPERIMENT_TO_READ_INDEX_TO_SPEC = json.load(f)
with open(EXPERIMENT_TO_RUNS_F, 'r') as f:
    EXPERIMENT_TO_RUNS = json.load(f)


"""
"SRX352279": {
        "0": {
            "read_type": "Forward",
            "read_class": "Application Read",
            "base_coord": 1
        },
        "1": {
            "read_type": "Reverse",
            "read_class": "Application Read",
            "base_coord": 51
        }
    },

"""


#def query_experiment_accessions():
#    sql_cmd = "SELECT experiment_accession FROM experiment JOIN " + \
#        "sample USING (sample_accession) WHERE sample.scientific_name " + \
#        "= 'Homo sapiens' AND experiment.library_strategy = 'RNA-Seq' " + \
#        "AND platform = 'ILLUMINA'"
#    c = DB_CONN.cursor()    
#    returned = c.execute(sql_cmd)
#    exp_accs = [r[0].encode('utf-8') for r in returned]
#    return exp_accs

def get_runs(exp_acc):
    """
    For a given SRA experiment accession, retrieve 
    all SRA run accessions
    """
    if exp_acc not in EXPERIMENT_TO_RUNS:
        return None
    return EXPERIMENT_TO_RUNS[exp_acc]

def get_read_layout(exp_acc):
    """
    Get the read layout for a given RNA-seq experiment
    Args:
        exp_acc: the experiment accession in the SRA
    Returns:
        'PAIRED' if the reads are paired-end
        'SINGLE' if the reads are single-end
    """
    if exp_acc not in EXPERIMENT_TO_LAYOUT:
        return None
    return EXPERIMENT_TO_LAYOUT[exp_acc]


def get_read_classes(exp_acc):
    if exp_acc not in EXPERIMENT_TO_READ_INDEX_TO_SPEC:
        return None
    classes = []
    for read_index in range(len(EXPERIMENT_TO_READ_INDEX_TO_SPEC[exp_acc])):
        read_index_str = str(read_index)
        prop_to_val = EXPERIMENT_TO_READ_INDEX_TO_SPEC[exp_acc][read_index_str]
        classes.append(prop_to_val['read_class'])
    return classes

def get_read_types(exp_acc):
    if exp_acc not in EXPERIMENT_TO_READ_INDEX_TO_SPEC:
        return None
    types = []
    for read_index in range(len(EXPERIMENT_TO_READ_INDEX_TO_SPEC[exp_acc])):
        read_index_str = str(read_index)
        prop_to_val = EXPERIMENT_TO_READ_INDEX_TO_SPEC[exp_acc][read_index_str]
        types.append(prop_to_val['read_type'])
    return types

def experiment_readtypes(exp_acc):
    """
    For a given experiment accession, retrieve a mapping of the read-index
    to the read-type at that index.
    Args:
        exp_acc: experiment_accession
    Returns:
        A dictionary mapping a read-index to read-type
    """
    with open(EXPERIMENT_TO_READTYPES, "r") as f:
        run_to_readspec = json.load(f)
        try:
            index_to_readtype = {}
            read_specs = run_to_readspec[exp_acc]
            for read_spec in read_specs:
                index_to_readtype[read_spec["read_index"]] = read_spec["read_type"]
            return index_to_readtype
        except:
             print "ERROR! Readspec for experiment %s not found in metadata." % exp_acc

# TODO Remove this once the new method is built
def experiment_readtype_ORIGINAL(exp_acc):
    """
    For a given SRA experiment accession, retrieve the read-types of its 
    runs. 

    For example, let's say an experiment has two runs where:
        - run_A is paired-end with the first read being forward 
            and the second reverse and 
        - run_B is single-end with forward reads
    this method will return the set 
                    {(FORWARD, REVERSE), (FORWARD)}
    That is, it returns the set of all readtypes present in the runs of the
    experiment.
    """
    runs = retrieve_run_accessions(exp_acc)
    readtypes = Set()
    with open(RUN_TO_READTYPES, "r") as f:
        run_to_readtype = json.load(f)
        try:
            readtypes = [tuple(run_to_readtype[r]) for r in runs]
            readtypes = Set(readtypes)
        except:
            print "ERROR! Read-type for some runs in experiment %s not found in metadata." % exp_acc
    return readtypes


def main():
    parser = OptionParser()
    #parser.add_option("-a", "--a_descrip", action="store_true", help="This is a flat")
    #parser.add_option("-b", "--b_descrip", help="This is an argument")
    (options, args) = parser.parse_args()
    print query_experiment_accessions()

if __name__ == "__main__":
    main()
