from flask import Flask, render_template, request, jsonify
import mariadb
import random

app = Flask(__name__)

try:
    conn = mariadb.connect(
        user="root",
        password="r00t",
        host="127.0.0.1",
        port=3306,
        database="costbiedra"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")

cur = conn.cursor()

@app.route("/")
def index():
    
    cur.execute("SELECT * FROM produkty")
    rows = cur.fetchall()
    random_product = random.choice(rows)
    product_id = random_product[0]
    nazwa = random_product[1]
    cena = float(random_product[2])
    zdjecie = random_product[3]

    
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

   
    cur.execute(f"SELECT * FROM produkty ORDER BY {sort_query}")
    rows = cur.fetchall()
    products = [{"id": row[0], "nazwa": row[1], "cena": float(row[2]), "zdjecie": row[3]} for row in rows]

    return render_template("products.html", title=title, products=products, sort=sort_option)


@app.route("/check_price", methods=["POST"])
def check_price():
    # Obsługa danych z przeglądarki
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