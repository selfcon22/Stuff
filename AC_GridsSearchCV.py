#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

samples = np.loadtxt('Loads_Data.Sample', np.float32)
labels = np.loadtxt('Loads_Data.Label', dtype=np.str)
warm_start = False
# early_stopping=False

# Scale Data
scalar = StandardScaler()
nn_samples = samples
scalar.fit(nn_samples)
nn_samples = scalar.transform(nn_samples)

parameters = {'hidden_layer_sizes': [(400, ), (400, 400, 400)], 
              'activation': ['identity', 'logistic', 'tahn', 'relu'], 
              'solver': ['lbfgs'], 
              'learning_rate': ['constant'], 
              'alpha': [1e-4, 1e-6], 
              'random_state': [0, 1]}

mpl_nn = MLPClassifier()

clf = GridSearchCV(mpl_nn, parameters)

clf.fit(samples, labels)
best_params = mpl_nn.best_params_

print(f"NN, \nbest params {best_params}")

# Get Stats
x_train, x_test, y_train, y_test = train_test_split(samples, labels, trains_size=0.2, random_state=1)

#nn_stats = mpl_nn.MLPClassifier()