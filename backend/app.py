from flask import Flask, jsonify
from flask_cors import CORS
import pyodbc
import os
import struct
import logging
import base64
import json

from azure.identity import DefaultAzureCredential

app = Flask(__name__)
CORS(app)


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

azure_logger = logging.getLogger("azure.identity")
azure_logger.setLevel(logging.DEBUG)


# Initialize the Azure Identity provider
credential = DefaultAzureCredential()


def get_connection():

    print("\n==============================================")
    print("Getting Azure SQL access token")
    print("==============================================")

    # Get Azure SQL access token
    access_token = credential.get_token(
        "https://database.windows.net/.default"
    ).token

    print("Access token successfully acquired.")

    # ============================================================
    # Decode token claims ONLY for troubleshooting.
    #
    # DO NOT print the actual access token.
    # ============================================================

    try:

        parts = access_token.split(".")

        if len(parts) == 3:

            payload = parts[1]

            # Add required Base64 padding
            payload += "=" * (-len(payload) % 4)

            decoded_payload = base64.urlsafe_b64decode(
                payload
            )

            claims = json.loads(
                decoded_payload
            )

            print("\n==============================================")
            print("TOKEN IDENTITY INFORMATION")
            print("==============================================")

            print(
                "Application / Client ID (appid):",
                claims.get("appid")
            )

            print(
                "Object ID (oid):",
                claims.get("oid")
            )

            print(
                "Tenant ID (tid):",
                claims.get("tid")
            )

            print(
                "Subject (sub):",
                claims.get("sub")
            )

            print(
                "Identity Type (idtyp):",
                claims.get("idtyp")
            )

            print(
                "Token Audience (aud):",
                claims.get("aud")
            )

            print("==============================================\n")

        else:
            print("Unexpected token format.")

    except Exception as e:

        print(
            "Could not decode token claims:",
            str(e)
        )

    # ============================================================
    # Convert token to format required by pyodbc
    # ============================================================

    token_bytes = access_token.encode("utf-16-le")

    token_struct = struct.pack(
        f"<I{len(token_bytes)}s",
        len(token_bytes),
        token_bytes
    )

    # ============================================================
    # Build SQL connection string
    # ============================================================

    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER', 'sqlserver-service.database.windows.net')};"
        f"DATABASE={os.getenv('DB_NAME', 'SchoolDB')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )

    print("SQL Server:", os.getenv(
        "DB_SERVER",
        "sqlserver-service.database.windows.net"
    ))

    print("Database:", os.getenv(
        "DB_NAME",
        "SchoolDB"
    ))

    # ============================================================
    # Connect to Azure SQL using Entra ID access token
    # ============================================================

    SQL_CO_ATTR_TOKEN = 1256

    conn = pyodbc.connect(
        connection_string,
        attrs_before={
            SQL_CO_ATTR_TOKEN: token_struct
        }
    )

    print("Successfully connected to Azure SQL.")
    print("==============================================\n")

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

    return {
        "status": "Healthy"
    }, 200


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )