from flask import Flask, request, jsonify
import joblib
from utils import clean_text_pipeline  
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

model_files = {
    'svm': ('/Users/joycendichu/nlp_flask_app/models/svm_model.pkl', '/Users/joycendichu/nlp_flask_app/models/svm_vectorizer.pkl'),
    'naive_bayes': ('/Users/joycendichu/nlp_flask_app/models/naive_bayes_model.pkl', '/Users/joycendichu/nlp_flask_app/models/naive_bayes_vectorizer.pkl'),
    'logistics_regression': ('/Users/joycendichu/nlp_flask_app/models/log_reg_model.pkl', '/Users/joycendichu/nlp_flask_app/models/log_reg_vectorizer.pkl'),
}

models = {}
vectorizers = {}

for model_name, (model_path, vectorizer_path) in model_files.items():
    models[model_name] = joblib.load(model_path)
    vectorizers[model_name] = joblib.load(vectorizer_path)
    print(f"{model_name} model and vectorizer loaded.")

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    data = request.get_json()
    review = data['review']
    
    cleaned_review, adjectives_adverbs = clean_text_pipeline(review)

    best_model = None
    best_prediction = None
    highest_confidence = -1  

    for model_name, model in models.items():
        print(f"Using model: {model_name}")
        vectorizer = vectorizers[model_name]
        review_vector = vectorizer.transform([cleaned_review])

        if hasattr(model, 'predict_proba'):
            prediction_probabilities = model.predict_proba(review_vector)
            confidence = max(prediction_probabilities[0])
            prediction = model.predict(review_vector)
            print(f"$$$$$$$$$$$$$${prediction_probabilities}:::::::{confidence}::::{prediction}@@@@@@@@@@")
        else:
            prediction = model.predict(review_vector)
            confidence = 1  

        if confidence > highest_confidence:
            highest_confidence = confidence
            best_model = model_name
            best_prediction = prediction[0]

    return jsonify({
        "sentiment": best_prediction,
        "model": best_model,
        "confidence": highest_confidence,
        "adjectives_adverbs": adjectives_adverbs  
    })


if __name__ == '__main__':
    app.run(debug=True, port=7070)
