from flask import Flask, render_template, request, jsonify
import sqlite3
import random

app = Flask(__name__)

# Funkcja do łączenia z bazą danych
def get_db_connection():
    conn = sqlite3.connect('produkty.db')
    conn.row_factory = sqlite3.Row  # pozwala traktować wyniki jak słowniki
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produkty")
    rows = cur.fetchall()
    conn.close()

    random_product = random.choice(rows)
    product_id = random_product["id"]
    nazwa = random_product["nazwa"]
    cena = float(random_product["cena"])
    zdjecie = random_product["obrazek"]

    title = "Biedrondle"
    return render_template("index.html", title=title, product_id=product_id, nazwa=nazwa, cena=cena, zdjecie=zdjecie)

@app.route('/about')
def about():
    title = "Biedrondle | O mnie"
    return render_template("about.html", title=title)

@app.route('/products')
def products():
    title = "Biedrondle | Produkty"
    sort_option = request.args.get('sort', 'name_asc')

    sort_query = "nazwa ASC"
    if sort_option == 'name_asc':
        sort_query = "nazwa ASC"
    elif sort_option == 'name_desc':
        sort_query = "nazwa DESC"
    elif sort_option == 'price_asc':
        sort_query = "cena ASC"
    elif sort_option == 'price_desc':
        sort_query = "cena DESC"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM produkty ORDER BY {sort_query}")
    rows = cur.fetchall()
    conn.close()

    products = [{"id": row["id"], "nazwa": row["nazwa"], "cena": float(row["cena"]), "zdjecie": row["obrazek"]} for row in rows]

    return render_template("products.html", title=title, products=products, sort=sort_option)

@app.route("/check_price", methods=["POST"])
def check_price():
    data = request.json
    user_price = float(data["price"])
    correct_price = float(data["correct_price"])
    remaining_tries = int(data["remaining_tries"])

    difference = abs(user_price - correct_price)
    direction = "down" if user_price > correct_price else "up"

    game_status = "playing"
    if difference < 0.10:
        game_status = "win"
    elif remaining_tries <= 1:
        game_status = "lose"

    return jsonify({
        "difference": difference,
        "direction": direction,
        "game_status": game_status,
        "remaining_tries": max(remaining_tries - 1, 0)
    })
    
@app.route('/login')
def login():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
