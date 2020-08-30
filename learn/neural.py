import keras
from tensorflow.keras.layers.experimental.preprocessing import Normalization

def encode_numerical_feature(feature, name, dataset):
    normalizer = Normalization()
    feature_ds = dataset.map(lambda x, y: x[name])
    feature_ds = feature_ds.map(lambda x: tf.expand_dims(x, -1))
    normalizer.adapt(feature_ds)
    encoded_feature = normalizer(feature)

def find_accuracy(df):
    word_mean       = keras.Input(shape=(1,), name="word_mean",       dtype="float64")
    word_stddev     = keras.Input(shape=(1,), name="word_stddev",     dtype="float64")
    sentence_mean   = keras.Input(shape=(1,), name="sentence_mean",   dtype="float64")
    sentence_stddev = keras.Input(shape=(1,), name="sentence_stddev", dtype="float64")
    all_inputs = [word_mean, word_stddev, sentence_mean, sentence_stddev]
