# OFX2CSV
##Generate CSV files from OFX files. 

This works with the Wealthfront OFX export. It will generate two files for each input file: one for transactions and one for positions. 

It currently only supports one account per file.

Usage: 
    pip install -r requirements.txt
    python ofx2csv.py <file_path> <output_dir>, where output_dir is optional.