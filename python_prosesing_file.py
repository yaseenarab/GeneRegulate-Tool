from flask import render_template, session, flash, get_flashed_messages, redirect, request, Flask, url_for
import pymysql
import sys
import warnings
import pandas as pd
import numpy as np
import cs11 as cfig
import setuptools
import subprocess
import csv
from collections import defaultdict

#conect with the sql database

con = pymysql.connect(host=cfig.con['host'], user=cfig.con['user'], password=cfig.con['password'],
                      database=cfig.con['database'])
cur = con.cursor()
#end

filename = "sample_file_1.tsv" #make it jthe file name input
data = pd.read_csv(filename, sep='\t')
# to know what is he have in the data e only or e and s

header = data.columns.tolist()
number_colum = len(header)
if number_colum == 9:
    sillincer = "true"
else:
    sillincer = "false"

# now that we know if there is silincer in the file or no we can complete our work

# we will need what organ is it coming from for the loop
# I will make it in a way that have a data sql and if you chose the name it will have the file name pre-install there
# so we will need to call the filename from the sql data and the orgain name as the key


query  = '''select file from organ where name = %s ;'''

organ_name = 'hh' # the chosen orgain from the html file (user)

cur.execute(query, organ_name)
loop_rr = cur.fetchone()
if loop_rr:
    loop_filename = loop_rr[0]
    loop_filename = loop_filename.split('/')[-1]
    print(loop_filename)


#loop_file_name = "Schmitt_2016_Pancreas_hg19_peakachu-merged_loops.bed"


# we now have the loop file nmae and the file name we also know if there is silincer or there not

# now we will need to get the result and once the result are there we will add then to
# the database so that we can eassy get them back when they are needed them
# we will need to have a line for every gene and the number of e and the number of s if needed


# the data that I will be getting will only be data it is not eve aline i will have to a line them it is
# just a set of data it even can be in what ever way






# so there have to be a set before were I will have to cut the stuff into multible files
# once everything have it own file will start working with the files
# there will be an allign where I will a line the gene with the loop first
# then I will a line the enhancer with the loop and the silincer with the loop
# last thing if they share the same loop name/id they are togather otherwise no
# the genes loop are the start the rest I do not care about if it is not in the gene then it will not count

# it will only be a counter I will not return the result it is only a counter for every gene and the data will be
# store in the database




# DIVID THE DATA TO FILE START

first_three_columns = data.iloc[:, 0:4]
first_three_columns.to_csv("gene.bed", sep='\t', index=False)

#first_three_columns = data.iloc[:, 4:7]
#first_three_columns.to_csv("enhancer.bed", sep='\t', index=False)

if sillincer:
    first_three_columns = data.iloc[:, 7:10]
    first_three_columns.to_csv("silincer.bed", sep='\t', index=False)


loop_data = pd.read_csv(loop_filename, sep='\t')
selected_columns = loop_data.iloc[:, [0, 1, -1]].copy()
num_rows = selected_columns.shape[0]
#selected_columns.loc[:, '0'] = range(1, num_rows + 1)
#selected_columns.to_csv("loop.bed", sep='\t', index=False)

#  END


# DATA ALLIGN PROSSES WITH LOOP START


bedtools_command = ["bedtools", "intersect", "-a", "loop.bed", "-b", "gene.bed","-wa","-wb"]
output = subprocess.check_output(bedtools_command, universal_newlines=True)
with open("loop+gene.bed", "w") as file:
    file.write(output)

bedtools_command = ["bedtools", "intersect", "-a", "loop.bed", "-b", "enhancer.bed","-wa","-wb"]
output = subprocess.check_output(bedtools_command, universal_newlines=True)
with open("loop+enhancer.bed", "w") as file:
    file.write(output)

if sillincer:
    bedtools_command = ["bedtools", "intersect", "-a", "loop.bed", "-b", "silincer.bed","-wa","-wb"]
    output = subprocess.check_output(bedtools_command, universal_newlines=True)
    with open("loop+silincer.bed", "w") as file:
        file.write(output)

#END


# now we have to match the sutf on the number of the loop
# i will match the gene with the enhancer then the g+e with the sillincer

# COUNT E AND S FROM GENE DATA START

with open('loop+gene.bed', 'r') as file1, open('loop+enhancer.bed', 'r') as file2:
    file1_lines = file1.readlines()
    file2_lines = file2.readlines()
file2_dict = {}
for line in file2_lines:
    split_line = line.split('\t')
    col4_value = split_line[3].strip()
    file2_dict[col4_value] = line
with open('gene+enhancer.bed', 'w') as file3:
    for line in file1_lines:
        split_line = line.split('\t')
        col4_value = split_line[3].strip()
        if col4_value in file2_dict:
            # If a match is found, write the merged row to file3
            merged_line = line.strip() + '\t' + file2_dict[col4_value]
            file3.write(merged_line)
with open('gene+enhancer.bed', 'r') as file:
    file_lines = file.readlines()
gene_counts = defaultdict(int)
for line in file_lines:
    split_line = line.split('\t')
    gene_name = split_line[7].strip()
    gene_counts[gene_name] += 1
with open('gene+en_number.bed', 'w') as output_file:
    # Write the gene names and counts to the output file
    for gene_name, count in gene_counts.items():
        output_line = f"{gene_name}\t{count}\n"
        output_file.write(output_line)
if sillincer:
    with open('loop+gene.bed', 'r') as file1, open('loop+silincer.bed', 'r') as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()
    file2_dict = {}
    for line in file2_lines:
        split_line = line.split('\t')
        col4_value = split_line[3].strip()
        file2_dict[col4_value] = line
    with open('gene+silincer.bed', 'w') as file3:
        for line in file1_lines:
            split_line = line.split('\t')
            col4_value = split_line[3].strip()
            if col4_value in file2_dict:
                merged_line = line.strip() + '\t' + file2_dict[col4_value]
                file3.write(merged_line)
    with open('gene+silincer.bed', 'r') as file:
        file_lines = file.readlines()
    gene_counts = defaultdict(int)
    for line in file_lines:
        split_line = line.split('\t')
        gene_name = split_line[7].strip()
        gene_counts[gene_name] += 1
    with open('gene+si_number.bed', 'w') as output_file:
        for gene_name, count in gene_counts.items():
            output_line = f"{gene_name}\t{count}\n"
            output_file.write(output_line)
#END

#add it back to the data base so that i can use it in the front end.

with open('gene+en_number.bed', 'r') as file9:
    for line in file9:
        gene_name1, enh2 = line.strip().split('\t')
        query = "INSERT INTO file_result VALUES (%s, %s,null) "
        cur.execute(query, (gene_name1, enh2))

if sillincer:
    with open('gene+si_number.bed', 'r') as file0:
        for line in file0:
            gene_name2, silin2 = line.strip().split('\t')
            cur.execute("update file_result set silin = %s where gene_name = %s",(silin2,gene_name2))
            print("s")
#end

con.commit()
con.close()
