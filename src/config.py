#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu Yapılandırma Modülü
----------------------------------------------------------------
Bu modül, uygulama yapılandırmasını yönetir.
"""

import json
import os
from typing import Dict, Any


class Config:
    """Uygulama yapılandırmasını yöneten sınıf"""
    
    def __init__(self, config_path: str = None):
        """
        Yapılandırma sınıfını başlatır
        
        Args:
            config_path: Yapılandırma dosyasının yolu (None ise varsayılan konum kullanılır)
        """
        if config_path is None:
            # Varsayılan yapılandırma dosyası yolu
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "config.json")
            
            # Yapılandırma dosyası yoksa örnek dosyayı kopyala
            if not os.path.exists(config_path):
                example_config_path = os.path.join(base_dir, "config", "config.example.json")
                if os.path.exists(example_config_path):
                    print(f"Yapılandırma dosyası bulunamadı. Örnek dosya kopyalanıyor: {example_config_path} -> {config_path}")
                    with open(example_config_path, "r", encoding="utf-8") as src:
                        with open(config_path, "w", encoding="utf-8") as dst:
                            dst.write(src.read())
                else:
                    print(f"Uyarı: Yapılandırma dosyası ve örnek dosya bulunamadı.")
                    self.config = self._get_default_config()
                    return
        
        # Yapılandırma dosyasını oku
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            print(f"Yapılandırma dosyası yüklendi: {config_path}")
        except Exception as e:
            print(f"Yapılandırma dosyası okunamadı: {e}")
            self.config = self._get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Yapılandırma değerini döndürür
        
        Args:
            key: Nokta ile ayrılmış yapılandırma anahtarı (örn. "api.nominatim.user_agent")
            default: Anahtar bulunamazsa döndürülecek varsayılan değer
            
        Returns:
            Yapılandırma değeri veya varsayılan değer
        """
        keys = key.split(".")
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Yapılandırma değerini ayarlar
        
        Args:
            key: Nokta ile ayrılmış yapılandırma anahtarı (örn. "api.nominatim.user_agent")
            value: Ayarlanacak değer
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_path: str = None) -> None:
        """
        Yapılandırmayı dosyaya kaydeder
        
        Args:
            config_path: Yapılandırma dosyasının yolu (None ise varsayılan konum kullanılır)
        """
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "config.json")
        
        # Dizini oluştur
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Yapılandırmayı kaydet
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        print(f"Yapılandırma dosyaya kaydedildi: {config_path}")
    
    def _get_default_config(self) -> Dict:
        """
        Varsayılan yapılandırmayı döndürür
        
        Returns:
            Varsayılan yapılandırma
        """
        return {
            "api": {
                "nominatim": {
                    "user_agent": "SustainableSupplyChainOptimizer/1.0",
                    "rate_limit": 1
                },
                "osrm": {
                    "base_url": "http://router.project-osrm.org",
                    "profile": "driving"
                },
                "overpass": {
                    "base_url": "https://overpass-api.de/api/interpreter",
                    "timeout": 25
                }
            },
            "emission_factors": {
                "transportation": {
                    "car": 0.17,
                    "truck": 0.85
                }
            },
            "sustainability_weights": {
                "distance": 0.3,
                "emissions": 0.3,
                "local_sourcing": 0.25,
                "environmental_certifications": 0.15
            },
            "local_sourcing": {
                "threshold_km": 50
            },
            "web_app": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": True
            },
            "data_paths": {
                "cache_dir": "data/cache",
                "results_dir": "data/results",
                "logs_dir": "data/logs"
            }
        }


# Yapılandırma örneği
config = Config()


if __name__ == "__main__":
    # Yapılandırma değerlerini göster
    print("Yapılandırma değerleri:")
    print(f"Nominatim User-Agent: {config.get('api.nominatim.user_agent')}")
    print(f"OSRM Base URL: {config.get('api.osrm.base_url')}")
    print(f"Truck Emission Factor: {config.get('emission_factors.transportation.truck')} kg CO2e/km")
    print(f"Local Sourcing Threshold: {config.get('local_sourcing.threshold_km')} km")
    print(f"Web App Port: {config.get('web_app.port')}")
