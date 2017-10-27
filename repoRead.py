#coding: utf-8

import sys, requests, urllib, json, time, re, argparse, csv

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Constants definition

DATASETS_FOLDER = 'datasets'

DATAVERSE_API_KEY = 'XXXX-XXXX'
SEARCH_API_POINT = 'https://dataverse.harvard.edu/api/search?'
DATASET_API_POINT = 'https://dataverse.harvard.edu/api/datasets/:persistentId/?'
FILEACCESS_API_POINT = 'https://dataverse.harvard.edu/api/access/datafile/'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Input data read

parser = argparse.ArgumentParser(description = 'This program reads the Harvard Dataverse repository and downloads CSV datasets')
parser.add_argument('--headerFile', help = 'File with a header row that can be used to check datasets\' importance')

headerFile = parser.parse_args().headerFile

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Search

searchKeywords = raw_input('Introduce a few keywords for your search: ')
searchQuery = {'q' : searchKeywords, 'type' : 'dataset', 'show_relevance': 'true', 'per_page' : 20, 'key' : DATAVERSE_API_KEY}
searchEncoded = urllib.urlencode(searchQuery)

response = requests.get(SEARCH_API_POINT + searchEncoded)
responseDict = json.loads(response.text)

header = searchKeywords.lower().split() # In case there is no headerFile, we use search keywords

if headerFile:
	header = [word.lower() for word in next(csv.reader(open(headerFile, 'rb')), [])]
	print 'Read header:', ', '.join(header)

print '\n', responseDict['data']['total_count'], 'datasets were found!'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Results exploration

for dataset in responseDict['data']['items']:
	print '\n********************************************************************************'
	print dataset['name']
	print '********************************************************************************'
	print '-Search score:', dataset['score']
	print '-Global Id:', dataset['global_id']

	if 'description' in dataset:
		print '-Description:', dataset['description']

		matches = [word for word in header if word in dataset['description'].lower()]
		print '-Matches:', len(matches) , '/', len(header)
		print '-Matched words:', ', '.join(matches)

	print '\nSelect an action to perform:\nD- Download CSV file\nN- Next result\nQ- Quit program'

	action = 'X'

	while action != 'N' and action != 'D' and action != 'Q':
		action = raw_input('Action: ')

	if action == 'Q':
		sys.exit(0)
	elif action == 'N':
		continue

	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	# Dataset file download

	searchQuery = {'persistentId' : dataset['global_id'], 'key' : DATAVERSE_API_KEY}
	searchEncoded = urllib.urlencode(searchQuery)

	response = requests.get(DATASET_API_POINT + searchEncoded)
	responseDict = json.loads(response.text)

	if len(responseDict['data']['latestVersion']['files']) == 0:
		print '\nNo files in this dataset. Showing the next result...'
		time.sleep(5)
		continue

	fileData = responseDict['data']['latestVersion']['files'][0]['dataFile']
	
	if re.match('.*pdf.*|.*various.*|.*i', fileData['contentType'].lower()) or re.match('.*x-stata.*|.*spss-*', fileData['originalFileFormat']):
		print '\nThis dataset includes a non-open file format (PDF, SPSS, Stata, etc). Showing the next result...'
		time.sleep(5)
		continue

	searchQuery = {'format' : 'original', 'key' : DATAVERSE_API_KEY}
	searchEncoded = urllib.urlencode(searchQuery)

	response = requests.get(FILEACCESS_API_POINT + str(fileData['id']) + '?' + searchEncoded)

	fileName = dataset['name'] + ' - ' + fileData['filename']
	targetFile = open (DATASETS_FOLDER + '/' + fileName, 'w')
	targetFile.truncate()
	targetFile.write(response.text)
	targetFile.close()

	print "\nDatafile '" + fileName + "' donwloaded!\nShowing the next result..."
	time.sleep(5)

sys.exit(0)
