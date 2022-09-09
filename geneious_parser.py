import os

def main():
	#define needed lists 
	types = []
	counts = []
	typesWCS = []
	countsWCS = []
	filenames = []
	#get folder name
	while True:
		try:
			print("Enter folder name: ")
			foldername = input()
			if foldername not in os.listdir():
				raise ValueError
		except ValueError:
			print("Folder not found.")
		except FileNotFoundError:
			print("Folder not found.")
		else:
			break
	#create foldername_parsed
	foldername_parsed = foldername + "_parsed"
	#check if already folder exsists, make it if it doesn't
	if foldername_parsed not in os.listdir():
		os.mkdir(foldername_parsed)
	#gather all the filenames from the data folder into a list of filenames
	#this has to be done becasue the os.listdir() function also changes the working directory
	#this change causes conflicts with the file navigation commands in the headerParser function
	for filename in os.listdir(foldername):
		filenames.append(filename)
	#send each filename from the list to the headerParser function
	#the function does its own file navigation, so no navigation is needed in hte main function
	#the headerParser function also returns the name of the newly made file so it can be updated in the filename list
	for i in range(0, len(filenames)):
		filenames[i] = headerParser(filenames[i], foldername, foldername_parsed)
	#run geneCounter on all files in foldername_parsed
	#values returned by geenCounter are put into temporary holding variable before being added to lists
	for i in range(0, len(filenames)):
		types_Temp, counts_Temp, typesWCS_Temp, countsWCS_Temp = geneCounter(filenames[i], foldername_parsed)
		types.append(types_Temp)
		counts.append(counts_Temp)
		typesWCS.append(typesWCS_Temp)
		countsWCS.append(countsWCS_Temp)
	#merge types and typesWCS into single lists for use as headers when writing the table
	headers, headerWCS = listMerger(types, typesWCS)
	#send all lists to csvWriter so tables can be generated
	csvWriter(types, counts, typesWCS, countsWCS, headers, headerWCS, filenames, foldername)
	#make geneious file structure
	geneiousFileMaker(types,foldername, filenames)
	#must be given specific itme from the lists in a loop--------------------------------
	for filename in filenames:
		geneiousFilePopulator(geneiousSequenceParser(filename, foldername_parsed, foldername), filename, foldername)

def headerParser(filename, foldername, foldername_parsed):
	#define neccesary lists
	onlyHeaders = []
	#nagivate to the proper folder
	os.chdir(foldername)
	#extract out all the headers from the fasta file and put them in onlyHeaders list
	with open(filename) as fh:
		for line in fh:
			if line.startswith(">"):
				onlyHeaders.append(line)
	#navigate out of data folder and back into starting folder
	os.chdir(os.path.dirname(os.getcwd()))
	#navigate into parsedData folder to deposit the new file
	os.chdir(foldername_parsed)
	#extract species name from filename, all file names have either "GCF" or "GCA" after the species name
	#this is done after the filename varialbe has been used to referecen the file, so it can be chagned now
	#filename = filename.split("GC") <------------ This only works for reference genomes
	filename = filename.split("genomic") # <------ This works for non-referecne genomes
	filename = filename[0].strip("_")
	filename += ".txt"
	#create new empty file using species name extracted from filename
	newFile = open(filename, "w")
	#write each header to new empty file
	for header in onlyHeaders:
		newFile.write(header)
	#close new file
	newFile.close()
	#navigate back to starting folder
	os.chdir(os.path.dirname(os.getcwd()))
	#return modified filename so it can be used in other function to refer to the newly made file
	return(filename)

def geneCounter(filename, foldername_parsed):
	#define required lists
	OR_list = []
	types_list = []
	types_list_with_coding_status = []
	counts_list = []
	counts_list_with_coding_status = []
	#navigate to parsedData folder
	os.chdir(foldername_parsed)
	#open file and extract gene names and coding status to OR_list
	with open(filename)as fh:
		for line in fh:
			line = line.split("|")
			if len(line) == 2:
				OR_list.append(tuple([line[1].strip("\n"), "CODING"]))
			elif len(line) == 3:
				OR_list.append(tuple([line[1].strip("\n"), line[2].strip("\n")]))
	
	
	#identify all unique gene type and coding status pairs in OR_list and add them to types_list_with_coding_status
	#include both gene type and coding status in types_list_with_coding_status
	for OR in OR_list:
		if OR in types_list_with_coding_status:
			pass
		else:
			types_list_with_coding_status.append(OR)
	#identify all unique gene types in OR_list and add them to types_list
	#having both types_list_with_coding_status and types_list allows for multiple types of table to be made later
	for OR in OR_list:
		if OR[0] in types_list:
			pass
		else:
			types_list.append(OR[0])

	#add a zero value entry to counts list for each unique gene type in types_list
	for Type in types_list:
		counts_list.append(0)
	#does the same as above but for counts_list_with_coding_status and types_list_with_coding_status	
	for Type in types_list_with_coding_status:
		counts_list_with_coding_status.append(0)
	#tally up the total number of each unique gene type in OR_list, tallies as put int counts_list
	for i in range(0, len(types_list)):
		for OR in OR_list:
			if OR[0] == types_list[i]:
				counts_list[i] += 1
	#does the same as above but for counts_list_with_coding_status and types_list_with_coding_status			
	for i in range(0, len(types_list_with_coding_status)):
		for OR in OR_list:
			if OR == types_list_with_coding_status[i]:
				counts_list_with_coding_status[i] += 1
	#navigate back to starting folder
	os.chdir(os.path.dirname(os.getcwd()))
	#return both sets of type_lists
	return(types_list, counts_list, types_list_with_coding_status, counts_list_with_coding_status)

