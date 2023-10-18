from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Krishna15!'
app.config['MYSQL_DB'] = 'item_management'

mysql = MySQL(app)

# Create the items table if it doesn't exist
with app.app_context():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        CREATE DATABASE IF NOT EXISTS item_management
    ''')
    cursor.execute('''
        USE item_management
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            image_url VARCHAR(255)
        )
    ''')
    cursor.close()
    mysql.connection.commit()

@app.route('/')
def browse_items():
    # Retrieve and display the list of items from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items")
    
    # Fetch the results and convert them to dictionaries
    items = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
    
    cur.close()
    return render_template('browse_items.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form['image_url'][:255]  # Truncate to a maximum of 255 characters

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO items (name, description, image_url) VALUES (%s, %s, %s)",
                    (name, description, image_url))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('browse_items'))
    
    return render_template('add_item.html')


@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form['image_url'][:255]  # Truncate to a maximum of 255 characters

        cur = mysql.connection.cursor()
        cur.execute("UPDATE items SET name = %s, description = %s, image_url = %s WHERE id = %s",
                    (name, description, image_url, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('browse_items'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s", (id,))
    item = cur.fetchone()
    cur.close()

    return render_template('edit_item.html', item=item)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/')

@app.route('/search', methods=['POST'])
def search_item():
    search_query = request.form['search']
    
    # Retrieve items matching the search query by ID or name
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s OR name LIKE %s", (search_query, f'%{search_query}%'))
    
    # Fetch the results and convert them to dictionaries
    items = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
    
    cur.close()
    
    return render_template('search_results.html', items=items)

@app.route('/sort_items', methods=['POST'])
def sort_items():
    sort_by = request.form['sort_by']

    # Retrieve the items from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items")
    items = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]

    # Sort the items based on the selected option
    if sort_by == 'id':
        items.sort(key=lambda x: x['id'])
    elif sort_by == 'name':
        items.sort(key=lambda x: x['name'].lower())  # Sort ignoring case

    cur.close()

    return render_template('browse_items.html', items=items)
                           
if __name__ == '__main__':
    app.run(debug=True)
