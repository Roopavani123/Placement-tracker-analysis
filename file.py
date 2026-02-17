from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from collections import Counter

app = Flask(__name__)

FILE = "placement_data.csv"

# Load or create CSV
if os.path.exists(FILE):
    df = pd.read_csv(FILE, on_bad_lines="skip")
else:
    df = pd.DataFrame(columns=["Name", "Department", "Company", "Package", "Status"])
    df.to_csv(FILE, index=False)

@app.route("/", methods=["GET"])
def home():
    global df

    # Search by name
    search_name = request.args.get("name", "").strip()

    if search_name:
        filtered_df = df[df["Name"].str.contains(search_name, case=False, na=False)]
        message = "✅ Student Found" if not filtered_df.empty else "❌ Student Not Found"
    else:
        filtered_df = df
        message = ""

    # Dashboard stats (overall)
    total = len(df)
    placed_df = df[df["Status"] == "Placed"]
    placed = len(placed_df)
    not_placed = total - placed
    percentage = round((placed / total) * 100, 2) if total > 0 else 0

    # Charts data (from placed students)
    company_chart = dict(Counter(placed_df["Company"]))
    dept_chart = dict(Counter(placed_df["Department"]))

    return render_template(
        "index.html",
        students=filtered_df.to_dict(orient="records"),
        total=total,
        placed=placed,
        not_placed=not_placed,
        percentage=percentage,
        search_name=search_name,
        message=message,
        company_chart=company_chart,
        dept_chart=dept_chart
    )

@app.route("/add", methods=["POST"])
def add_student():
    global df

    new_data = {
        "Name": request.form["name"],
        "Department": request.form["department"],
        "Company": request.form["company"].replace(",", ""),
        "Package": float(request.form["package"]),
        "Status": request.form["status"]
    }

    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(FILE, index=False)

    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete_student():
    global df

    name = request.form["name"]
    df = df[df["Name"] != name]
    df.to_csv(FILE, index=False)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


