from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'dharun2305'

# Google Generative AI API setup
api_key = os.getenv("GENAI_API_KEY", 'AIzaSyBvLns6edyYX3Ak0ceoFSKph-AKgWW6bAk')
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 150,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", 
    generation_config=generation_config,
)


chat_session = model.start_chat(history=[])

@app.route("/")
def welcome():
    return render_template("index.html")
@app.route('/customer',methods=['GET','POST'])
def customer():
    return render_template("customer.html")

@app.route('/owner', methods=['POST', 'GET'])
def owner():
    if request.method == 'POST':
        product_name = request.form['product_name']
        base_price = int(request.form['base_price'])
        min_price = int(request.form['min_price'])

        session['product_name'] = product_name
        session['base_price'] = base_price
        session['min_price'] = min_price
        session['current_price'] = base_price 

        return redirect(url_for('owner_confirmation'))

    return render_template('owner.html') 

@app.route('/owner_confirmation',methods=['GET','POST'])
def owner_confirmation():
    product_name = session.get('product_name')
    base_price = session.get('base_price')
    min_price = session.get('min_price')

    return render_template('owner_confirmation.html', product_name=product_name, base_price=base_price, min_price=min_price)

@app.route('/negotiate', methods=['POST','GET'])
def negotiate():
    data = request.json
    user_message = data.get('user_message', '').strip()

    product = session.get('product_name', 'Product')
    base_price = session.get('base_price', 0)
    min_price = session.get('min_price', 0)


    if user_message.lower() == 'exit':
        return jsonify({"message": "Ending negotiation. Goodbye!"})

    formatted_input = (
        f"You are negotiating the price of a {product} with a customer. "
        f"The base price is ${base_price} and the minimum price is ${min_price}. "
        f"Customer says: {user_message}. "
        "Respond accordingly without revealing the minimum price, behave like a shopkeeper, "
        "and never sell below the minimum price. Give a precise answer without being too lengthy."
    )

    try:
        print("Connecting to chatbot...")
        response = chat_session.send_message(formatted_input)
        session['current_price'] = base_price 
        return jsonify({"bot_response": response.text, "current_price": session['current_price']})
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route('/confirm_deal', methods=['POST','GET'])
def confirm_deal():
    current_price = session.get('current_price', 0)

    
    def analyze_sentiment(message):
        return 70 if "good" in message.lower() else 10 

    def calculate_discount(sentiment_score):
        return sentiment_score 

    final_discount = calculate_discount(analyze_sentiment("confirm deal"))
    final_price_with_discount = current_price * (1 - final_discount / 100)

    return jsonify({
        "final_price": final_price_with_discount,
        "discount": final_discount
    })

if __name__ == '__main__':
    app.run(debug=True)
