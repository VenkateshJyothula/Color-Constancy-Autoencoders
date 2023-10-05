# -*- coding: utf-8 -*-
"""...

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18WQBnBrrhxEbgDgWzqoEqe9RGCgkt2I0
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Conv2D,Input,UpSampling2D,MaxPooling2D,Dropout,Conv2DTranspose
from tensorflow.keras import Sequential
from matplotlib import image as img,pyplot as plt
from tqdm import tqdm
import cv2
import os
from keras import backend as K
from google.colab.patches import cv2_imshow


#-----------------------------------Cosine Loss-----------------------------------------------------------
def Cosine_Loss_Function(y_true,y_pred):
    loss=[]
    y_true_shaped=tf.reshape(y_true,(-1,256,256,3))
    y_pred_shaped=tf.reshape(y_pred,(-1,256,256,3))
    for i in range(len(y_true_shaped)):
      y_true_vector = tf.reshape(y_true_shaped[i],[-1])
      y_pred_vector = tf.reshape(y_pred_shaped[i],[-1])
      sum=tf.math.reduce_sum(y_true_vector*y_pred_vector)
      suma=tf.math.reduce_sum(y_true_vector*y_true_vector)
      sumb=tf.math.reduce_sum(y_pred_vector*y_pred_vector)
      cosine_similarity=0.0
      cosine_similarity=sum
      cosine_similarity=cosine_similarity/tf.math.sqrt(suma)
      cosine_similarity=cosine_similarity/tf.math.sqrt(sumb)
      cosine_distance = 1.0 - cosine_similarity
      loss.append(cosine_distance)
      if cosine_distance<0:
        tf.print("False")
    return tf.convert_to_tensor(loss)

#----------------------------------------Pearson Loss Function--------------------------------------------------------------
def Pearson_Loss_Function(y_true,y_pred):
    loss=[]
    y_true_shaped=tf.reshape(y_true,(-1,256,256,3))
    y_pred_shaped=tf.reshape(y_pred,(-1,256,256,3))
    for i in range(len(y_true_shaped)):
      y_true_i=y_true_shaped[i]
      y_pred_i=y_pred_shaped[i]
      y_true_reshaped=tf.reshape(y_true_i,[-1])
      y_pred_reshaped=tf.reshape(y_pred_i,[-1])
      y_true_ripple=y_true_reshaped-tf.math.reduce_mean(y_true_reshaped)
      y_pred_ripple=y_pred_reshaped-tf.math.reduce_mean(y_pred_reshaped)
      sum=tf.math.reduce_sum(y_true_ripple*y_pred_ripple)
      suma=tf.math.reduce_sum(y_true_ripple*y_true_ripple)
      sumb=tf.math.reduce_sum(y_pred_ripple*y_pred_ripple)
      pearson_similarity=0.0
      pearson_similarity=sum
      pearson_similarity=pearson_similarity/tf.math.sqrt(suma)
      pearson_similarity=pearson_similarity/tf.math.sqrt(sumb)
      pearson_distance = 1.0 - pearson_similarity
      loss.append(pearson_distance)
    return tf.convert_to_tensor(loss)

input_shape=(256,256,3)

model = Sequential()

# Encoder
model.add(Conv2D(32, (5, 5), activation='relu', padding='same', input_shape=input_shape))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Conv2D(32, (5, 5), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Conv2D(32, (4, 4), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Conv2D(256, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

# Middle Layer
model.add(Conv2D(50, (3, 3), activation='relu', padding='same'))

# Decoder
model.add(Dropout(0.2))
model.add(Conv2DTranspose(256, (3, 3), activation='relu', padding='same'))
model.add(Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same'))

model.add(Conv2DTranspose(32, (4, 4), activation='relu', padding='same'))
model.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))

model.add(Conv2DTranspose(32, (5, 5), activation='relu', padding='same'))
model.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))

model.add(Conv2DTranspose(32, (5, 5), activation='relu', padding='same'))
model.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))

model.add(Conv2DTranspose(3, (3, 3), activation='sigmoid', padding='same'))
model.compile(optimizer='adam',loss=Cosine_Loss_Function,metrics=['accuracy'])
model.summary()

