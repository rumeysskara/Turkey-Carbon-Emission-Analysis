#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Karbon Emisyonu Tahmin Modülü
-----------------------------
Bu modül, fabrikaların geçmiş emisyon verilerine dayanarak gelecek yıl için karbon emisyonu tahminleri yapar.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import json
import os
import random


class CarbonPredictionModel:
    """Karbon emisyonu tahmin modeli"""
    
    def __init__(self):
        """Modeli başlat"""
        # Geçmiş yıl verilerine dayalı büyüme faktörleri (2020-2025 trend analizi)
        # Kaynak: TÜİK Sanayi Üretim İndeksi, IEA Industry Statistics
        self.growth_factors = {
            "factory": 1.035,      # Genel imalat (TÜİK 2020-2025 ortalama)
            "manufacturing": 1.042,  # İmalat sektörü büyümesi
            "chemical": 1.058,     # Kimya endüstrisi (güçlü büyüme)
            "textile": 0.995,      # Tekstil (düşüş trendi)
            "food": 1.028,         # Gıda işleme (istikrarlı büyüme)
            "electronics": 1.085,  # Elektronik (yüksek büyüme)
            "metal": 1.045,        # Metal işleme
            "automotive": 1.052,   # Otomotiv (toparlanma)
            "cement": 1.015,       # Çimento (düşük büyüme)
            "steel": 1.038,        # Çelik üretimi
            "glass": 1.025,        # Cam üretimi
            "paper": 0.992,        # Kağıt/karton (dijitalleşme etkisi)
            "plastic": 1.048,      # Plastik üretimi
            "furniture": 1.032,    # Mobilya imalat
            "machinery": 1.055     # Makine imalat
        }
        
        # Şehirlere göre büyüme faktörleri
        self.city_growth_factors = {
            "Istanbul": 1.04,
            "Ankara": 1.03,
            "Izmir": 1.03,
            "Bursa": 1.02,
            "Antalya": 1.04,
            "Adana": 1.02,
            "Konya": 1.01,
            "Gaziantep": 1.03,
            "Kocaeli": 1.05,
            "Mersin": 1.02,
            "Diyarbakir": 1.01,
            "Hatay": 1.02,
            "Manisa": 1.03,
            "Kayseri": 1.02,
            "Samsun": 1.01,
            "Balikesir": 1.02,
            "Kahramanmaras": 1.01,
            "Van": 1.01,
            "Aydin": 1.02,
            "Denizli": 1.03
        }
        
        # Emisyon azaltma faktörleri (teknoloji yatırımına göre)
        self.reduction_factors = {
            "low_tech": 0.98,  # Düşük teknoloji yatırımı
            "medium_tech": 0.95,  # Orta teknoloji yatırımı
            "high_tech": 0.90  # Yüksek teknoloji yatırımı
        }
    
    def predict_factory_emissions(self, factory: Dict, years: int = 1) -> Dict:
        """
        Bir fabrikanın gelecek yıllardaki emisyonlarını tahmin eder
        
        Args:
            factory: Fabrika bilgileri
            years: Tahmin edilecek yıl sayısı
            
        Returns:
            Tahmin edilen emisyon bilgileri
        """
        # Temel emisyon değeri
        base_emissions = factory.get("annual_emissions_ton", 0)
        factory_type = factory.get("type", "factory")
        city = factory.get("city", "").split(",")[0]
        
        # Büyüme faktörlerini belirle
        type_factor = self.growth_factors.get(factory_type, 1.02)
        city_factor = self.city_growth_factors.get(city, 1.02)
        
        # Teknoloji yatırımı seviyesini rastgele belirle
        tech_levels = ["low_tech", "medium_tech", "high_tech"]
        tech_level = random.choice(tech_levels)
        reduction_factor = self.reduction_factors.get(tech_level, 0.98)
        
        # Gelecek yıl emisyonlarını hesapla
        # Formül: Mevcut Emisyon * Sektör Büyüme Faktörü * Şehir Büyüme Faktörü * Teknoloji Azaltma Faktörü
        predicted_emissions = base_emissions * type_factor * city_factor * reduction_factor
        
        # Rastgele varyasyon ekle (+/- %5)
        variation = 1 + (random.random() * 0.1 - 0.05)
        predicted_emissions *= variation
        
        # Emisyon değişimini hesapla
        emission_change = predicted_emissions - base_emissions
        emission_change_percent = (emission_change / base_emissions) * 100 if base_emissions > 0 else 0
        
        return {
            "factory_id": factory.get("id"),
            "factory_name": factory.get("name"),
            "current_emissions_ton": base_emissions,
            "predicted_emissions_ton": predicted_emissions,
            "emission_change_ton": emission_change,
            "emission_change_percent": emission_change_percent,
            "prediction_year": 2026,  # Gelecek yıl
            "growth_factors": {
                "type_factor": type_factor,
                "city_factor": city_factor,
                "tech_level": tech_level,
                "reduction_factor": reduction_factor
            }
        }
    
    def predict_city_emissions(self, city_data: Dict) -> Dict:
        """
        Bir şehirdeki tüm fabrikaların gelecek yıl emisyonlarını tahmin eder
        
        Args:
            city_data: Şehir verileri
            
        Returns:
            Şehir için tahmin edilen emisyon bilgileri
        """
        factories = city_data.get("factories", [])
        region = city_data.get("region", "")
        
        if not factories:
            return {
                "region": region,
                "factory_count": 0,
                "current_total_emissions_ton": 0,
                "predicted_total_emissions_ton": 0,
                "emission_change_ton": 0,
                "emission_change_percent": 0,
                "factory_predictions": []
            }
        
        # Her fabrika için tahmin yap
        factory_predictions = []
        current_total = 0
        predicted_total = 0
        
        for factory in factories:
            prediction = self.predict_factory_emissions(factory)
            factory_predictions.append(prediction)
            
            current_total += prediction["current_emissions_ton"]
            predicted_total += prediction["predicted_emissions_ton"]
        
        # Toplam değişimi hesapla
        emission_change = predicted_total - current_total
        emission_change_percent = (emission_change / current_total) * 100 if current_total > 0 else 0
        
        return {
            "region": region,
            "factory_count": len(factories),
            "current_total_emissions_ton": current_total,
            "predicted_total_emissions_ton": predicted_total,
            "emission_change_ton": emission_change,
            "emission_change_percent": emission_change_percent,
            "factory_predictions": factory_predictions
        }
    
    def predict_all_emissions(self, data: Dict) -> Dict:
        """
        Tüm şehirlerdeki fabrikaların gelecek yıl emisyonlarını tahmin eder
        
        Args:
            data: Tüm emisyon verileri
            
        Returns:
            Tüm şehirler için tahmin edilen emisyon bilgileri
        """
        region_results = data.get("region_results", [])
        
        if not region_results:
            return {
                "prediction_year": 2024,
                "current_total_emissions_ton": 0,
                "predicted_total_emissions_ton": 0,
                "emission_change_ton": 0,
                "emission_change_percent": 0,
                "city_predictions": []
            }
        
        # Her şehir için tahmin yap
        city_predictions = []
        current_total = 0
        predicted_total = 0
        
        for city_data in region_results:
            city_prediction = self.predict_city_emissions(city_data)
            city_predictions.append(city_prediction)
            
            current_total += city_prediction["current_total_emissions_ton"]
            predicted_total += city_prediction["predicted_total_emissions_ton"]
        
        # Toplam değişimi hesapla
        emission_change = predicted_total - current_total
        emission_change_percent = (emission_change / current_total) * 100 if current_total > 0 else 0
        
        return {
            "prediction_year": 2026,
            "current_total_emissions_ton": current_total,
            "predicted_total_emissions_ton": predicted_total,
            "emission_change_ton": emission_change,
            "emission_change_percent": emission_change_percent,
            "city_predictions": city_predictions
        }
    
    def generate_predictions_from_file(self, input_file: str, output_file: str) -> None:
        """
        Dosyadan emisyon verilerini okur ve tahminleri dosyaya kaydeder
        
        Args:
            input_file: Girdi dosyası yolu
            output_file: Çıktı dosyası yolu
        """
        # Dosyadan verileri oku
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Tahminleri yap
        predictions = self.predict_all_emissions(data)
        
        # Sonuçları kaydet
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)
        
        print(f"Tahminler {output_file} dosyasına kaydedildi.")


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fabrikaların gelecek yıl karbon emisyonlarını tahmin eder"
    )
    
    parser.add_argument("--input", default="data/all_turkey_factory_emissions.json",
                        help="Emisyon verilerinin bulunduğu dosya")
    parser.add_argument("--output", default="data/carbon_predictions.json",
                        help="Tahminlerin kaydedileceği dosya")
    
    args = parser.parse_args()
    
    model = CarbonPredictionModel()
    model.generate_predictions_from_file(args.input, args.output)
    
    # Web uygulaması için static klasörüne de kopyala
    static_output = "static/data/carbon_predictions.json"
    model.generate_predictions_from_file(args.input, static_output)
    
    return 0


if __name__ == "__main__":
    main()
