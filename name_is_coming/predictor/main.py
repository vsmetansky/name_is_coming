import os
import datetime
import io
from io import StringIO
import IPython
import IPython.display
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from keras.layers import Input
from keras.models import Model
from keras.layers.core import Dense, Activation
from keras.layers.recurrent import SimpleRNN
import plotly.graph_objects as go

plt.style.use('dark_background')
val_performance = {}
performance = {}

MAX_EPOCHS = 100

def compile_and_fit(model, window, patience=1):
  early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=patience,
                                                    mode='min')

  model.compile(loss=tf.losses.MeanSquaredError(),
                optimizer=tf.optimizers.Adam(),
                metrics=[tf.metrics.MeanAbsoluteError()])

  history = model.fit(window.train, batch_size=1, epochs=MAX_EPOCHS,
                      validation_data=window.val,
                      callbacks=None)
  return history

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False


df = pd.read_csv(("/Users/inepp/name_is_coming/predictor/ml_data_gen/debris_loc.csv"))
df = pd.DataFrame(df)
df = df.drop(columns=df.columns[0])

df = df.T
df.columns =['Name', 'Latitude', 'Longitude', 'Altitude', "v1", "v2", "v3", 'Time', "b_lat", "b_lon", "b_h"]
print(df.head())


df['Latitude'] = df['Latitude'].astype(float)
df['Longitude'] = df['Longitude'].astype(float)
df['Altitude'] = df['Altitude'].astype(float)
df['v1'] = df['v1'].astype(float)
df['v2'] = df['v2'].astype(float)
df['v3'] = df['v3'].astype(float)
date_time = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')


cosmos_dt = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
plot_cols = ['Latitude', 'Longitude', 'Altitude']
plot_features = df[plot_cols]

df =  df[["Latitude", 'Longitude', 'Altitude', 'v1', 'v2', 'v3']]

column_indices = {name: i for i, name in enumerate(df.columns)}

n = len(df)
print(len(df))
train_df = df[:120]
val_df = df[120:140]
test_df = df[140:149]
num_features = df.shape[1]

print(len(train_df))
print(len(val_df))
print(len(test_df))

train_mean = train_df.mean()
train_std = train_df.std()

train_df = (train_df - train_mean) / train_std
val_df = (val_df - train_mean) / train_std
test_df = (test_df - train_mean) / train_std

df_std = (df - train_mean) / train_std
df_std = df_std.melt(var_name='Column', value_name='Normalized')
plt.figure(figsize=(12, 6))


class WindowGenerator():
  def __init__(self, input_width, label_width, shift,
               train_df=train_df, val_df=val_df, test_df=test_df,
               label_columns=None):

    self.train_df = train_df
    self.val_df = val_df
    self.test_df = test_df

    self.label_columns = label_columns
    if label_columns is not None:
      self.label_columns_indices = {name: i for i, name in
                                    enumerate(label_columns)}
    self.column_indices = {name: i for i, name in
                           enumerate(train_df.columns)}


    self.input_width = input_width
    self.label_width = label_width
    self.shift = shift

    self.total_window_size = input_width + shift

    self.input_slice = slice(0, input_width)
    self.input_indices = np.arange(self.total_window_size)[self.input_slice]

    self.label_start = self.total_window_size - self.label_width
    self.labels_slice = slice(self.label_start, None)
    self.label_indices = np.arange(self.total_window_size)[self.labels_slice]

  def __repr__(self):
    return '\n'.join([
        f'Total window size: {self.total_window_size}',
        f'Input indices: {self.input_indices}',
        f'Label indices: {self.label_indices}',
        f'Label column name(s): {self.label_columns}'])



def split_window(self, features):
  inputs = features[:, self.input_slice, :]
  labels = features[:, self.labels_slice, :]
  if self.label_columns is not None:
    labels = tf.stack(
        [labels[:, :, self.column_indices[name]] for name in self.label_columns],
        axis=-1)

  inputs.set_shape([None, self.input_width, None])
  labels.set_shape([None, self.label_width, None])

  return inputs, labels

WindowGenerator.split_window = split_window

def plot(self, model=None, plot_col='Altitude', max_subplots=3):
  inputs, labels = self.example
  plt.figure(figsize=(12, 8))
  plot_col_index = self.column_indices[plot_col]
  max_n = min(max_subplots, len(inputs))
  for n in range(max_n):
    plt.subplot(max_n, 1, n+1)
    plt.ylabel(f'{plot_col} (Normalized])')
    plt.plot(self.input_indices, inputs[n, :, plot_col_index],
             label='Input data', c='white', marker='.', lw = 2, zorder=-10)

    if self.label_columns:
      label_col_index = self.label_columns_indices.get(plot_col, None)
    else:
      label_col_index = plot_col_index

    if label_col_index is None:
      continue

    plt.scatter(self.label_indices, labels[n, :, label_col_index],
                edgecolors='k', label='Target', c='white', s=64)
    if model is not None:
      predictions = model(inputs)

      plt.scatter(self.label_indices, predictions[n, :, label_col_index],
                  marker='x', label='Prediction',
                  c='#2CA02C', s=64)
      data_glob[0].append(self.label_indices)
      data_glob[1].append(predictions[n, :, label_col_index])


    if n == 0:
      plt.legend()


  plt.xlabel('Time [days]')

WindowGenerator.plot = plot

def make_dataset(self, data):
  data = np.array(data, dtype=np.float32)
  ds = tf.keras.preprocessing.timeseries_dataset_from_array(
      data=data,
      targets=None,
      sequence_length=self.total_window_size,
      sequence_stride=1,
      shuffle=False,
      batch_size=2)

  ds = ds.map(self.split_window)

  return ds

WindowGenerator.make_dataset = make_dataset


@property
def train(self):
  return self.make_dataset(self.train_df)

@property
def val(self):
  return self.make_dataset(self.val_df)

@property
def test(self):
  return self.make_dataset(self.test_df)

@property
def example(self):
  result = getattr(self, '_example', None)
  try:
      result = next(iter(self.train))
      self._example = result

  except StopIteration:
      pass

  return result

WindowGenerator.train = train
WindowGenerator.val = val
WindowGenerator.test = test
WindowGenerator.example = example


wide_window = WindowGenerator(
    input_width=10, label_width=10, shift=1,
    label_columns=["Latitude"])



lstm_model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(32, return_sequences=True),
    tf.keras.layers.Dense(units=1)
])


history = compile_and_fit(lstm_model, wide_window)
wide_window.plot(lstm_model, plot_col = "Latitude")
fig.show()
