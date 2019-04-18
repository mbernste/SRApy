#################################################################
#   Download the raw reads data from the SRA for a given
#   experiment.
#################################################################

from optparse import OptionParser
import sys
import os
from os.path import join

import download_and_quantify_tools
from download_and_quantify_tools.download import sra_download

def main():
    usage = "usage: %prog <options> <experiment_accession>"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--destination", help="Destination of SRA files.")
    parser.add_option("-u", "--uncompressed", action="store_true", help="Don't gzip FASTQ files")
    (options, args) = parser.parse_args()

    exp_acc = args[0]
    destination = options.destination
    gzip = not options.uncompressed

    sra_download.download_and_organize_fastqs_for_experiment(
        exp_acc,
        destination=destination,
        gzip=gzip, 
        bypass_slots=True
    )

if __name__ == "__main__":
    main()
