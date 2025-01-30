from flask import Flask, render_template, request, jsonify, redirect, url_for
from recommendation import recomm
from transformers import BertTokenizer, TFBertForSequenceClassification
import tensorflow as tf
import requests
from bs4 import BeautifulSoup
import numpy as np

MODEL_PATH = "./bert_imdb_model"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = TFBertForSequenceClassification.from_pretrained(MODEL_PATH)

def scrape(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Accept-Language': 'en-US,en;q=0.9',
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    try:
        print(url)
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = soup.find_all('div', class_='ipc-html-content-inner-div')
        reviews = [i.text.strip() for i in reviews]
    except Exception as e:
        print(e)
        return []
    return reviews

def analyze_reviews(reviews):

    inputs = tokenizer(reviews, return_tensors="tf", truncation=True, padding=True, max_length=128)
    outputs = model(**inputs)
    predictions = tf.nn.softmax(outputs.logits, axis=-1).numpy()

    labels = []
    positive_confidences = []
    negative_confidences = []

    for prediction in predictions:
        label = np.argmax(prediction)
        confidence = prediction[label]

        if label == 1: 
            positive_confidences.append(confidence)
            labels.append('positive')
        else:  
            negative_confidences.append(confidence)
            labels.append('negative')

    avg_positive_confidence = np.mean(positive_confidences) if positive_confidences else 0
    avg_negative_confidence = np.mean(negative_confidences) if negative_confidences else 0

    overall_label = 'positive' if avg_positive_confidence > avg_negative_confidence else 'negative'
    overall_confidence = max(avg_positive_confidence, avg_negative_confidence)

    return reviews[:5], labels, overall_label, overall_confidence

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        if movie_name:
            base_url = "https://www.imdb.com/find/?q="
            search_url = base_url + '+'.join(movie_name.split())
            recommended_movies = recomm(search_url)
            return render_template('results.html', movies=recommended_movies)
    return render_template('index.html')

@app.route('/analyze', methods=['GET'])
def analyze():
    href = request.args.get('href')
    if not href:
        return jsonify({'error': 'No href provided'}), 400

    url = 'https://www.imdb.com' + href + 'reviews'
    scraped_reviews = scrape(url)
    if not scraped_reviews:
        return jsonify({'error': 'No reviews found'}), 400

    reviews, labels, overall_label, overall_confidence = analyze_reviews(scraped_reviews)
    print("yo",overall_label)
    return render_template('analyze.html', reviews=reviews, labels=labels, overall_label=overall_label, overall_confidence=overall_confidence)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6900,debug=True)