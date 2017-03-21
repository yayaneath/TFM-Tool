#coding: utf-8

import argparse, pandas, tensorflow, numpy

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Input data read

parser = argparse.ArgumentParser(description = 'This program reuses a trained model to give predictions on a selected samples file')
parser.add_argument('filename', help = 'Name of the CSV file that stores the samples, if there are class labels they should be consecutive numbers beginning by 0')
parser.add_argument('weights', help = 'Location of the weights file')
parser.add_argument('biases', help = 'Location of the biases file')
parser.add_argument('variables', help = 'Location of the variables file')
parser.add_argument('--header', help = 'If indicated, the file has a header row', action = 'store_true')

fileName = parser.parse_args().filename
header = parser.parse_args().header
learntWeights = numpy.loadtxt(parser.parse_args().weights)
learntBiases = numpy.loadtxt(parser.parse_args().biases)
trainVariables = [line.rstrip('\n') for line in open(parser.parse_args().variables)]
numLabels = learntWeights.shape[1]

if header:
	dataset = pandas.read_csv(fileName)
else:
	dataset = pandas.read_csv(fileName, header = None)
	dataset.columns = map(str, range(dataset.shape[1])) # New header of ints as str

print '\nInput data summary:\n', dataset.describe()
print '\nTraining variables:\n', ', '.join(trainVariables)
print '\nWeights:\n', learntWeights
print '\nBiases:\n', learntBiases

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Mapping input columns

print '\nIf there is a label column already, please indicate it. Otherwise, just leave it empty:'
print ','.join(dataset.columns)

labelColumn = '-'
while labelColumn not in dataset.columns and labelColumn:
	labelColumn = raw_input('Corresponding column: ')

if labelColumn:
	labels = dataset[labelColumn]
	dataset.drop([labelColumn], axis = 1, inplace = True)
	
variablesOrder = []

for variable in trainVariables:
	print '\nWhich is the corresponding feature of', variable, ':'
	print ','.join(dataset.columns)

	corrColumn = ''
	while corrColumn not in dataset.columns:
		corrColumn = raw_input('Corresponding column: ')

	variablesOrder.append(corrColumn)

unusedVariables = list(set(dataset.columns) - set(variablesOrder))
dataset.drop(unusedVariables, axis = 1, inplace = True)
dataset = dataset[variablesOrder]

numFeatures = dataset.shape[1]
numSamples = dataset.shape[0]

print '\n'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Define tensorflow

samples = tensorflow.placeholder(tensorflow.float32, [None, numFeatures])
targets = tensorflow.placeholder(tensorflow.int64, None)
weights = tensorflow.placeholder(tensorflow.float32, [numFeatures, numLabels])
biases = tensorflow.placeholder(tensorflow.float32, [numLabels])
predictions = tensorflow.matmul(samples, weights) + biases

if labelColumn:
	predicted = tensorflow.placeholder(tensorflow.int64, None)
	correctPrediction = tensorflow.equal(predicted, targets)
	accuracy = tensorflow.reduce_mean(tensorflow.cast(correctPrediction, tensorflow.float32))

sess = tensorflow.Session()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Predictions

print '\nPredicting samples...\n'

classification = predictions.eval(session = sess, feed_dict = {samples: dataset, weights : learntWeights, biases: learntBiases})
prediction = sess.run(tensorflow.argmax(classification, 1))

if labelColumn:
	print 'Accuracy on the set: ', sess.run(accuracy, feed_dict = {predicted: prediction, targets : labels})
	dataset[labelColumn] = labels

dataset['prediction'] = prediction
dataset.to_csv(fileName + '.predicted', encoding = 'utf-8', index = False)

print 'Predictions completed! A new file called', fileName + '.predicted has been created where a new column called "prediction" holds the estimated label for each sample.'