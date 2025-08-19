#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu API Testleri
---------------------------------------------------------
Bu modül, API fonksiyonlarını test eder.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Src dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from apis import EmissionDataAPIs, LogisticsDataAPIs, SupplyChainOptimizer


class TestEmissionDataAPIs(unittest.TestCase):
    """Emisyon veri API'lerini test eden sınıf"""
    
    def test_get_ghg_protocol_factors(self):
        """GHG Protocol emisyon faktörlerini test eder"""
        api = EmissionDataAPIs()
        factors = api.get_ghg_protocol_factors()
        
        # Temel kontroller
        self.assertIsInstance(factors, dict)
        self.assertIn("electricity", factors)
        self.assertIn("fuel", factors)
        
        # Değer kontrolleri
        self.assertIn("turkey", factors["electricity"])
        self.assertIn("diesel", factors["fuel"])
        self.assertIsInstance(factors["electricity"]["turkey"], (int, float))
        self.assertIsInstance(factors["fuel"]["diesel"], (int, float))
    
    def test_get_epa_emission_data(self):
        """EPA emisyon verilerini test eder"""
        api = EmissionDataAPIs()
        data = api.get_epa_emission_data("transportation")
        
        # Temel kontroller
        self.assertIsInstance(data, dict)
        self.assertIn("passenger_car", data)
        self.assertIsInstance(data["passenger_car"], (int, float))


class TestLogisticsDataAPIs(unittest.TestCase):
    """Lojistik veri API'lerini test eden sınıf"""
    
    @patch("apis.LogisticsDataAPIs.geocode_address")
    def test_geocode_address(self, mock_geocode):
        """Adres kodlama fonksiyonunu test eder"""
        # Mock yanıt ayarla
        mock_geocode.return_value = {
            "lat": 41.0082,
            "lon": 28.9784,
            "display_name": "İstanbul, Türkiye"
        }
        
        api = LogisticsDataAPIs()
        result = api.geocode_address("Istanbul, Turkey")
        
        # Kontroller
        self.assertIsInstance(result, dict)
        self.assertIn("lat", result)
        self.assertIn("lon", result)
        self.assertIsInstance(result["lat"], float)
        self.assertIsInstance(result["lon"], float)
    
    @patch("requests.get")
    def test_get_local_suppliers(self, mock_get):
        """Yerel tedarikçi bulma fonksiyonunu test eder"""
        # Mock yanıt ayarla
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "elements": [
                {
                    "id": 123456789,
                    "lat": 41.1,
                    "lon": 29.0,
                    "tags": {
                        "name": "Test Supplier",
                        "industrial": "electronics"
                    },
                    "distance": 10000  # 10 km
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api = LogisticsDataAPIs()
        result = api.get_local_suppliers(41.0, 29.0, 20000, "electronics")
        
        # Kontroller
        self.assertIsInstance(result, dict)
        self.assertIn("elements", result)
        self.assertEqual(len(result["elements"]), 1)
        self.assertEqual(result["elements"][0]["tags"]["industrial"], "electronics")


class TestSupplyChainOptimizer(unittest.TestCase):
    """Tedarik zinciri optimizasyonu sınıfını test eden sınıf"""
    
    @patch("apis.LogisticsDataAPIs.geocode_address")
    @patch("apis.LogisticsDataAPIs.calculate_route_distance")
    def test_optimize_routes(self, mock_calculate_route, mock_geocode):
        """Rota optimizasyonu fonksiyonunu test eder"""
        # Mock yanıtları ayarla
        mock_geocode.side_effect = [
            {"lat": 41.0, "lon": 29.0, "display_name": "İstanbul, Türkiye"},
            {"lat": 39.9, "lon": 32.8, "display_name": "Ankara, Türkiye"},
            {"lat": 38.4, "lon": 27.1, "display_name": "İzmir, Türkiye"}
        ]
        
        mock_calculate_route.side_effect = [
            {
                "distance_km": 450.0,
                "duration_min": 300.0,
                "emissions_kg_co2e": 382.5
            },
            {
                "distance_km": 500.0,
                "duration_min": 330.0,
                "emissions_kg_co2e": 425.0
            }
        ]
        
        optimizer = SupplyChainOptimizer()
        result = optimizer.optimize_routes(
            "Istanbul, Turkey",
            ["Ankara, Turkey", "Izmir, Turkey"]
        )
        
        # Kontroller
        self.assertIsInstance(result, dict)
        self.assertIn("optimized_routes", result)
        self.assertIn("total_emissions", result)
        self.assertEqual(len(result["optimized_routes"]), 2)
        self.assertAlmostEqual(result["total_emissions"], 807.5)
    
    @patch("apis.LogisticsDataAPIs.geocode_address")
    @patch("apis.LogisticsDataAPIs.get_local_suppliers")
    def test_find_sustainable_suppliers(self, mock_get_suppliers, mock_geocode):
        """Sürdürülebilir tedarikçi bulma fonksiyonunu test eder"""
        # Mock yanıtları ayarla
        mock_geocode.return_value = {
            "lat": 41.0, 
            "lon": 29.0, 
            "display_name": "İstanbul, Türkiye"
        }
        
        mock_get_suppliers.return_value = {
            "elements": [
                {
                    "id": 123,
                    "lat": 41.1,
                    "lon": 29.1,
                    "tags": {
                        "name": "Supplier 1",
                        "industrial": "electronics"
                    },
                    "distance": 15000  # 15 km
                },
                {
                    "id": 456,
                    "lat": 41.2,
                    "lon": 29.2,
                    "tags": {
                        "name": "Supplier 2",
                        "industrial": "electronics"
                    },
                    "distance": 25000  # 25 km
                }
            ]
        }
        
        optimizer = SupplyChainOptimizer()
        result = optimizer.find_sustainable_suppliers(
            "electronics",
            "Istanbul, Turkey",
            50.0
        )
        
        # Kontroller
        self.assertIsInstance(result, dict)
        self.assertIn("suppliers", result)
        self.assertIn("count", result)
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["suppliers"]), 2)
        
        # Tedarikçilerin sürdürülebilirlik puanı olduğunu kontrol et
        for supplier in result["suppliers"]:
            self.assertIn("sustainability_score", supplier)
            self.assertIsInstance(supplier["sustainability_score"], (int, float))


if __name__ == "__main__":
    unittest.main()
