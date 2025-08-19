#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu Uygulama Testleri
--------------------------------------------------------------
Bu modül, komut satırı uygulamasını test eder.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import tempfile
import argparse

# Src dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# App modülündeki fonksiyonları içe aktar
from app import optimize_routes, find_suppliers, analyze_impact, save_results


class TestApp(unittest.TestCase):
    """Komut satırı uygulamasını test eden sınıf"""
    
    @patch("app.SupplyChainOptimizer")
    def test_optimize_routes(self, mock_optimizer_class):
        """Rota optimizasyonu fonksiyonunu test eder"""
        # Mock optimizer örneği oluştur
        mock_optimizer = MagicMock()
        mock_optimizer_class.return_value = mock_optimizer
        
        # Mock optimize_routes yanıtını ayarla
        mock_optimizer.optimize_routes.return_value = {
            "optimized_routes": [
                {
                    "origin": "Istanbul, Turkey",
                    "destination": "Ankara, Turkey",
                    "distance_km": 450.0,
                    "emissions_kg_co2e": 382.5
                }
            ],
            "total_emissions": 382.5
        }
        
        # Mock argümanlar oluştur
        args = argparse.Namespace()
        args.origin = "Istanbul, Turkey"
        args.destinations = ["Ankara, Turkey"]
        args.output = None
        
        # Fonksiyonu çağır
        result = optimize_routes(args)
        
        # Kontroller
        self.assertEqual(result, 0)  # Başarılı sonuç kodu
        mock_optimizer.optimize_routes.assert_called_once_with("Istanbul, Turkey", ["Ankara, Turkey"])
    
    @patch("app.SupplyChainOptimizer")
    def test_find_suppliers(self, mock_optimizer_class):
        """Tedarikçi bulma fonksiyonunu test eder"""
        # Mock optimizer örneği oluştur
        mock_optimizer = MagicMock()
        mock_optimizer_class.return_value = mock_optimizer
        
        # Mock find_sustainable_suppliers yanıtını ayarla
        mock_optimizer.find_sustainable_suppliers.return_value = {
            "suppliers": [
                {
                    "name": "Supplier 1",
                    "distance_km": 15.0,
                    "sustainability_score": 85.0
                }
            ],
            "count": 1
        }
        
        # Mock argümanlar oluştur
        args = argparse.Namespace()
        args.product_type = "electronics"
        args.location = "Istanbul, Turkey"
        args.max_distance = 50.0
        args.output = None
        
        # Fonksiyonu çağır
        result = find_suppliers(args)
        
        # Kontroller
        self.assertEqual(result, 0)  # Başarılı sonuç kodu
        mock_optimizer.find_sustainable_suppliers.assert_called_once_with(
            "electronics", "Istanbul, Turkey", 50.0
        )
    
    @patch("app.SupplyChainOptimizer")
    def test_analyze_impact(self, mock_optimizer_class):
        """Çevresel etki analizi fonksiyonunu test eder"""
        # Mock optimizer örneği oluştur
        mock_optimizer = MagicMock()
        mock_optimizer_class.return_value = mock_optimizer
        
        # Mock calculate_environmental_impact yanıtını ayarla
        mock_optimizer.calculate_environmental_impact.return_value = {
            "total_emissions_kg_co2e": 500.0,
            "avg_supplier_sustainability": 80.0,
            "local_sourcing_ratio": 0.75,
            "environmental_impact_score": 90.0
        }
        
        # Geçici dosyalar oluştur
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as routes_file:
            json.dump({
                "optimized_routes": [
                    {
                        "origin": "Istanbul, Turkey",
                        "destination": "Ankara, Turkey",
                        "distance_km": 450.0,
                        "emissions_kg_co2e": 382.5
                    }
                ]
            }, routes_file)
            routes_file_path = routes_file.name
        
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as suppliers_file:
            json.dump({
                "suppliers": [
                    {
                        "name": "Supplier 1",
                        "distance_km": 15.0,
                        "sustainability_score": 85.0
                    }
                ]
            }, suppliers_file)
            suppliers_file_path = suppliers_file.name
        
        try:
            # Mock argümanlar oluştur
            args = argparse.Namespace()
            args.routes_file = routes_file_path
            args.suppliers_file = suppliers_file_path
            args.output = None
            
            # Fonksiyonu çağır
            result = analyze_impact(args)
            
            # Kontroller
            self.assertEqual(result, 0)  # Başarılı sonuç kodu
            mock_optimizer.calculate_environmental_impact.assert_called_once()
        finally:
            # Geçici dosyaları temizle
            os.unlink(routes_file_path)
            os.unlink(suppliers_file_path)
    
    def test_save_results(self):
        """Sonuçları kaydetme fonksiyonunu test eder"""
        # Test verileri
        results = {
            "test_key": "test_value",
            "test_number": 123
        }
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            output_path = temp_file.name
        
        try:
            # Dosyaya kaydet
            save_results(results, output_path)
            
            # Dosyayı oku ve kontrol et
            with open(output_path, "r") as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data, results)
        finally:
            # Geçici dosyayı temizle
            os.unlink(output_path)


if __name__ == "__main__":
    unittest.main()
