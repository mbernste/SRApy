# SRApy 

The Python package ``download_and_quantify`` contains code for downloading raw RNA-seq data from the SRA into FASTQ files.

## Setup 

This package requires a few installations. First, the [SRA toolkit](https://www.ncbi.nlm.nih.gov/books/NBK158900/) must be installed. Then, makes sure that the SRA toolkit's executables are added to the Linux ``PATH`` environment variable. For example, on my machine these executables are located in ``sratoolkit.2.8.2-1-centos_linux64/bin`` given that ``sratoolkit.2.8.2-1-centos_linux64`` is the SRA Toolkit directory.

Next, you will need to download [Aspera](https://asperasoft.com) and make sure the ``aspera`` executable is also on the ``PATH`` variable. 

The SRA Toolkit requires an Aspera private key (see SRA Toolkit documentation), which will need to be added to a ``ASPERA_KEY`` environment variable:

``export ASPERA_KEY=<path to Aspera key>``

Finally, the Python dependencies are listed in ``requirements.txt``.

## Download the FASTQ files for an SRA experiment 

To download the FASTQ files for an SRA experiment, run 

``python download_experiment.py <SRA experiment accession> -d <download destination>`` 

This will create a directory ``<download destination>/<SRA experiment accession>`` that will store the FASTQ file for each read (for paired-end data, there will be a FASTQ for the forward and reverse stranded read).


