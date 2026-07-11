from flask import Flask, jsonify
from flask_cors import CORS
import pyodbc
import os
import struct
from azure.identity import DefaultAzureCredential

app = Flask(__name__)
CORS(app)

# Initialize the Azure Identity provider
credential = DefaultAzureCredential()

def get_connection():
    # CORRECTED: Using the exact, full Azure SQL audience scope
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
    
    # Package the token bytes into the format pyodbc requires
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    
    # Build connection string without UID/PWD secrets
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER', 'sqlserver-service.database.windows.net')};"
        f"DATABASE={os.getenv('DB_NAME', 'SchoolDB')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    
    # Bind the token to attribute 1256 (SQL_CO_ATTR_TOKEN) before connecting
    SQL_CO_ATTR_TOKEN = 1256
    conn = pyodbc.connect(connection_string, attrs_before={SQL_CO_ATTR_TOKEN: token_struct})
    return conn

@app.route('/students')
def students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Age, Grade FROM Students ORDER BY Id")
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

@app.route('/health')
def health():
    return {"status": "Healthy"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
