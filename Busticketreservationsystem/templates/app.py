from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to create the database and tables if they don't exist
def create_tables():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            seats_available INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            bus_id INTEGER,
            num_seats INTEGER,
            FOREIGN KEY (bus_id) REFERENCES buses(id)
        )
    ''')

    conn.commit()
    conn.close()

# Call the function to create tables
create_tables()

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buses')
    buses = cursor.fetchall()
    conn.close()
    return render_template('index.html', buses=buses)

@app.route('/bus/<int:bus_id>')
def show_bus(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
    bus = cursor.fetchone()
    conn.close()
    if not bus:
        return "Bus not found", 404
    return render_template('bus.html', bus=bus)

@app.route('/reserve/<int:bus_id>', methods=['GET', 'POST'])
def reserve(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
    bus = cursor.fetchone()
    if not bus:
        conn.close()
        return "Bus not found", 404
    
    if request.method == 'POST':
        num_seats = int(request.form['seats'])
        if num_seats > bus[2]:
            conn.close()
            return "Not enough seats available", 400
        
        cursor.execute('UPDATE buses SET seats_available = ? WHERE id = ?', (bus[2] - num_seats, bus_id))
        cursor.execute('INSERT INTO reservations (bus_id, num_seats) VALUES (?, ?)', (bus_id, num_seats))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('reserve.html', bus=bus)

@app.route('/reservations')
def show_reservations():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservations')
    reservations = cursor.fetchall()
    conn.close()
    return render_template('reservations.html', reservations=reservations)

@app.route('/bus/add', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        bus_name = request.form['name']
        seats_available = int(request.form['seats_available'])
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO buses (name, seats_available) VALUES (?, ?)', (bus_name, seats_available))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_bus.html')

@app.route('/bus/edit/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
    bus = cursor.fetchone()
    if not bus:
        conn.close()
        return "Bus not found", 404
    
    if request.method == 'POST':
        new_name = request.form['name']
        new_seats_available = int(request.form['seats_available'])
        cursor.execute('UPDATE buses SET name = ?, seats_available = ? WHERE id = ?', (new_name, new_seats_available, bus_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('edit_bus.html', bus=bus)

@app.route('/bus/delete/<int:bus_id>')
def delete_bus(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
