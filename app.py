from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import datetime 
import mariadb
import random

app = Flask(__name__)
app.secret_key = 'rabarbar_123_super_tajny'
try:
    conn = mariadb.connect(
        user="root",
        password="r00t",
        host="127.0.0.1",
        port=3306,
        database="costbiedra"
    )
except mariadb.Error as blad:
    print(f"Błąd w połączeniu z bazą danych: {blad}")

cur = conn.cursor()

@app.route("/")
def index():
    
    cur.execute("SELECT * FROM produkty")
    rows = cur.fetchall()
    today = datetime.date.today().toordinal()
    index = today % len(rows)
    selected_product = rows[index]

    product_id = selected_product[0]
    nazwa = selected_product[1]
    cena = float(selected_product[2])
    zdjecie = selected_product[3]

    
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur.execute("SELECT id, password, is_admin FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user and user[1] == password:
            session['user_id'] = user[0]
            session['is_admin'] = user[2]
            return redirect(url_for('dodaj_produkt'))
        else:
            return render_template('login.html', error="Nieprawidłowy login lub hasło")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# DODAWANIE PRODUKTÓW
@app.route('/admin/dodaj-produkt', methods=['GET', 'POST'])
def dodaj_produkt():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nazwa = request.form['nazwa']
        cena = request.form['cena']
        obraz = request.files['obraz']

        #Sprawdzenie czy produkt jest w bazie
        cur.execute("SELECT id FROM produkty WHERE Nazwa = ?", (nazwa,))
        existing = cur.fetchone()

        if existing:
            return render_template('dodaj_produkt.html', error="Produkt o tej nazwie jest już w bazie")

        # zapisz obrazek
        filename = obraz.filename
        filepath = os.path.join('static/images/products', filename)
        obraz.save(filepath)

        cur.execute("INSERT INTO produkty (Nazwa, Cena, Obrazek) VALUES (?, ?, ?)", (nazwa, cena, filename))
        conn.commit()

        return redirect(url_for('dodaj_produkt'))

    return render_template('dodaj_produkt.html')
