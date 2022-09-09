#!/bin/bash
#SBATCH --partition=Orion
#SBATCH --time=72:00:00
#SBATCH --mem=64GB
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=8

cd ~/ora-1.9.1/scripts
for file in /projects/yohe_lab/Human_OR_Final/KT/blast/*T.dedupe.fasta
do
        perl or.pl -sequence "$file" -a -d --sub "$file".sub.fasta > "$file".ORs.fasta
done

cd /projects/yohe_lab/Human_OR_Final/KT/blast
python3 /projects/yohe_lab/genomeGTFtools-master/ORA_Fix.py

#~/bbmap/dedupe.sh in="$file" out="${file%.*.*.*}".ORs.clean.fasta ow=t
