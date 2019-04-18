# SRApy 

The Python package ``download_and_quantify`` contains code for downloading raw RNA-seq data from the SRA into FASTQ files.

## Setup 

This package requires a few installations. First, the [SRA toolkit](https://www.ncbi.nlm.nih.gov/books/NBK158900/) must be installed. Then, makes sure that the SRA toolkit's executables are added to the Linux ``PATH`` environment variable. For example, on my machine these executables might be located in ``sratoolkit.2.8.2-1-centos_linux64/bin`` given that ``sratoolkit.2.8.2-1-centos_linux64`` is the SRA Toolkit directory.

Next, you will need to download [Aspera](https://asperasoft.com) and make sure the ``aspera`` executable is also on the ``PATH`` variable. 

Finally, the SRA Toolkit requires an Aspera private key (see SRA Toolkit documentation), which will need to be added to a ``ASPERA_KEY`` environment variable.
