from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os
import pymysql

# Konfigurasi driver MySQL
pymysql.install_as_MySQLdb()

# Load variabel dari file .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql://root:@localhost/penjualan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi database
db = SQLAlchemy(app)

# Model database
class PenjualanCireng(db.Model):
    __tablename__ = "penjualan_cireng"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_pembeli = db.Column(db.String(100), nullable=False)
    rasa_cireng = db.Column(db.String(100), nullable=False)
    tanggal_beli = db.Column(db.Date, nullable=True)
    jumlah_porsi = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nama_pembeli": self.nama_pembeli,
            "rasa_cireng": self.rasa_cireng,
            "tanggal_beli": str(self.tanggal_beli) if self.tanggal_beli else None,
            "jumlah_porsi": self.jumlah_porsi
        }

# Bikin tabel
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/penjualan_cireng', methods=['GET'])
def get_penjualan():
    data = PenjualanCireng.query.all()
    return jsonify([item.to_dict() for item in data])

@app.route('/penjualan_cireng/<int:id>', methods=['GET'])
def get_penjualan_by_id(id):
    item = db.session.get(PenjualanCireng, id)
    if not item:
        return jsonify({"message": "Data penjualan cireng tidak ditemukan"}), 404
    return jsonify(item.to_dict())

@app.route('/penjualan_cireng', methods=['POST'])
def add_penjualan():
    try:
        data = request.get_json()

        if not all(k in data for k in ("nama_pembeli", "rasa_cireng", "tanggal_beli", "jumlah_porsi")):
            return jsonify({"error": "Data tidak lengkap"}), 400
        if not isinstance(data["jumlah_porsi"], int) or data["jumlah_porsi"] <= 0:
            return jsonify({"error": "Jumlah porsi harus angka positif"}), 400

        item = PenjualanCireng(
            nama_pembeli=data["nama_pembeli"],
            rasa_cireng=data["rasa_cireng"],
            tanggal_beli=datetime.strptime(data["tanggal_beli"], "%Y-%m-%d").date() if data["tanggal_beli"] else None,
            jumlah_porsi=data["jumlah_porsi"]
        )

        db.session.add(item)
        db.session.commit()

        return jsonify({"message": "Transaksi cireng berhasil ditambahkan", "data": item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/penjualan_cireng/<int:id>', methods=['PUT'])
def update_penjualan(id):
    item = db.session.get(PenjualanCireng, id)
    if not item:
        return jsonify({"message": "Data penjualan cireng tidak ditemukan"}), 404

    try:
        data = request.get_json()

        if "jumlah_porsi" in data and (not isinstance(data["jumlah_porsi"], int) or data["jumlah_porsi"] <= 0):
            return jsonify({"error": "Jumlah porsi harus angka positif"}), 400

        item.nama_pembeli = data.get("nama_pembeli", item.nama_pembeli)
        item.rasa_cireng = data.get("rasa_cireng", item.rasa_cireng)
        item.tanggal_beli = datetime.strptime(data["tanggal_beli"], "%Y-%m-%d").date() if data.get("tanggal_beli") else item.tanggal_beli
        item.jumlah_porsi = data.get("jumlah_porsi", item.jumlah_porsi)

        db.session.commit()
        return jsonify({"message": "Data penjualan cireng diperbarui", "data": item.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/penjualan_cireng/<int:id>', methods=['DELETE'])
def delete_penjualan(id):
    item = db.session.get(PenjualanCireng, id)
    if not item:
        return jsonify({"message": "Data penjualan cireng tidak ditemukan"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Data penjualan cireng dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == '__main__':
    app.run(debug=True)
