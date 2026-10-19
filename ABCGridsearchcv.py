#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report


# https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html?highlight=gridsearch#sklearn.model_selection.GridSearchCV

samples = np.loadtxt("/home/niar/Pycharmprojects/PDF_Digits_v1/PDF_Pics (copy)/AA_Combine_Set.sample", np.float32)
labels = np.loadtxt("/home/niar/Pycharmprojects/PDF_Digits_v1/PDF_Pics (copy)/AA_Combine_Set.label", np.int64)

# https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier
# NN GridSearchCV
# Scale Data.......
scaler = StandardScaler()
nn_samples = samples
scaler.fit(nn_samples)
nn_samples = scaler.transform(nn_samples)
# Variables to Find Optimum Hyperparameters
params = {"hidden_layer_sizes": [(400, ), (400, 400, 400)],
          "activation": ['identity', 'logistic', 'tanh', "relu"],
          "solver": ["lbfgs"], #, 'sgd', 'adam'],
          'learning_rate': ['constant', 'invscaling', 'adaptive'],
          # 'learning_rate_init': [0.0001], # Only for solver=’sgd’ or ‘adam’
          "alpha": [1e-4, 1e-6],
          "random_state": [0, 1]}
# A tuple (i1,i2,i3,...,in) gives a network with 'n' hidden layers, where 'ik' gives the number of neurons in the
# kth hidden layer. For three hidden layers with 10, 30 and 20 neurons, the tuple would look like (10,30,20).

mpl = MLPClassifier()
# Gridsearch
mpl_grid = GridSearchCV(mpl, params)
mpl_grid.fit(nn_samples, labels)
print('Neural Net', '\n', 'Best Params', mpl_grid.best_params_, '\n')

# https://scikit-learn.org/stable/modules/classes.html?highlight=svm#module-sklearn.svm
# SVM GridSearchCV
# Variables to Find Optimum Hyperparameters
parameters = {'kernel': ('linear', 'rbf', 'poly'), 'tol': [1E-4, 1E-6], 'degree': [3, 5], 'C': [1, 10, 100],
              'gamma': ['scale', 'auto']}
# Support Vector Machine Model
svm_grid = svm.SVC()
# Gridsearch
svm_grid_cv = GridSearchCV(svm_grid, parameters)
svm_grid_cv.fit(samples, labels)
best_params = svm_grid_cv.best_params_
print('SVM', '\nBest Params', best_params)

# Get some Statics
x_train, x_test, y_train, y_test = train_test_split(samples, labels, train_size=0.2, random_state=4)

svm_stats = svm.SVC(C=best_params.get('C'), degree=best_params.get('degree'), gamma=best_params.get('gamma'),
                    kernel=best_params.get('kernel'), tol=best_params.get('tol'))
svm_stats.fit(x_test, y_test)
prediction = svm_stats.predict(x_test)
print("\naccuracy:", accuracy_score(y_test, prediction) * 100)
print('\nconfusion_matrix\n', confusion_matrix(y_test, prediction))
print('\nclassification_report\n', classification_report(y_test, prediction))

""""
TP - True Positive
TN - True negative
FP - False Positive
FN - False negative

Accuracy = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F-Measure = 2 x (Precision x Recall) / (Precision + Recall)

Recall - How many of this class fond over the whole number of elements of this class
Precision - How many are correctly classified among that class
F1-score - Harmonic mean between precision & recall
Support - Number of occurrences of the given class in dataset
"""
