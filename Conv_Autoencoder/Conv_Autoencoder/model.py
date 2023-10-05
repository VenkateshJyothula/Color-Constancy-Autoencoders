from keras.layers import Conv2D, Conv2DTranspose, PReLU
from keras.models import Sequential, Model
from keras.applications.vgg16 import VGG16
import numpy as np
import tensorflow as tf
from keras.losses import MeanAbsoluteError
import keras.backend as K
import math

def jaccard_distance(y_true, y_pred, smooth=1e-7):
  intersection = K.sum(K.abs(y_true * y_pred), axis=-1)
  union = K.sum(K.abs(y_true) + K.abs(y_pred), axis=-1) - intersection
  jaccard_score = (intersection + smooth) / (union + smooth)
  jaccard_distance = 1 - jaccard_score
  return jaccard_distance

def cosine_distance(y_true,y_pred):
    loss=[]
    y_true_shaped=tf.reshape(y_true,(-1,256,256,3))
    y_pred_shaped=tf.reshape(y_pred,(-1,256,256,3))
    y_true_vector = tf.reshape(y_true_shaped,[-1])
    y_pred_vector = tf.reshape(y_pred_shaped,[-1])
    sum=tf.math.reduce_sum(y_true_vector*y_pred_vector)
    suma=tf.math.reduce_sum(y_true_vector*y_true_vector)
    sumb=tf.math.reduce_sum(y_pred_vector*y_pred_vector)
    cosine_similarity=0.0
    cosine_similarity=sum
    cosine_similarity=cosine_similarity/tf.math.sqrt(suma)
    cosine_similarity=cosine_similarity/tf.math.sqrt(sumb)
    cosine_distance = 1.0 - cosine_similarity
    loss.append(cosine_distance)
    return tf.convert_to_tensor(loss)


def custom_loss(y_true, y_pred):
  mae_loss = MeanAbsoluteError()(y_true, y_pred)
  jaccard_loss = jaccard_distance(y_true, y_pred)
  cosine_loss = cosine_distance(y_true, y_pred)
  total_loss = mae_loss + jaccard_loss + cosine_loss
  return total_loss


def cosine_angle(y_true, y_pred):
    cosine_angle = tf.acos(1-cosine_distance(y_true,y_pred))
    return cosine_angle*180/math.pi


def create_model(x_train,y_train,epo=1000):
    vggmodel = VGG16()
    newmodel = Sequential()
    #num = 0
    for i, layer in enumerate(vggmodel.layers):
        if i<19:          #Only up to 19th layer to include feature extraction only
          newmodel.add(layer)
    # newmodel.summary()
    for layer in newmodel.layers:
     layer.trainable=False   #We don't want to train these layers again, so False.


    vgg_features = []
    for i, sample in enumerate(x_train):
      sample = sample.reshape((1,224,224,3))
      prediction = newmodel.predict(sample)
      prediction = prediction.reshape((7,7,512))
      vgg_features.append(prediction)
    vgg_features = np.array(vgg_features)


    # Create the decoder part of the model
    decoder = Sequential()
    decoder.add(Conv2DTranspose(256, (3, 3), activation=PReLU(), padding='same', input_shape=(7, 7, 512)))
    decoder.add(Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same'))

    decoder.add(Conv2DTranspose(32, (4, 4), activation=PReLU(), padding='same'))
    decoder.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))

    decoder.add(Conv2DTranspose(32, (5, 5), activation=PReLU(), padding='same'))
    decoder.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))

    decoder.add(Conv2DTranspose(32, (5, 5), activation=PReLU(), padding='same'))
    decoder.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))
    decoder.add(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same'))

    decoder.add(Conv2DTranspose(3, (3, 3), activation='sigmoid', padding='same'))

    decoder.compile(optimizer='adam', loss=custom_loss, metrics=['accuracy','mae',cosine_angle])

    decoder.fit(vgg_features, y_train, epochs=epo, batch_size=32)

    # Connect the encoder (VGG16) and decoder
    encoder_output = newmodel.layers[-1].output
    decoder_output = decoder(encoder_output)

    # Create the complete model
    model = Model(inputs=newmodel.input, outputs=decoder_output)

    return model