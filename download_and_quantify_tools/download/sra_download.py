#!/usr/bin/python

#################################################################################################
#       Methods for downloading SRA files from the SRA database
#################################################################################################

import xml.etree.ElementTree as et
import urllib2
import os
from os.path import join, dirname
import sys
import random
import time
import sqlite3
import pkg_resources as pr
import json
from collections import deque, defaultdict
from optparse import OptionParser

from ..common import query_metadata
from ..common import command_line as cl
from ..common import config

# Parallel downloading
NUM_DOWNLOAD_SLOTS = 7

# Binaries
ASPERA_BIN = "ascp"
PREFETCH_BIN = "prefetch"
CONFIGURE_BIN = "vdb-config"
FASTQ_DUMP_BIN = "fastq-dump"

# log
SRA_FILE_PREFIX = "anonftp@ftp.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByRun/sra"

# Error messages that may be contained in the output of the SRA toolkit.
SRA_REMOVED = "Access denied - object has been removed from distribution"
NO_PERMISSION = "Access denied - please request permission to access"

def main():
    parser = OptionParser()
    #parser.add_option("-a", "--a_descrip", action="store_true", help="This is a flat")
    parser.add_option("-d", "--destination", help="Destination of SRA files.")
    (options, args) = parser.parse_args()

    sra_acc = args[0]
    destination = options.destination
    download_sra(sra_acc, destination=destination)


def download_and_organize_fastqs_for_experiment(
        exp_acc, 
        destination=".", 
        gzip=False,
        bypass_slots=False
    ):
    """
    Download FASTQ files for a given experiment. The first reads are 
    located in a subdirectory called "read1" and the second reads are 
    located in subdirectory "read2" if there are a set of second reads.
    Args:
        exp_acc: the experiment accession
        destination: download destination
        bypass_slots: if False, this script will check a 'download 
            status' directory to see how many jobs are downloading from 
            the NCBI. If more than the the threshold are downloading at 
            a time, then wait until some jobs finish.
    """
    def is_fastq(fastq_fname):
        # Determine if this is a FASTQ file
        toks = fastq_fname.split(".")
        if gzip:
            if len(toks) > 1:
                if toks[-2] != "fastq" or toks[-1] != "gz":
                    return False
            else:
                return False
        else:
            if toks[-1] != "fastq":
                return False
        return True

    no_permission, removed, download_dir = download_sras_for_experiment(
        exp_acc, 
        destination=destination, 
        gzip=gzip,
        bypass_slots=bypass_slots
    )
    read_index_to_fastqs = defaultdict(lambda: [])
    for fastq_fname in os.listdir(download_dir):
        if not is_fastq(fastq_fname):
            continue
        fastq_f = join(download_dir, fastq_fname)
        read_index = fastq_fname.split(".")[0].split("_")[-1]
        read_index_to_fastqs[read_index].append(fastq_f)
    for read_index, fastqs in read_index_to_fastqs.iteritems():
        read_dir = join(download_dir, "read_%s" % read_index)
        cl.run_command("mkdir %s" % read_dir)
        for fastq in fastqs:
            cl.run_command("mv %s %s" % (fastq, read_dir))
    return download_dir


def download_sras_for_experiment(
        exp_acc, 
        destination=".", 
        gzip=False, 
        bypass_slots=False
    ):
    """
    Download SRA files for a given experiment.
    Args:
        exp_acc: the experiment accession
        destination: download destination
        bypass_slots: if True, this script will check a 'download 
            status' directory to see how many jobs are downloading 
            from the NCBI. If more than the the threshold are 
            downloading at a time, then wait until some jobs finish.
    """
    download_dir = join(destination, exp_acc)
    cl.run_command("mkdir %s" % download_dir)
    no_permission = []
    removed = []
    try:
        run_accs = query_metadata.get_runs(exp_acc)
        for run_acc in run_accs:
            out, err = download_sra(
                run_acc, 
                destination=download_dir,
                gzip=gzip,
                bypass_slots=bypass_slots
            ) 
            if SRA_REMOVED in err:
                removed.append(run_acc)
            if NO_PERMISSION in err:
                no_permission.append(run_acc)
    except KeyError, e:
        print "DOWNLOAD_ERROR: Unable to find run data for experiment %s." % exp_acc
    return no_permission, removed, download_dir


def download_sra(
        run_acc, 
        destination=".", 
        gzip=False, 
        bypass_slots=True, 
        use_aspera=True
    ):
    """
    Download SRA files for a given run accession. 
    Args:
        run_acc: the run accession
        destination: location to download file
    Returns:
        size of the downloaded SRA file
    """
    configure_toolkit(destination)
    slots_loc = config.download_slots_location()

    # Wait until there is a slot for downloading the job
    if not bypass_slots:
        time.sleep(random.randint(1,10))
        while len(os.listdir(slots_loc)) >= NUM_DOWNLOAD_SLOTS:
            print "All the download slots are taken... waiting my turn"
            time.sleep(random.randint(1,10))
        with open(join(slots_loc, run_acc), 'w') as f:
            f.write('.')
    try:
        if use_aspera:
            # Prefetch the SRA files with aspera
            cmd = '%s --ascp-path "%s|%s" %s' % (
                PREFETCH_BIN,
                ASPERA_BIN,
                config.aspera_key_loc(),
                run_acc
            )
            out, err = cl.run_command_capture_output(cmd)
            if out:
                print "Output:\n%s" % out
            if err:
                print "Error:\n%s" % err

            # Convert the SRA files to FASTQ
            sra_file = join(destination, "sra", "%s.sra" % run_acc)
            cmd = "%s %s -O %s --split-files " % (
                FASTQ_DUMP_BIN,
                sra_file,
                destination
            )
            # Remove the file that claims a download slot
            # perform this here, so that slot is released
            # for the FASTQ conversion
            if not bypass_slots:
                cl.run_command("rm %s" % join(slots_loc, run_acc))

            if gzip:
                cmd += "--gzip "
            out, err = cl.run_command_capture_output(cmd)
            if out:
                print "Output:\n%s" % out
            if err:
                print "Error:\n%s" % err
        else:
            cmd = "%s %s -O %s --split-files " % (
                FASTQ_DUMP_BIN,
                run_acc,
                destination
            )
            if gzip:
                cmd += "--gzip "
            out, err = cl.run_command_capture_output(cmd)
            if out:
                print "Output:\n%s" % out
            if err:
                print "Error:\n%s" % err
            # Remove the file that claims a download slot
            if not bypass_slots:
                cl.run_command("rm %s" % join(slots_loc, run_acc))
    except Exception as e:
        if not bypass_slots:
            cl.run_command("rm %s" % join(slots_loc, run_acc))
        raise e
    return out, err


def configure_toolkit(destination, rate=1500):
    cl.run_command(
        "%s -s /tools/ascp/max_rate=%dm" % (
            CONFIGURE_BIN, 
            rate
        )
    )
    cl.run_command(
        "%s -s /repository/user/main/public/root=%s" % (
            CONFIGURE_BIN, 
            destination
        )
    )


def build_ascp_url(sra_acc):
    return "%s/%s/%s/%s/%s.sra" % (SRA_FILE_PREFIX, sra_acc[0:3], sra_acc[0:6], sra_acc, sra_acc)


if __name__ == "__main__":
    main()
