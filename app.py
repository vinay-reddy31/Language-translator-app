from flask import Flask, render_template, request
import tensorflow as tf
import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import custom_object_scope
from bahdanau_attention import BahdanauAttention
import os
import gdown

app = Flask(__name__)


MODEL_PATH = "translation_model.h5"
MODEL_DRIVE_ID = "1HGAhF4PYPrQdhGMGJMn5do6fHT37QJAI"

# Download model from Google Drive if it doesn't exist
if not os.path.exists(MODEL_PATH):
    print("Model not found, downloading from Google Drive...")
    gdown.download(f"https://drive.google.com/uc?id={MODEL_DRIVE_ID}", MODEL_PATH, quiet=False)
    print("Download completed.")


# Load the model with custom attention layer
model = load_model(MODEL_PATH, custom_objects={'BahdanauAttention': BahdanauAttention}, compile=False)


# Load tokenizers
with open('tokenizer_eng.pkl', 'rb') as f:
    tokenizer_eng = pickle.load(f)

with open('tokenizer_fr.pkl', 'rb') as f:
    tokenizer_fr = pickle.load(f)

# Set max lengths (set based on your preprocessing script)
max_length_eng = 6
max_length_fr = 14

# Translation function
def translate(text):
    # Encode the input
    seq = tokenizer_eng.texts_to_sequences([text.lower()])
    encoder_input = pad_sequences(seq, maxlen=max_length_eng, padding='post')

    # Start decoding
    decoder_input = np.zeros((1, max_length_fr - 1))
    start_token = tokenizer_fr.word_index['<start>']
    decoder_input[0, 0] = start_token

    output = []
    for i in range(1, max_length_fr - 1):
        predictions = model.predict([encoder_input, decoder_input])
        predicted_id = np.argmax(predictions[0][i - 1])
        predicted_word = tokenizer_fr.index_word.get(predicted_id, '')

        if predicted_word == '<end>':
            break

        output.append(predicted_word)
        decoder_input[0, i] = predicted_id

    return ' '.join(output)


# Home Route
@app.route('/', methods=['GET', 'POST'])
def index():
    translation = None
    if request.method == 'POST':
        input_text = request.form['text']
        translation = translate(input_text)

    return render_template('index.html', translation=translation)

# Run server
if __name__ == '__main__':
    app.run(debug=True)
