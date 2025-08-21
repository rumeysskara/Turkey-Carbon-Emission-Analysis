#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu Web Arayüzü
--------------------------------------------------------
Bu uygulama, sürdürülebilir tedarik zinciri optimizasyonu için
basit bir web arayüzü sağlar.
"""

import json
import os
from flask import Flask, render_template, request, jsonify

# API modülünü içe aktar (opsiyonel)
try:
    from apis import SupplyChainOptimizer
    optimizer = SupplyChainOptimizer()
except ImportError:
    print("APIs modülü bulunamadı, sadece static sayfalar çalışacak")
    optimizer = None

app = Flask(__name__, 
            template_folder="../templates",
            static_folder="../static")


@app.route("/")
def index():
    """Ana sayfa"""
    return render_template("index.html")


@app.route("/factory-emissions")
def factory_emissions():
    """Fabrika emisyonları sayfası"""
    return render_template("factory_emissions.html")


@app.route("/all-turkey-emissions")
def all_turkey_emissions():
    """Tüm Türkiye fabrika emisyonları sayfası"""
    return render_template("all_turkey_emissions.html")


@app.route("/carbon-predictions")
def carbon_predictions():
    """Karbon emisyonu tahminleri ve GPT analizi sayfası"""
    return render_template("carbon_predictions.html")




@app.route("/emission-scenarios")
def emission_scenarios():
    """Karbon emisyonu gelecek senaryoları sayfası"""
    return render_template("emission_scenarios.html")


@app.route("/optimize-routes", methods=["POST"])
def optimize_routes():
    """Rotaları optimize et"""
    data = request.get_json()
    
    if not data or "origin" not in data or "destinations" not in data:
        return jsonify({"error": "Geçersiz istek. 'origin' ve 'destinations' gerekli."}), 400
    
    origin = data["origin"]
    destinations = data["destinations"]
    
    if not isinstance(destinations, list):
        return jsonify({"error": "'destinations' bir liste olmalıdır."}), 400
    
    results = optimizer.optimize_routes(origin, destinations)
    return jsonify(results)


@app.route("/find-suppliers", methods=["POST"])
def find_suppliers():
    """Sürdürülebilir tedarikçileri bul"""
    data = request.get_json()
    
    if not data or "product_type" not in data or "location" not in data:
        return jsonify({"error": "Geçersiz istek. 'product_type' ve 'location' gerekli."}), 400
    
    product_type = data["product_type"]
    location = data["location"]
    max_distance = float(data.get("max_distance", 50.0))
    
    results = optimizer.find_sustainable_suppliers(product_type, location, max_distance)
    return jsonify(results)


@app.route("/analyze-impact", methods=["POST"])
def analyze_impact():
    """Çevresel etki analizi yap"""
    data = request.get_json()
    
    if not data or "routes" not in data or "suppliers" not in data:
        return jsonify({"error": "Geçersiz istek. 'routes' ve 'suppliers' gerekli."}), 400
    
    routes = data["routes"]
    suppliers = data["suppliers"]
    
    if not isinstance(routes, list) or not isinstance(suppliers, list):
        return jsonify({"error": "'routes' ve 'suppliers' listeler olmalıdır."}), 400
    
    results = optimizer.calculate_environmental_impact(routes, suppliers)
    return jsonify(results)


@app.route("/test")
def test_page():
    """Test sayfası"""
    return render_template("test.html")


@app.route("/carbon-predictions-simple")
def carbon_predictions_simple():
    """Basit emisyon tahminleri sayfası"""
    return render_template("carbon_predictions_simple.html")


@app.route("/debug-json")
def debug_json():
    """JSON dosyalarının durumunu kontrol et"""
    import os
    json_files = [
        'static/data/carbon_predictions.json',
        'static/data/gpt_sustainability_report.json', 
        'static/data/model_performance.json',
        'static/data/all_turkey_factory_emissions.json'
    ]
    
    results = {}
    for file_path in json_files:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results[file_path] = {
                        'exists': True,
                        'size': len(str(data)),
                        'keys': list(data.keys()) if isinstance(data, dict) else 'not_dict'
                    }
            else:
                results[file_path] = {'exists': False, 'error': 'File not found'}
        except Exception as e:
            results[file_path] = {'exists': False, 'error': str(e)}
    
    return jsonify(results)


if __name__ == "__main__":
    # templates ve static klasörlerinin varlığını kontrol et
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"'{templates_dir}' klasörü oluşturuldu.")
    
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"'{static_dir}' klasörü oluşturuldu.")
    
    # Uygulama ayarları
    debug = True
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 8080))
    
    print(f"Web arayüzü http://{host}:{port} adresinde çalışıyor...")
    app.run(debug=debug, host=host, port=port)
