from flask import Flask, request, render_template, jsonify


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", message="Hello, Flask!")

@app.route("/submit_address", methods=["POST"])
def submit_address():
    ethereum_address = request.form.get("ethereum_address")
    
    # Validate the address (basic validation example)
    if ethereum_address and len(ethereum_address) >= 42:
        return jsonify({
            "status": "success",
            "message": f"Successfully processed Ethereum address: {ethereum_address}",
            "address": ethereum_address
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid Ethereum address. Please enter a valid address."
        }), 400

if __name__ == "__main__":
    app.run(debug=True)