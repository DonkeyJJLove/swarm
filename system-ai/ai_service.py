from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)
model = joblib.load(os.getenv("MODEL_PATH", "/app/model.joblib"))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    try:
        X = [data['x'], data['y'], data['battery'], data['speed']]
        prediction = model.predict([X])
        return jsonify({'prediction': prediction[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
