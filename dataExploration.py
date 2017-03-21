#coding: utf-8

import sys, pandas, argparse, time, numpy
import matplotlib.pyplot as pyplot

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Auxiliar functions

def dataVisualizationModule(dataset):
	print '\nSelect one of the following visualizations:'
	print '1- Histogram (hist)'
	print '2- Scatter plot (scatter)'

	plotType = ''

	while plotType not in ['1', '2', 'B']:
		plotType = raw_input('Selection: ')

	if plotType == '1':
		print '\nSelect the column that will be visualized:'
		print ', '.join(dataset.columns)

		selectedColumn = ''

		while selectedColumn not in dataset.columns and selectedColumn != 'B':
			selectedColumn = raw_input('Selected column: ')

		if selectedColumn == 'B':
			return

		try:
			dataset[selectedColumn].dropna().plot(kind = 'hist', 
				xticks  = dataset[selectedColumn].dropna().unique(), 
				bins = dataset[selectedColumn].dropna().unique().size)
			pyplot.xlabel(selectedColumn)
			pyplot.title(selectedColumn + ' distribution')
			pyplot.grid(True)
			pyplot.show()
		except Exception as e:
			print 'Unexpected error:', str(e)

	elif plotType == '2':
		print '\nIndicate the column for the x axis:'
		print ', '.join(dataset.columns)

		selectedXColumn = ''

		while selectedXColumn not in dataset.columns and selectedXColumn != 'B':
			selectedXColumn = raw_input('Selected column: ')

		if selectedXColumn == 'B':
			return

		print '\nIndicate the column for the y axis:'
		print ', '.join(dataset.columns)

		selectedYColumn = ''

		while selectedYColumn not in dataset.columns and selectedYColumn != 'B':
			selectedYColumn = raw_input('Selected column: ')

		if selectedYColumn == 'B':
			return

		print '\nWhich is the objective column?'
		print ', '.join(dataset.columns)

		objColumn = ''

		while objColumn not in dataset.columns and objColumn != 'B':
			objColumn = raw_input('Objective column: ')

		if objColumn == 'B':
			return

		try:
			dataset.plot(kind = 'scatter', 
				x = selectedXColumn, 
				y = selectedYColumn, 
				c = objColumn, 
				s = 50)
			pyplot.xlabel(selectedXColumn)
			pyplot.ylabel(selectedYColumn)
			pyplot.title(selectedXColumn + ' - ' + selectedYColumn)
			pyplot.grid(True)
			pyplot.show()
		except Exception as e:
			print 'Unexpected error:', str(e)

	else:
		return

def dataNormalizationModule(dataset, fileName):
	print '\nSelect a method:'
	print '1- Feature scaling'
	print '2- Standardization'

	processingMethod = ''

	while processingMethod not in ['1', '2', 'B']:
		processingMethod = raw_input('Selection: ')

	if processingMethod == 'B':
		return dataset

	print 'Working...'

	if processingMethod == '1':
		processedDataset = (dataset - dataset.min()) / (dataset.max() - dataset.min())

	elif processingMethod == '2':
		processedDataset = (dataset - dataset.mean()) / dataset.std()

	return processedDataset

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Main program

parser = argparse.ArgumentParser(description = 'This program explores and preprocesses a dataset file')
parser.add_argument('filename', help = 'Name of the file to be loaded')
parser.add_argument('--header', help = 'If indicated, the file has a header row', action = 'store_true')

fileName = parser.parse_args().filename
header = parser.parse_args().header

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Data read

if header:
	dataset = pandas.read_csv(fileName)
else:
	dataset = pandas.read_csv(fileName, header = None)
	dataset.columns = map(str, range(dataset.shape[1])) # New header of ints as str
	
dataset = dataset.apply(pandas.to_numeric, errors = 'coerce')

print 'Initial description of the read data:'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Menu presentation

while True:
	print '\n', dataset.describe()

	print '\nWhat action do you want to perform over the dataset?'
	print '1- Data visualization'
	print '2- Data normalization'
	print '3- Drop feature'
	print '4- Deal with missing values'
	print '5- Convert to numeric classes'
	print 'S- Save file'
	print 'Q- Quit'
	print 'You can always type B in any submenu to get back to the program menu.'

	action = ''

	while action not in ['1', '2', '3', '4', '5', 'S', 'Q']:
		action = raw_input('Selection: ')

	# Data visualization - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	if action == '1':
		dataVisualizationModule(dataset)

	# Data normalization - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	elif action == '2':
		dataset = dataNormalizationModule(dataset, fileName)
		time.sleep(2)
	
	# Drop feature - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	elif action == '3':
		print '\nIndicate the column that will be removed:'
		print ', '.join(dataset.columns)

		droppedColumn = ''

		while droppedColumn not in dataset.columns and droppedColumn != 'B':
			droppedColumn = raw_input('Dropped column: ')

		if droppedColumn == 'B':
			continue

		dataset = dataset.drop([droppedColumn], axis = 1)

	# Deal with missing values - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	elif action == '4':
		print '\nSelect a method:'
		print '1- Replace with feature mean'
		print '2- Drop rows'

		missMethod = ''

		while missMethod not in ['1', '2', 'B']:
			missMethod = raw_input('Selection: ')

		if missMethod == 'B':
			continue

		if missMethod == '1':
			print 'Replacing every non-numerical value...'
			dataset.fillna(dataset.mean(), inplace = True)
		elif missMethod == '2':
			print 'Removing every row with missing values...'
			dataset.dropna(inplace = True)

		time.sleep(2)

	# Convert to numeric classes - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	elif action == '5':
		print '\nIndicate the classes column:'
		print ', '.join(dataset.columns)

		classColumn = ''

		while classColumn not in dataset.columns and classColumn != 'B':
			classColumn = raw_input('Class column: ')

		if classColumn == 'B':
			continue

		classes = dataset[classColumn].unique()

		for i in range(len(classes)):
			print 'Mapping the value "', classes[i], '" to', i

			dataset.loc[dataset[classColumn] == classes[i], classColumn] = i

	# Save file - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	elif action == 'S':
		if header:
			dataset.to_csv(fileName + '.new', encoding = 'utf-8', index = False)
		else:
			dataset.to_csv(fileName + '.new', encoding = 'utf-8', index = False, header = False)

		print 'Saving as', fileName + '.new ...'
		time.sleep(2)

	# Quit - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	elif action == 'Q':
		sys.exit(0)