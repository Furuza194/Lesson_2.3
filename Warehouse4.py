from flask import Flask, render_template, request, redirect, url_for, flash
import os
import ast

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Filenames for storing data
BALANCE_FILE = "balance.txt"
WAREHOUSE_FILE = "warehouse.txt"
OPERATIONS_FILE = "operations.txt"

def load_data(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = f.read()
                return ast.literal_eval(data)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default
    else:
        return default

def save_data(filename, data):
    try:
        with open(filename, "w") as f:
            f.write(str(data))
    except Exception as e:
        print(f"Error saving {filename}: {e}")

balance = load_data(BALANCE_FILE, 0.0)
warehouse = load_data(WAREHOUSE_FILE, {})
operations = load_data(OPERATIONS_FILE, [])

@app.route("/", methods=["GET", "POST"])
def index():
    global balance, warehouse, operations

    if request.method == "POST":
        form_type = request.form.get("form-type")

        try:
            if form_type == "purchase":
                product = request.form["purchase-name"]
                price = float(request.form["purchase-price"])
                quantity = int(request.form["purchase-quantity"])
                total = price * quantity

                if total > balance:
                    flash("Insufficient funds for this purchase.", "error")
                else:
                    balance -= total
                    if product not in warehouse:
                        warehouse[product] = {"price": price, "quantity": quantity}
                    else:
                        warehouse[product]["quantity"] += quantity
                        warehouse[product]["price"] = price
                    operations.append(f"Purchased {quantity} of {product} at {price} each. Total: {total}")
                    flash("Purchase successful.", "success")

            elif form_type == "sale":
                product = request.form["sale-name"]
                price = float(request.form["sale-price"])
                quantity = int(request.form["sale-quantity"])

                if product not in warehouse or warehouse[product]["quantity"] < quantity:
                    flash("Not enough stock for this sale.", "error")
                else:
                    total = price * quantity
                    balance += total
                    warehouse[product]["quantity"] -= quantity
                    operations.append(f"Sold {quantity} of {product} at {price} each. Total: {total}")
                    flash("Sale successful.", "success")

            elif form_type == "balance":
                operation = request.form["balance-type"]
                amount = float(request.form["balance-amount"])
                if operation == "add":
                    balance += amount
                    operations.append(f"Balance increased by {amount}. New balance: {balance}")
                elif operation == "subtract":
                    balance -= amount
                    operations.append(f"Balance decreased by {amount}. New balance: {balance}")
                flash("Balance updated successfully.", "success")

            save_data(BALANCE_FILE, balance)
            save_data(WAREHOUSE_FILE, warehouse)
            save_data(OPERATIONS_FILE, operations)

        except (ValueError, KeyError) as e:
            flash(f"Invalid input: {e}", "error")

        return redirect(url_for("index"))

    return render_template("index.html", balance=balance, warehouse=warehouse)

@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    global operations

    filtered_operations = operations
    if line_from is not None and line_to is not None:
        line_from = max(0, line_from)
        line_to = min(len(operations), line_to)
        filtered_operations = operations[line_from:line_to]

    return render_template("history.html", operations=filtered_operations)

if __name__ == "__main__":
    app.run(debug=True)
