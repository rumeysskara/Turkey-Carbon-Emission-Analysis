#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu Web Arayüzü Testleri
-----------------------------------------------------------------
Bu modül, web arayüzünü test eder.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Src dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Web app modülünü içe aktar
import web_app


class TestWebApp(unittest.TestCase):
    """Web arayüzünü test eden sınıf"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.app = web_app.app.test_client()
        self.app.testing = True
    
    def test_index_route(self):
        """Ana sayfa rotasını test eder"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
    
    @patch("web_app.optimizer")
    def test_optimize_routes_api(self, mock_optimizer):
        """Rota optimizasyonu API'sini test eder"""
        # Mock yanıtı ayarla
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
        
        # API isteği gönder
        response = self.app.post(
            "/optimize-routes",
            data=json.dumps({
                "origin": "Istanbul, Turkey",
                "destinations": ["Ankara, Turkey"]
            }),
            content_type="application/json"
        )
        
        # Kontroller
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("optimized_routes", data)
        self.assertIn("total_emissions", data)
        self.assertEqual(len(data["optimized_routes"]), 1)
        self.assertEqual(data["optimized_routes"][0]["origin"], "Istanbul, Turkey")
        self.assertEqual(data["optimized_routes"][0]["destination"], "Ankara, Turkey")
    
    @patch("web_app.optimizer")
    def test_find_suppliers_api(self, mock_optimizer):
        """Tedarikçi bulma API'sini test eder"""
        # Mock yanıtı ayarla
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
        
        # API isteği gönder
        response = self.app.post(
            "/find-suppliers",
            data=json.dumps({
                "product_type": "electronics",
                "location": "Istanbul, Turkey",
                "max_distance": 50.0
            }),
            content_type="application/json"
        )
        
        # Kontroller
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("suppliers", data)
        self.assertIn("count", data)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["suppliers"][0]["name"], "Supplier 1")
    
    @patch("web_app.optimizer")
    def test_analyze_impact_api(self, mock_optimizer):
        """Çevresel etki analizi API'sini test eder"""
        # Mock yanıtı ayarla
        mock_optimizer.calculate_environmental_impact.return_value = {
            "total_emissions_kg_co2e": 500.0,
            "avg_supplier_sustainability": 80.0,
            "local_sourcing_ratio": 0.75,
            "environmental_impact_score": 90.0
        }
        
        # API isteği gönder
        response = self.app.post(
            "/analyze-impact",
            data=json.dumps({
                "routes": [
                    {
                        "origin": "Istanbul, Turkey",
                        "destination": "Ankara, Turkey",
                        "distance_km": 450.0,
                        "emissions_kg_co2e": 382.5
                    }
                ],
                "suppliers": [
                    {
                        "name": "Supplier 1",
                        "distance_km": 15.0,
                        "sustainability_score": 85.0
                    }
                ]
            }),
            content_type="application/json"
        )
        
        # Kontroller
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("total_emissions_kg_co2e", data)
        self.assertIn("avg_supplier_sustainability", data)
        self.assertIn("local_sourcing_ratio", data)
        self.assertIn("environmental_impact_score", data)
    
    def test_invalid_optimize_routes_request(self):
        """Geçersiz rota optimizasyonu isteğini test eder"""
        # Eksik parametre ile API isteği gönder
        response = self.app.post(
            "/optimize-routes",
            data=json.dumps({
                "origin": "Istanbul, Turkey"
                # destinations eksik
            }),
            content_type="application/json"
        )
        
        # Kontroller
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_invalid_find_suppliers_request(self):
        """Geçersiz tedarikçi bulma isteğini test eder"""
        # Eksik parametre ile API isteği gönder
        response = self.app.post(
            "/find-suppliers",
            data=json.dumps({
                "product_type": "electronics"
                # location eksik
            }),
            content_type="application/json"
        )
        
        # Kontroller
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_invalid_analyze_impact_request(self):
        """Geçersiz çevresel etki analizi isteğini test eder"""
        # Eksik parametre ile API isteği gönder
        response = self.app.post(
            "/analyze-impact",
            data=json.dumps({
                "routes": []
                # suppliers eksik
            }),
            content_type="application/json"
        )
        
        # Kontroller
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
