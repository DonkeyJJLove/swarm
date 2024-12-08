from flask import Flask, request
app = Flask(__name__)

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.json
    print(f"Received from {data['name']}: position {data['x']}, {data['y']}")
    return {"status": "success"}, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
