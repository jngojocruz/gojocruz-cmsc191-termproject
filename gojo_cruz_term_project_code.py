# -*- coding: utf-8 -*-
"""Gojo Cruz - Term Project Code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Jvt5jpLx77RxyxUshHLm_Y7BIYF61HXF
"""

#SETUP
import tensorflow as tf
from tensorflow import keras

import os
import tempfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import math
from keras.utils import np_utils

import sklearn
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import LabelEncoder

from imblearn.over_sampling import SMOTE
from collections import Counter
from matplotlib import pyplot

# DATA PROCESSING
# Yeast Dataset
file = tf.keras.utils
raw_df = pd.read_csv("datasets/yeast.csv")
raw_df_1 = pd.read_csv("datasets/train_data_70.csv")
raw_df_2 = pd.read_csv("datasets/validation_data_15.csv")
raw_df_3 = pd.read_csv("datasets/test_data_15.csv")

# Class Label 
cyt = nuc = mit = me3 = me2 = me1 = exc = vac = pox = erl = 0
raw_dfs = [raw_df_1, raw_df_2, raw_df_3]
for df in raw_dfs:
  res_cyt, res_nuc, res_mit, res_me3, res_me2, res_me1, res_exc, res_vac, res_pox, res_erl = np.bincount(df["class_code"])
  cyt += res_cyt
  nuc += res_nuc
  mit += res_mit
  me3 += res_me3
  me2 += res_me2
  me1 += res_me1
  exc += res_exc
  vac += res_vac
  pox += res_pox
  erl += res_erl

total = cyt + nuc + mit + me3 + me2 + me1 + exc + vac + pox + erl
print("Examples:\n  Total: {}".format(total))
print(" CYT: {} ({:.2f}% of total)".format(cyt, 100*cyt/total))
print(" NUC: {} ({:.2f}% of total)".format(nuc, 100*nuc/total))
print(" MIT: {} ({:.2f}% of total)".format(mit, 100*mit/total))
print(" ME3: {} ({:.2f}% of total)".format(me3, 100*me3/total))
print(" ME2: {} ({:.2f}% of total)".format(me2, 100*me2/total))
print(" ME1: {} ({:.2f}% of total)".format(me1, 100*me1/total))
print(" EXC: {} ({:.2f}% of total)".format(exc, 100*exc/total))
print(" VAC: {} ({:.2f}% of total)".format(vac, 100*vac/total))
print(" POX: {} ({:.2f}% of total)".format(pox, 100*pox/total))
print(" ERL: {} ({:.2f}% of total)".format(erl, 100*erl/total))

# Clean, Split, and Normalize the Data
cleaned_df = raw_df.copy()
cleaned_df_1 = raw_df_1.copy()
cleaned_df_2 = raw_df_2.copy()
cleaned_df_3 = raw_df_3.copy()

# remove the unnecessary columns
for x in ["seq_name", "class_code", "z_cyt", "z_nuc", "z_mit", "z_me3", "z_me2", "z_me1", "z_exc", "z_vac", "z_pox", "z_erl"]:
  cleaned_df.pop(x)
  cleaned_df_1.pop(x)
  cleaned_df_2.pop(x)
  cleaned_df_3.pop(x)

train_df = cleaned_df_1
val_df = cleaned_df_2
test_df = cleaned_df_3

# np arrays of labels and features
train_labels = np.array(train_df.pop("classification"))
val_labels = np.array(val_df.pop("classification"))
test_labels = np.array(test_df.pop("classification"))

train_features = np.array(train_df)
val_features = np.array(val_df)
test_features = np.array(test_df)

all_labels = np.concatenate((train_labels, val_labels, test_labels))
all_features = np.concatenate((train_features, val_features, test_features))

# summarize distribution
counter = Counter(train_labels)
for k,v in counter.items():
	per = v / len(train_labels) * 100
	print('Class=%s, n=%d (%.3f%%)' % (k, v, per))
# plot the distribution
pyplot.bar(counter.keys(), counter.values())
pyplot.show()

oversample = SMOTE()
train_features, train_labels = oversample.fit_resample(train_features, train_labels)

train_features.shape

# summarize distribution
counter = Counter(train_labels)
for k,v in counter.items():
	per = v / len(train_labels) * 100
	print('Class=%s, n=%d (%.3f%%)' % (k, v, per))
# plot the distribution
pyplot.bar(counter.keys(), counter.values())
pyplot.show()

# encode class values as integers
encoder = LabelEncoder()
encoder.fit(train_labels)
train_labels = encoder.transform(train_labels)
val_labels = encoder.transform(val_labels)
test_labels = encoder.transform(test_labels)
all_labels = encoder.transform(all_labels)

