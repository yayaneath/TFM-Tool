#coding: utf-8

import time, argparse, pandas, tensorflow, numpy, pickle

TRAINSET_SIZE = 0.8
LEARNING_RATE = 0.3
BATCH_SIZE = 10
LOG_PATH = './tmp_log_board/' + time.strftime("%Y%m%d%H%M%S", time.localtime())

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Input data read

parser = argparse.ArgumentParser(description = 'This program builds a machine learning model using a given training dataset in a CSV file')
parser.add_argument('filename', help = 'Name of the CSV file to be loaded, where classes should be consecutive numbers beginning by 0')
parser.add_argument('--header', help = 'If indicated, the file has a header row', action = 'store_true')

fileName = parser.parse_args().filename
header = parser.parse_args().header

if header:
	dataset = pandas.read_csv(fileName)
else:
	dataset = pandas.read_csv(fileName, header = None)
	dataset.columns = map(str, range(dataset.shape[1])) # New header of ints as str

print '\nWhich is the objective variable?'
print ', '.join(dataset.columns)

objColumn = ''

while objColumn not in dataset.columns:
	objColumn = raw_input('Objective column: ')

print '\n'

trainSet = dataset.sample(frac = TRAINSET_SIZE, random_state = 100)
testSet = dataset.drop(trainSet.index)

numFeatures = trainSet.shape[1] - 1
numSamples = trainSet.shape[0]
numLabels = dataset[objColumn].unique().size

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Define tensorflow

with tensorflow.name_scope('input'):
	samples = tensorflow.placeholder(tensorflow.float32, [None, numFeatures])
	targets = tensorflow.placeholder(tensorflow.int64, None)

with tensorflow.name_scope('weights'):
	weights = tensorflow.Variable(tensorflow.zeros([numFeatures, numLabels]))

with tensorflow.name_scope('biases'):
	biases = tensorflow.Variable(tensorflow.zeros([numLabels]))

with tensorflow.name_scope('softmax_model'):
	predictions = tensorflow.matmul(samples, weights) + biases

with tensorflow.name_scope('cross_entropy_cost'):
	crossEntropy = tensorflow.reduce_mean(tensorflow.nn.sparse_softmax_cross_entropy_with_logits(predictions, targets))

with tensorflow.name_scope('train_optimizer'):
	trainStep = tensorflow.train.GradientDescentOptimizer(LEARNING_RATE).minimize(crossEntropy)

with tensorflow.name_scope('accuracy'):
	correctPrediction = tensorflow.equal(tensorflow.argmax(predictions, 1), targets)
	accuracy = tensorflow.reduce_mean(tensorflow.cast(correctPrediction, tensorflow.float32))

tensorflow.scalar_summary('cost', crossEntropy)
tensorflow.scalar_summary('accuracy', accuracy)
summaryOp = tensorflow.merge_all_summaries()

init = tensorflow.initialize_all_variables()
sess = tensorflow.Session()
sess.run(init)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Train

print '\nTraining...'

writer = tensorflow.train.SummaryWriter(LOG_PATH, graph = tensorflow.get_default_graph())

for i in range(numSamples / BATCH_SIZE):
	# The last batch must get the rest of the samples
	if i * BATCH_SIZE + 2 * BATCH_SIZE > numSamples:
		batchFrame = trainSet[i * BATCH_SIZE : ]
	else:
		batchFrame = trainSet[i * BATCH_SIZE : i * BATCH_SIZE + BATCH_SIZE]

	batchSamples = batchFrame.drop([objColumn], axis = 1)
	batchTargets = sum(batchFrame[[objColumn]].values.tolist(), [])
	
	_, summary = sess.run([trainStep, summaryOp], feed_dict = {samples: batchSamples, targets: batchTargets})

	writer.add_summary(summary, i)

print 'Learnt weights:\n', sess.run(weights)
print 'Learnt biases:\n', sess.run(biases)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Test

print '\nTesting...'
batchTestSamples = testSet.drop([objColumn], axis = 1)
batchTestTargets = sum(testSet[[objColumn]].values.tolist(), [])

print 'Accuracy on test set: ', sess.run(accuracy, feed_dict = {samples: batchTestSamples, targets : batchTestTargets})

# print '\nPredicting sample:'
# print testSet.iloc[[10]]

# classification = predictions.eval(session = sess, feed_dict = {samples: testSet.iloc[[10]].drop([objColumn], axis = 1)})

# print 'The system predicts...', sess.run(tensorflow.argmax(classification, 1))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Export model

numpy.savetxt('model/Weights.txt', sess.run(weights))
numpy.savetxt('model/Biases.txt', sess.run(biases))

colsFile = open('model/Variables.txt', 'w')
for column in dataset.columns:
	if column != objColumn:
		colsFile.write('%s\n' % column)
colsFile.close()

print 'Model\'s learnt parameters exported to "model" folder.'