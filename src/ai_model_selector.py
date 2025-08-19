#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Model Seçici
--------------
Bu modül, farklı AI modelleri arasında seçim yapmak için kullanılır.
"""

import json
import sys
import os
from typing import Dict, Any

# Module import için path ayarla
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gpt_integration import GPTIntegration
    from openrouter_integration import OpenRouterGPTIntegration
except ImportError:
    # Alternative import yolu
    import importlib.util
    
    def load_module_from_path(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    GPTIntegration = load_module_from_path("gpt_integration", os.path.join(current_dir, "gpt_integration.py")).GPTIntegration
    OpenRouterGPTIntegration = load_module_from_path("openrouter_integration", os.path.join(current_dir, "openrouter_integration.py")).OpenRouterGPTIntegration


class AIModelSelector:
    """AI Model seçici sınıfı"""
    
    def __init__(self):
        """Sınıfı başlat"""
        self.available_models = {
            "gpt-4o-mini": {
                "provider": "openai",
                "cost": "düşük",
                "speed": "hızlı",
                "description": "OpenAI'nin verimli modeli"
            },
            "gpt-5-nano": {
                "provider": "openrouter", 
                "cost": "çok düşük",
                "speed": "çok hızlı",
                "description": "En hızlı ve ekonomik GPT-5 modeli"
            },
            "gpt-5-mini": {
                "provider": "openrouter",
                "cost": "orta",
                "speed": "hızlı", 
                "description": "Gelişmiş GPT-5 mini modeli"
            }
        }
    
    def get_best_model_for_task(self, task_type: str = "analysis") -> str:
        """
        Görev tipine göre en iyi modeli seç
        
        Args:
            task_type: Görev tipi (analysis, prediction, scenario)
            
        Returns:
            Model adı
        """
        if task_type == "analysis":
            # Hızlı analiz için nano
            return "gpt-5-nano"
        elif task_type == "prediction":
            # Tahmin için mini
            return "gpt-4o-mini"  
        elif task_type == "scenario":
            # Senaryo için nano (hızlı)
            return "gpt-5-nano"
        else:
            return "gpt-4o-mini"
    
    def create_analysis_with_best_model(self, emissions_data: Dict, predictions_data: Dict, task_type: str = "analysis") -> Dict:
        """
        En iyi modelle analiz oluştur
        
        Args:
            emissions_data: Emisyon verileri
            predictions_data: Tahmin verileri
            task_type: Görev tipi
            
        Returns:
            Analiz sonuçları
        """
        best_model = self.get_best_model_for_task(task_type)
        
        try:
            if best_model == "gpt-5-nano":
                # GPT-5-nano kullan
                openrouter = OpenRouterGPTIntegration()
                return openrouter.generate_carbon_analysis(emissions_data, predictions_data)
            else:
                # OpenAI kullan
                gpt = GPTIntegration()
                return gpt.generate_sustainability_report(emissions_data, predictions_data)
                
        except Exception as e:
            print(f"AI analiz hatası ({best_model}): {str(e)}")
            
            # Fallback olarak OpenAI dene
            try:
                gpt = GPTIntegration()
                return gpt.generate_sustainability_report(emissions_data, predictions_data)
            except Exception as e2:
                print(f"Fallback AI hatası: {str(e2)}")
                return self._create_emergency_fallback()
    
    def _create_emergency_fallback(self) -> Dict:
        """Acil durum fallback analizi"""
        return {
            "title": "Acil Durum Analizi",
            "model": "emergency_fallback",
            "executive_summary": "AI servislerine erişim sağlanamadı. Sistem otomatik analize geçti.",
            "current_emissions": {
                "key_findings": [
                    "Türkiye genelinde fabrika emisyonları tespit edildi",
                    "Sektörel ve bölgesel analizler yapıldı",
                    "İyileştirme potansiyeli belirlendi"
                ]
            },
            "future_predictions": {
                "recommendations": {
                    "emission_reduction": [
                        "Enerji verimliliği artırılmalı",
                        "Yenilenebilir enerji kullanılmalı", 
                        "Teknoloji yatırımları yapılmalı"
                    ],
                    "policy_suggestions": [
                        "Karbon fiyatlandırması uygulanmalı",
                        "Emisyon standartları güçlendirilmeli",
                        "Yeşil teşvikler artırılmalı"
                    ],
                    "technology_investments": [
                        "Karbon yakalama teknolojileri",
                        "Akıllı enerji sistemleri",
                        "Temiz üretim teknolojileri"
                    ]
                }
            },
            "conclusion": "Sistem yerel analizle devam ediyor. AI servisleri aktif olduğunda güncellenecek."
        }
    
    def get_model_info(self) -> Dict:
        """Mevcut modeller hakkında bilgi ver"""
        return {
            "available_models": self.available_models,
            "recommended": {
                "speed": "gpt-5-nano",
                "cost": "gpt-5-nano", 
                "quality": "gpt-4o-mini",
                "balanced": "gpt-5-nano"
            }
        }


def main():
    """Test fonksiyonu"""
    selector = AIModelSelector()
    info = selector.get_model_info()
    
    print("Mevcut AI Modelleri:")
    for model, details in info["available_models"].items():
        print(f"- {model}: {details['description']} ({details['provider']})")
    
    print(f"\nÖnerilen modeller:")
    for use_case, model in info["recommended"].items():
        print(f"- {use_case}: {model}")


if __name__ == "__main__":
    main()
