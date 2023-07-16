from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Database Models
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    from_location = db.Column(db.String(50))
    to_location = db.Column(db.String(50))
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', backref=db.backref('movements', lazy=True))

# Routes and Views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product = Product(product_id=product_id)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))

    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/update/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        new_product_id = request.form['product_id']
        product.product_id = new_product_id
        db.session.commit()
        return redirect(url_for('products'))

    return render_template('update_product.html', product=product)

@app.route('/products/delete/<product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('products'))

    return render_template('delete_product.html', product=product)

@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        location_id = request.form['location_id']
        location = Location(location_id=location_id)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('locations'))

    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/update/<location_id>', methods=['GET', 'POST'])
def update_location(location_id):
    location = Location.query.get(location_id)
    if request.method == 'POST':
        new_location_id = request.form['location_id']
        location.location_id = new_location_id
        db.session.commit()
        return redirect(url_for('locations'))

    return render_template('update_location.html', location=location)

@app.route('/locations/delete/<location_id>', methods=['GET', 'POST'])
def delete_location(location_id):
    location = Location.query.get(location_id)
    if request.method == 'POST':
        db.session.delete(location)
        db.session.commit()
        return redirect(url_for('locations'))

    return render_template('delete_location.html', location=location)

@app.route('/movements', methods=['GET', 'POST'])
def movements():
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        timestamp_str = request.form['timestamp']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        product_id = request.form['product_id']
        qty = request.form['qty']
        
        # Convert timestamp string to DateTime object
        #timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')

        
        movement = ProductMovement(movement_id=movement_id, timestamp=timestamp,
                                   from_location=from_location, to_location=to_location,
                                   product_id=product_id, qty=qty)
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for('movements'))

    movements = ProductMovement.query.all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/update/<movement_id>', methods=['GET', 'POST'])
def update_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)
    if request.method == 'POST':
        # Update the fields of the movement
        movement.movement_id = request.form['movement_id']
        movement.timestamp = datetime.strptime(request.form['timestamp'], '%Y-%m-%d %H:%M')
        movement.from_location = request.form['from_location']
        movement.to_location = request.form['to_location']
        movement.product_id = request.form['product_id']
        movement.qty = int(request.form['qty'])
        db.session.commit()
        return redirect(url_for('movements'))

    return render_template('update_movement.html', movement=movement)

@app.route('/movements/delete/<movement_id>', methods=['GET', 'POST'])
def delete_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)
    if request.method == 'POST':
        db.session.delete(movement)
        db.session.commit()
        return redirect(url_for('movements'))

    return render_template('delete_movement.html', movement=movement)

@app.route('/report')
def report():
    locations = Location.query.all()
    report_data = []
    for location in locations:
        product_balances = {}
        movements = ProductMovement.query.filter((ProductMovement.to_location == location.location_id) |
                                                 (ProductMovement.from_location == location.location_id)).all()
        for movement in movements:
            if movement.product_id not in product_balances:
                product_balances[movement.product_id] = 0
            if movement.to_location == location.location_id:
                product_balances[movement.product_id] += movement.qty
            else:
                product_balances[movement.product_id] -= movement.qty
        report_data.append({'location': location.location_id, 'balances': product_balances})
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