# convert integers to dummy variables (i.e. one hot encoded)
train_labels = np_utils.to_categorical(train_labels)
val_labels = np_utils.to_categorical(val_labels)
test_labels = np_utils.to_categorical(test_labels)
all_labels = np_utils.to_categorical(all_labels)

# standardize the input features
scaler = StandardScaler()
train_features = scaler.fit_transform(train_features)
val_features = scaler.transform(val_features)
test_features = scaler.transform(test_features)
#print(train_features)

# normalizer = Normalizer()
# train_features = normalizer.fit_transform(train_features)
# val_features = normalizer.transform(val_features)
# test_features = normalizer.transform(test_features)
# print(train_features)

print("Training labels shape:", train_labels.shape)
print("Validation labels shape:", val_labels.shape)
print("Test labels shape:", test_labels.shape)

print("Training features shape:", train_features.shape)
print("Validation features shape:", val_features.shape)
print("Test features shape:", test_features.shape)

# DEFINE THE MODEL AND METRICS

METRICS = [
  keras.metrics.CategoricalAccuracy(name='accuracy'),
  keras.metrics.Precision(name='precision'),
  keras.metrics.Recall(name='recall'),
  keras.metrics.AUC(name='auc'),
  keras.metrics.AUC(name='prc', curve='PR'),
]

def make_model(metrics=METRICS, output_bias=None, optimizer = "adam"):
  if output_bias is not None:
    output_bias = tf.keras.initializers.Constant(output_bias)
  model = keras.Sequential()
  model.add(keras.layers.Dense(12, input_dim=8, activation="relu"))
  model.add(keras.layers.Dense(11, activation="relu"))
  model.add(keras.layers.Dense(10, activation="softmax", bias_initializer=output_bias))

  model.compile(
      optimizer=optimizer,
      loss=keras.losses.CategoricalCrossentropy(),
      metrics=metrics
  )

  return model

# BASELINE MODEL
# Build the model
EPOCHS = 100
BATCH_SIZE = 5

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    verbose=1,
    patience=50,
    mode="min",
    restore_best_weights=True
)

model = make_model()
model.summary()

'''
CYT: 463 (31.20% of total)  - 0.3120
NUC: 429 (28.91% of total)  - 0.2891
MIT: 244 (16.44% of total)  - 0.1644
ME3: 163 (10.98% of total)  - 0.1098
ME2: 51 (3.44% of total)    - 0.0344
ME1: 44 (2.96% of total)    - 0.0296
EXC: 35 (2.36% of total)    - 0.0236
VAC: 30 (2.02% of total)    - 0.0202
POX: 20 (1.35% of total)    - 0.0135
ERL: 5 (0.34% of total)     - 0.0034
'''

initial_bias = [1.5, 1.4, 0.84, 0.41, -0.72, -0.9, -1.1, -1.25, -1.7, -3]

# frequency = [(math.exp(b) / sum([math.exp(c) for c in biases])) for b in biases]
# print(frequency)

# Checkpoint the initial weights

initial_weights = os.path.join(tempfile.mkdtemp(), 'initial_weights')
model.save_weights(initial_weights)

# Train the model

model = make_model()
model.load_weights(initial_weights)
baseline_history = model.fit(
    train_features,
    train_labels,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=(val_features, val_labels))

# Evaluate metrics
train_predictions_baseline = model.predict(train_features)
test_predictions_baseline = model.predict(test_features)

train_predictions_baseline_encoded = train_predictions_baseline.argmax(1)
test_predictions_baseline_encoded = test_predictions_baseline.argmax(1)

train_labels_encoded = train_labels.argmax(1)
test_labels_encoded = test_labels.argmax(1)

def plot_cm(labels, predictions, p=0.5):
  cm = confusion_matrix(labels, predictions)
  plt.figure(figsize=(5,5))
  sns.heatmap(cm, annot=True, fmt="d")
  plt.title('Confusion matrix @{:.2f}'.format(p))
  plt.ylabel('Actual label')
  plt.xlabel('Predicted label')

baseline_results_train = model.evaluate(train_features, train_labels, batch_size=BATCH_SIZE, verbose=0)
for name, value in zip(model.metrics_names, baseline_results_train):
  print(name, ': ', value)
print()

plot_cm(train_labels_encoded, train_predictions_baseline_encoded)

baseline_results = model.evaluate(test_features, test_labels, batch_size=BATCH_SIZE, verbose=0)
for name, value in zip(model.metrics_names, baseline_results):
  print(name, ': ', value)
print()

plot_cm(test_labels_encoded, test_predictions_baseline_encoded)

# weight = model.get_weights()
# np.savetxt('weight.csv' , weight , fmt='%s', delimiter=',')

print(model.get_weights())