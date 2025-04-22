from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

#inventory storage
inventory = {}

@app.route('/')
def index():
    return render_template('index.html', inventory=inventory)

@app.route('/add', methods=['POST'])
def add():
    item = request.form['item'].strip()
    quantity = request.form['quantity'].strip()
    if item and quantity.isdigit():
        quantity = int(quantity)
        if item in inventory:
            inventory[item] += quantity
        else:
            inventory[item] = quantity
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    item = request.form['update_item'].strip()
    quantity = request.form['update_quantity'].strip()
    if item in inventory and quantity.isdigit():
        inventory[item] = int(quantity)
    return redirect(url_for('index'))

@app.route('/remove/<item>')
def remove(item):
    inventory.pop(item, None)
    return redirect(url_for('index'))

@app.route('/low_stock', methods=['POST'])
def low_stock():
    threshold = request.form['threshold'].strip()
    if threshold.isdigit():
        threshold = int(threshold)
        low_items = {item: qty for item, qty in inventory.items() if qty < threshold}
        return render_template('index.html', inventory=inventory, low_items=low_items)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000)
