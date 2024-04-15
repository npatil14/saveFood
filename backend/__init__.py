import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return pymysql.connections.Connection(
        host="localhost", user="root", password="root0000"
    )


@app.route("/")
def test_endpoint():
    return {"status": 200, "message": "SUCCESS"}


@app.route("/donate-food", methods=["POST"])
def get_food():
    request_body_str = request.data.decode("utf-8")
    request_body_json = json.loads(request_body_str)
    address = request_body_json.get("address", "")
    del request_body_json["address"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for key, value in request_body_json.items():
            food_name = value["foodName"]
            quantity = value["quantity"]
            expiry_date = value["expiryDate"]
            cursor.execute(
                "INSERT INTO scarlet_hawks.FoodInventory (foodName, quantity, expiry_date, address) VALUES(%s, %s, %s, %s);",
                (food_name, int(quantity), expiry_date, address),
            )

        conn.commit()
        cursor.close()
        conn.close()
        return 'Data inserted into the database.'
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/get-food", methods=["GET"])
def distribute_food():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scarlet_hawks.FoodInventory;")
        rows = cursor.fetchall()

        food_items = []
        for row in rows:
            food_items.append({
                "foodName": row[0],
                "quantity": row[1],
                "expiryDate": row[2],
                "address": row[3]
            })

        cursor.close()
        conn.close()
        return jsonify(food_items)
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    app.run()
