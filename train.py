from flask import Flask, request, jsonify
from transformers import BertTokenizer, TFBertForSequenceClassification
import tensorflow as tf
from youtube_transcript_api import YouTubeTranscriptApi
import re


app = Flask(__name__)

# Load the saved BERT model and tokenizer
MODEL_PATH = "./bert_imdb_model"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = TFBertForSequenceClassification.from_pretrained(MODEL_PATH)

def extract_video_id(url):
    pattern = r"(?:v=|be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return -1

# Define the prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No text provided'}), 400
    video_id=extract_video_id(url)
    if video_id==-1:
        return jsonify({'error':'Invalid URL'})
    else:
        d=YouTubeTranscriptApi.get_transcript(video_id)
        trans=''
        for i in d:
            trans+=i["text"]
    
        inputs = tokenizer(trans, return_tensors="tf", truncation=True, padding='max_length', max_length=128)
        
        # Perform prediction
        outputs = model(**inputs)
        predictions = tf.nn.softmax(outputs.logits, axis=-1)
        label = tf.argmax(predictions, axis=1).numpy()[0]
        confidence = predictions.numpy()[0][label]
        
        return jsonify({
            'label': 'positive' if label == 1 else 'negative',
            'confidence': float(confidence)
        })

if __name__ == '__main__':
    app.run()