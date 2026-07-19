import os
import time
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "dbname": os.environ.get("DB_NAME", "barangdb"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
}


def get_db_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(**DB_CONFIG)


def init_database():
    """Initialize database with retry logic."""
    max_retries = 30
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS barang (
                    id SERIAL PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL,
                    harga INTEGER NOT NULL
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully.")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Database connection failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("Failed to connect to database after all retries.")
                raise


# Initialize database on startup
init_database()


@app.route("/barang", methods=["GET"])
def get_all_barang():
    """Get all items."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM barang ORDER BY id;")
        items = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/barang/<int:id>", methods=["GET"])
def get_barang(id):
    """Get item by ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM barang WHERE id = %s;", (id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
        if item:
            return jsonify(item), 200
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/barang", methods=["POST"])
def create_barang():
    """Create a new item."""
    try:
        data = request.get_json()
        nama = data.get("nama")
        harga = data.get("harga")

        if not nama or not harga:
            return jsonify({"error": "Field 'nama' and 'harga' are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "INSERT INTO barang (nama, harga) VALUES (%s, %s) RETURNING *;",
            (nama, harga),
        )
        new_item = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/barang/<int:id>", methods=["PUT"])
def update_barang(id):
    """Update an existing item."""
    try:
        data = request.get_json()
        nama = data.get("nama")
        harga = data.get("harga")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if item exists
        cur.execute("SELECT * FROM barang WHERE id = %s;", (id,))
        existing = cur.fetchone()
        if not existing:
            cur.close()
            conn.close()
            return jsonify({"error": "Item not found"}), 404

        cur.execute(
            "UPDATE barang SET nama = %s, harga = %s WHERE id = %s RETURNING *;",
            (nama, harga, id),
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(updated), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/barang/<int:id>", methods=["DELETE"])
def delete_barang(id):
    """Delete an item."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if item exists
        cur.execute("SELECT * FROM barang WHERE id = %s;", (id,))
        existing = cur.fetchone()
        if not existing:
            cur.close()
            conn.close()
            return jsonify({"error": "Item not found"}), 404

        cur.execute("DELETE FROM barang WHERE id = %s;", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
