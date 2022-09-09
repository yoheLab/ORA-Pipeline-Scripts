import os

def main():
	#decleare required list
	lines = []
	#traverse through all files
	for filename in os.listdir():
		#select the specific files output by ORA
		if filename.endswith("ORs.fasta"):
			with open(filename) as fh:
				for line in fh:
					#only grab lines that arent empty
					if line.startswith(">") or line.startswith("A") or line.startswith("T") or line.startswith("C") or line.startswith("G") :
						lines.append(line)
						#print line to console for debugging
						#print(line)
					else:
						pass
			#make new file with .fixed extension
			print("Writing file: " + filename + ".fixed.fasta")
			newFile = open(filename + ".fixed.fasta", "w")
			for line in lines:
				newFile.write(line)

			#close new file
			newFile.close()
		#dump lines list memory
		lines = []

if __name__ == '__main__':
	main()
