from flask import Flask, jsonify
from flask_cors import CORS
import pyodbc
import os

app = Flask(__name__)
CORS(app)


def get_connection():

    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER','sqlserver-service')};"
        f"DATABASE={os.getenv('DB_NAME','SchoolDB')};"
        f"UID={os.getenv('DB_USER','sa')};"
        f"PWD={os.getenv('DB_PASSWORD','Password@123')};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )

    return conn


@app.route("/students")
def students():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT Id, Name, Age, Grade
        FROM Students
        ORDER BY Id
    """)

    rows = cursor.fetchall()

    result = []

    for row in rows:

        result.append({
            "id": row.Id,
            "name": row.Name,
            "age": row.Age,
            "grade": row.Grade
        })

    cursor.close()
    conn.close()

    return jsonify(result)


@app.route("/health")
def health():
    return {"status": "Healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)