def listMerger(types, typesWCS):
	#define list to hold both the full header list and the full header list w/ coding status
	header = []
	headerWCS = []
	#run through each list in types and see if it needs to be added to header
	for i in range(0, len(types)):
		for j in range(0, len(types[i])):
			if types[i][j] in header:
				pass
			else:
				header.append(types[i][j])
	#run through each list in typesWCS and see if it needs to be added to headerWCS	
	for i in range(0, len(typesWCS)):
		for j in range(0, len(typesWCS[i])):
			if typesWCS[i][j] in headerWCS:
				pass
			else:
				headerWCS.append(typesWCS[i][j])
	#return both full lists
	return(header, headerWCS)

def csvWriter(types, counts, typesWCS, countsWCS, headers, headerWCS, filenames, foldername):
	#create empty file to print data w/o coding status
	newFile = open(foldername + ".txt", "w")
	#write headers to top of file, check for last header so that no comma is written
	newFile.write("Organism Name" + ", ")
	for header in headers:
		if headers.index(header) == len(headers) - 1:
			newFile.write(header)
		else:
			newFile.write(header + ", ")
	#end header line
	newFile.write("\n")
	#write mammal name excluding .txt
	#check if an OR type is in each type list, write the corresponding count if it is, otherwise write a 0
	#excludes commas from the ends of each row
	for i in range(0, len(filenames)):
		newFile.write(filenames[i].strip(".txt") + ", ")
		for header in headers:
			if headers.index(header) == len(headers) - 1:
				if header in types[i]:
					newFile.write(str(counts[i][types[i].index(header)])) 
				else:
					newFile.write("0")
			else:
				if header in types[i]:
					newFile.write(str(counts[i][types[i].index(header)]) + ", ") 
				else:
					newFile.write("0 ,")
		newFile.write("\n")
	#close new file
	newFile.close()

	#create empty file to print data with coding status CODING
	newFile = open(foldername + "_coding_status.txt", "w")
	#write headers to top of file, check for last header so that no comma is written
	newFile.write("Organism Name" + ", ")
	#write OR type and coding status separated by a hyphen
	for header in headerWCS:
		if header[1] == "CODING":#<----------------------------------------
			if headerWCS.index(header) == len(headerWCS) - 1:
				newFile.write(header[0] + "-" + header[1])
			else:
				newFile.write(header[0] + "-"+ header[1] + ", ")
	#end header line
	newFile.write("\n")
	#write mammal name excluding .txt
	#check if an OR type with coding status is in each type list, write the corresponding count if it is, otherwise write a 0
	#excludes commas from the ends of each row
	for i in range(0, len(filenames)):
		newFile.write(filenames[i].strip(".txt") + ", ")
		for header in headerWCS:
			if header[1] == "CODING": #<----------------------------------------
				if headerWCS.index(header) == len(headerWCS) - 1:
					if header in typesWCS[i]:
						newFile.write(str(countsWCS[i][typesWCS[i].index(header)])) 
					else:
						newFile.write("0")
				else:
					if header in typesWCS[i]:
						newFile.write(str(countsWCS[i][typesWCS[i].index(header)]) + ", ") 
					else:
						newFile.write("0 ,")
		newFile.write("\n")
	#close new file
	newFile.close()
	
	#create empty file to print data with coding status PSUEDOGENE
	newFile = open(foldername + "_coding_status_psuedo.txt", "w")
	#write headers to top of file, check for last header so that no comma is written
	newFile.write("Organism Name" + ", ")
	#write OR type and coding status separated by a hyphen
	for header in headerWCS:
		if header[1] == "PSEUDOGENE":#<----------------------------------------
			if headerWCS.index(header) == len(headerWCS) - 1:
				newFile.write(header[0] + "-" + header[1])
			else:
				newFile.write(header[0] + "-"+ header[1] + ", ")
	#end header line
	newFile.write("\n")
	#write mammal name excluding .txt
	#check if an OR type with coding status is in each type list, write the corresponding count if it is, otherwise write a 0
	#excludes commas from the ends of each row
	for i in range(0, len(filenames)):
		newFile.write(filenames[i].strip(".txt") + ", ")
		for header in headerWCS:
			if header[1] == "PSEUDOGENE": #<----------------------------------------
				if headerWCS.index(header) == len(headerWCS) - 1:
					if header in typesWCS[i]:
						newFile.write(str(countsWCS[i][typesWCS[i].index(header)])) 
					else:
						newFile.write("0")
				else:
					if header in typesWCS[i]:
						newFile.write(str(countsWCS[i][typesWCS[i].index(header)]) + ", ") 
					else:
						newFile.write("0 ,")
		newFile.write("\n")
	#close new file
	newFile.close()

