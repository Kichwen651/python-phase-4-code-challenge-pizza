#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# Routes
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    response = [restaurant.to_dict() for restaurant in restaurants]
    return jsonify(response), 200


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        response = restaurant.to_dict(include=["restaurant_pizzas", "restaurant_pizzas.pizza"])
        return jsonify(response), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    response = [pizza.to_dict() for pizza in pizzas]
    return jsonify(response), 200


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    # Validation logic for 'price'
    price = data.get('price')
    if price is None or price < 1 or price > 30:
        return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

    try:
        # Create the RestaurantPizza object
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )

        # Add to the session and commit
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Return the created restaurant pizza with the related restaurant and pizza data
        return jsonify(restaurant_pizza.to_dict(include=["restaurant", "pizza"])), 201

    except KeyError as e:
        # Handle missing keys
        return jsonify({"errors": [f"Missing required field: {str(e)}"]}), 400

    except Exception as e:
        # Return a general exception error if something goes wrong
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
