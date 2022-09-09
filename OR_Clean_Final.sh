#!/bin/bash
#SBATCH --partition=Orion
#SBATCH --time=72:00:00
#SBATCH --mem=64GB
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=8

#post-processing script for OR_Final.sh data data
cd /projects/yohe_lab/Human_OR_Final/blast
#merge TAAR and OR data
for file in *_chemo.tblastn
do
	cat "$file" "${file%.*}".blastn > "$file".merged.chemo.blastn
done

module load bedtools2
module load blast

cd /projects/yohe_lab/Human_OR_Final/blast

for file in *.merged.chemo.blastn
do
	python /projects/yohe_lab/genomeGTFtools-master/blast2gff.py -b "$file" -F -l 100 -s 0.2 > "${file%.*}".output.gff3
done

for file in *.gff3
do
	awk -vOFS='\t' '{$3 = $9; print}' "$file" > "$file".name
done


cd /projects/yohe_lab/Human_OR_Final/blast
for file in *.output.gff3.name
do
	bedtools getfasta -fi /projects/yohe_lab/Human_OR_Final/"${file%_*.*.*.*}".fna -bed /projects/yohe_lab/Human_OR_Final/blast/"$file" -s -name -fo /projects/yohe_lab/Human_OR_Final/blast/"$file".fa.out
done

#remove exact duplicates
for file in *.out
do
	~/bbmap/dedupe.sh in="$file" out="${file%.*.*}".fasta ow=t
done

#move to your home directory
cd ~/ora-1.9.1/scripts
for file in /projects/yohe_lab/Human_OR_Final/blast/*.name.fasta
do
	perl or.pl -sequence "$file" -a -d --sub "$file".sub.fasta > "$file".ORs.fasta
done

#remove empty first line from fasta file to make up for ORA bug
#this can be run repeatedly without any dataloss
#I added this script to the genomeGTFtools folder for organization
cd /projects/yohe_lab/Human_OR_Final/blast
python3 /projects/yohe_lab/genomeGTFtools-master/ORA_Fix.py

#re-remove duplicates
for file in *.fixed.fasta
do
	~/bbmap/dedupe.sh in="$file" out="${file%.*.*.*}".ORs.clean.fasta ow=t
done

#create new gff3 file from final fasta by aligning fasta against original genome
#using -out_fmt 6 and num_alignments 5
#doesnt need multithreading becasue its much faster the second time

#cd /projects/yohe_lab/Human_OR
#for file in *.fna

#blastn -query /projects/yohe_lab/Human_OR/Final_blast/"${file%.*}"INSTERT PROPER EXTENTION HERE -db /projects/yohe_lab/Human_OR/blastdb/"${file%.*}" -num_threads 8 -num_alignments 5 -outfmt 6 -out /projects/yohe_lab/Human_OR/Final_blast/"${file%.*}"_chemo.blastn
