import os
import requests
from flask import Flask, render_template, request as flask_request

app = Flask(__name__)

API_URL = os.environ.get("API_URL", "http://api:8080")


@app.route("/", methods=["GET", "POST"])
def index():
    """Main page - display items and handle form submission."""
    message = None
    message_type = None

    if flask_request.method == "POST":
        nama = flask_request.form.get("nama")
        harga = flask_request.form.get("harga")
        action = flask_request.form.get("action", "add")

        try:
            if action == "add":
                resp = requests.post(
                    f"{API_URL}/barang",
                    json={"nama": nama, "harga": int(harga)},
                    timeout=5,
                )
                if resp.status_code == 201:
                    message = f"Item '{nama}' berhasil ditambahkan!"
                    message_type = "success"
                else:
                    message = f"Gagal menambahkan item: {resp.json().get('error', 'Unknown error')}"
                    message_type = "error"

            elif action == "delete":
                item_id = flask_request.form.get("id")
                resp = requests.delete(f"{API_URL}/barang/{item_id}", timeout=5)
                if resp.status_code == 200:
                    message = "Item berhasil dihapus!"
                    message_type = "success"
                else:
                    message = f"Gagal menghapus item: {resp.json().get('error', 'Unknown error')}"
                    message_type = "error"

            elif action == "update":
                item_id = flask_request.form.get("id")
                resp = requests.put(
                    f"{API_URL}/barang/{item_id}",
                    json={"nama": nama, "harga": int(harga)},
                    timeout=5,
                )
                if resp.status_code == 200:
                    message = f"Item berhasil diupdate!"
                    message_type = "success"
                else:
                    message = f"Gagal mengupdate item: {resp.json().get('error', 'Unknown error')}"
                    message_type = "error"

        except requests.exceptions.ConnectionError:
            message = "Tidak dapat terhubung ke API. Pastikan service berjalan."
            message_type = "error"
        except Exception as e:
            message = f"Error: {str(e)}"
            message_type = "error"

    # Get all items
    items = []
    try:
        resp = requests.get(f"{API_URL}/barang", timeout=5)
        if resp.status_code == 200:
            items = resp.json()
    except Exception:
        pass

    return render_template(
        "index.html",
        items=items,
        message=message,
        message_type=message_type,
        api_url=API_URL,
    )


@app.route("/health")
def health():
    """Health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