def geneiousFileMaker(types, foldername, filenames):
#make head folder name
	headFolder = foldername + "_geneious"
#make head folder for geneious file structure
	if headFolder not in os.listdir():
		os.mkdir(headFolder)
#move into head folder
	os.chdir(headFolder)
#make a folder for each gene
	for i in range(0, len(filenames)):
		if filenames[i].strip(".txt") not in os.listdir():
			os.mkdir(filenames[i].strip(".txt"))
		os.chdir(filenames[i].strip(".txt"))
		for OR in types[i]:
			if OR not in os.listdir():
				os.mkdir(OR)
				os.chdir(OR)
				os.mkdir(OR + "_CODING")
				os.mkdir(OR + "_PSEUDOGENE")
				os.chdir(os.path.dirname(os.getcwd()))
		os.chdir(os.path.dirname(os.getcwd()))
		os.chdir(os.path.dirname(os.getcwd()))
		os.chdir(headFolder)
#return to starting directory
	os.chdir(os.path.dirname(os.getcwd()))

def geneiousSequenceParser(filename, foldername_parsed, foldername):
	#define needed lists
	OR_list = []
	codingStatus = []
	headerList = []
	seqList = []
	masterList = []
	#move into original data folder
	os.chdir(foldername)
	#gather the contents of each fasta file into a list of tuples
	for file in os.listdir():
		if filename.strip(".txt") in file:
			with open(file) as fh:
				for line in fh:
					if line.startswith(">") == True:
	#add header to header list
						headerList.append(line.strip("\n"))
	#parse out OR type to put in tuple list later
						OR = line.split("|")
	#determine if gene is coding or pseudo
						if len(OR) == 2:
							OR_list.append(OR[1].strip("\n"))
							codingStatus.append("CODING")
						elif len(OR) == 3:
							OR_list.append(OR[1].strip("\n"))
							codingStatus.append(OR[2].strip("\n"))
	#define temp string to hold growing sequences
				temp = ""
	#run through file again to parse out sequences
			with open(file) as fh:
				for line in fh:
					if line.startswith(">") == True:
						seqList.append(temp)
						temp = ""
					else:
						temp += line.strip("\n")
	#add in last sequence as there are no more > symbols
				seqList.append(temp)
	#remove first empty itme from seqList
				del(seqList[0])

	#combine lists into masterList
	for i in range(0, len(OR_list)):
		masterList.append(tuple([OR_list[i], codingStatus[i], headerList[i], seqList[i]]))
	#send masterList from a single animal file back to main so its data can be written to the proper folder
	os.chdir(os.path.dirname(os.getcwd()))
	return(masterList)

def geneiousFilePopulator(masterList, filename, foldername):
	#navigate to proper folder
	os.chdir(foldername + "_geneious")
	os.chdir(filename.strip(".txt"))
	#run through masterList and distribute files into proper folders
	for tup in masterList:
	#move into correct OR type folder
		os.chdir(tup[0])
	#move into correct coding status folder
		os.chdir(tup[0] + "_" + tup[1])
	#write new file
		newFile = open(tup[2], "w")
		newFile.write(tup[2] + "\n")
		newFile.write(tup[3] + "\n")
	#return to head file
		os.chdir(os.path.dirname(os.getcwd()))
		os.chdir(os.path.dirname(os.getcwd()))
	#return to original directory
	os.chdir(os.path.dirname(os.getcwd()))
	os.chdir(os.path.dirname(os.getcwd()))
	print(filename.strip(".txt") + " done.")

if __name__ == '__main__':
	main()