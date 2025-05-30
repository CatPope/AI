# web.py
from flask import Flask, request, jsonify
from src.main import pipeline

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    left_img = request.files["left"]
    right_img = request.files["right"]
    order_json = request.files["order"]
    left_path = "./temp_left.jpg"
    right_path = "./temp_right.jpg"
    order_path = "./temp_order.json"
    left_img.save(left_path)
    right_img.save(right_path)
    order_json.save(order_path)
    result = pipeline(left_path, right_path, order_path)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
