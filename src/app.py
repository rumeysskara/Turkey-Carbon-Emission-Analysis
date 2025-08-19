#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu Uygulaması
-------------------------------------------------------
Bu uygulama, sürdürülebilir tedarik zinciri optimizasyonu için
bir komut satırı arayüzü sağlar.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any

# API modülünü içe aktar
from apis import SupplyChainOptimizer


def parse_args():
    """Komut satırı argümanlarını ayrıştırır"""
    parser = argparse.ArgumentParser(
        description="Sürdürülebilir Tedarik Zinciri Optimizasyonu"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Komut")
    
    # Rota optimizasyonu komutu
    route_parser = subparsers.add_parser("optimize-routes", help="Rotaları optimize et")
    route_parser.add_argument("--origin", required=True, help="Başlangıç adresi")
    route_parser.add_argument("--destinations", required=True, nargs="+", help="Varış adresleri")
    route_parser.add_argument("--output", help="Sonuçların kaydedileceği dosya yolu")
    
    # Tedarikçi bulma komutu
    supplier_parser = subparsers.add_parser("find-suppliers", help="Sürdürülebilir tedarikçileri bul")
    supplier_parser.add_argument("--product-type", required=True, help="Ürün tipi")
    supplier_parser.add_argument("--location", required=True, help="Konum adresi")
    supplier_parser.add_argument("--max-distance", type=float, default=50.0, help="Maksimum mesafe (km)")
    supplier_parser.add_argument("--output", help="Sonuçların kaydedileceği dosya yolu")
    
    # Çevresel etki analizi komutu
    impact_parser = subparsers.add_parser("analyze-impact", help="Çevresel etki analizi yap")
    impact_parser.add_argument("--routes-file", required=True, help="Rota verilerini içeren JSON dosyası")
    impact_parser.add_argument("--suppliers-file", required=True, help="Tedarikçi verilerini içeren JSON dosyası")
    impact_parser.add_argument("--output", help="Sonuçların kaydedileceği dosya yolu")
    
    return parser.parse_args()


def save_results(results: Dict, output_path: str = None) -> None:
    """
    Sonuçları dosyaya kaydeder veya ekrana yazdırır
    
    Args:
        results: Kaydedilecek sonuçlar
        output_path: Sonuçların kaydedileceği dosya yolu (None ise ekrana yazdırır)
    """
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Sonuçlar {output_path} dosyasına kaydedildi.")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


def optimize_routes(args):
    """Rotaları optimize eder"""
    optimizer = SupplyChainOptimizer()
    
    print(f"'{args.origin}' konumundan {len(args.destinations)} varış noktasına rotalar optimize ediliyor...")
    results = optimizer.optimize_routes(args.origin, args.destinations)
    
    if "error" in results:
        print(f"Hata: {results['error']}")
        return 1
    
    print(f"Toplam {len(results['optimized_routes'])} rota optimize edildi.")
    print(f"Toplam emisyon: {results['total_emissions']:.2f} kg CO2e")
    
    save_results(results, args.output)
    return 0


def find_suppliers(args):
    """Sürdürülebilir tedarikçileri bulur"""
    optimizer = SupplyChainOptimizer()
    
    print(f"'{args.location}' konumu çevresinde '{args.product_type}' ürün tipi için tedarikçiler aranıyor...")
    results = optimizer.find_sustainable_suppliers(
        args.product_type,
        args.location,
        args.max_distance
    )
    
    if "error" in results:
        print(f"Hata: {results['error']}")
        return 1
    
    print(f"Toplam {results['count']} tedarikçi bulundu.")
    
    save_results(results, args.output)
    return 0


def analyze_impact(args):
    """Çevresel etki analizi yapar"""
    optimizer = SupplyChainOptimizer()
    
    # Rota verilerini oku
    try:
        with open(args.routes_file, "r", encoding="utf-8") as f:
            routes_data = json.load(f)
        routes = routes_data.get("optimized_routes", [])
    except Exception as e:
        print(f"Rota dosyası okunamadı: {e}")
        return 1
    
    # Tedarikçi verilerini oku
    try:
        with open(args.suppliers_file, "r", encoding="utf-8") as f:
            suppliers_data = json.load(f)
        suppliers = suppliers_data.get("suppliers", [])
    except Exception as e:
        print(f"Tedarikçi dosyası okunamadı: {e}")
        return 1
    
    print("Çevresel etki analizi yapılıyor...")
    results = optimizer.calculate_environmental_impact(routes, suppliers)
    
    print(f"Toplam emisyon: {results['total_emissions_kg_co2e']:.2f} kg CO2e")
    print(f"Çevresel etki puanı: {results['environmental_impact_score']:.1f}/100")
    
    save_results(results, args.output)
    return 0


def main():
    """Ana fonksiyon"""
    args = parse_args()
    
    if args.command == "optimize-routes":
        return optimize_routes(args)
    elif args.command == "find-suppliers":
        return find_suppliers(args)
    elif args.command == "analyze-impact":
        return analyze_impact(args)
    else:
        print("Geçerli bir komut belirtilmedi. Yardım için --help kullanın.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
