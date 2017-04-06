from sklearn.preprocessing import OneHotEncoder
import numpy

from neupy import algorithms, layers, plots

training_set = numpy.loadtxt('training_set.txt')
print training_set.shape
testing_set = numpy.loadtxt('testing_set.txt')
print testing_set.shape

testing_attributes = numpy.delete(testing_set, 18, 1)
training_attributes = numpy.delete(training_set, 18, 1)

training_results = training_set[:,[18]]
testing_results = testing_set[:, [18]]

network = algorithms.Momentum(
        [
            layers.Input(18),
            layers.Sigmoid(40),
            layers.Sigmoid(20),
            layers.Tanh(1)
        ],
        error='categorical_crossentropy',
        step=0.15,
        verbose=True,
        shuffle_data=True,
        momentum=0.99,
        nesterov=True
)

network.architecture()

network.train(training_attributes, training_results, testing_attributes, testing_results, epochs=20)

'''for layer in network:
    print layer
    print "output shape " + layer.output_shape
    print "inpput_shape " + layer.input_shape'''
results = []
for x in range(0,10):
    result = network.predict(testing_attributes[x])
    print str(result) + " answer:" + str(testing_results[x])

