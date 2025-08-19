#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenRouter GPT-5-nano Entegrasyonu
---------------------------------
Bu modül, OpenRouter API üzerinden GPT-5-nano modelini kullanarak 
karbon emisyonu analizi ve tahminleri için yapay zeka destekli öneriler sunar.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional


class OpenRouterGPTIntegration:
    """OpenRouter GPT-5-nano entegrasyonu için sınıf"""
    
    def __init__(self, config_path: str = "config/openrouter_config.json"):
        """
        Sınıfı başlat
        
        Args:
            config_path: Yapılandırma dosyası yolu
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config.get("OPENROUTER_API_KEY", "")
        self.model = self.config.get("model", "openai/gpt-5-nano")
        self.api_url = self.config.get("api_url", "https://openrouter.ai/api/v1/chat/completions")
        self.site_url = self.config.get("site_url", "")
        self.site_name = self.config.get("site_name", "")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Yapılandırma dosyasını yükle
        
        Args:
            config_path: Yapılandırma dosyası yolu
            
        Returns:
            Yapılandırma
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"OpenRouter yapılandırma dosyası yüklenemedi: {str(e)}")
            return {}
    
    def _make_api_request(self, messages: List[Dict]) -> Dict:
        """
        OpenRouter API'ye istek gönder
        
        Args:
            messages: Mesaj listesi
            
        Returns:
            API yanıtı
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Opsiyonel header'lar ekle
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            headers["X-Title"] = self.site_name
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"OpenRouter API hatası: {str(e)}")
            return {}
    
    def generate_carbon_analysis(self, emissions_data: Dict, predictions_data: Dict) -> Dict:
        """
        Karbon emisyonu analizi oluştur
        
        Args:
            emissions_data: Mevcut emisyon verileri
            predictions_data: Tahmin verileri
            
        Returns:
            Analiz sonuçları
        """
        try:
            # Özet istatistikler çıkar
            total_factories = len([f for region in emissions_data.get("region_results", []) 
                                 for f in region.get("factories", [])])
            total_emissions = sum([region.get("total_emissions_ton", 0) 
                                 for region in emissions_data.get("region_results", [])])
            
            predicted_total = predictions_data.get("predicted_total_emissions_ton", 0)
            emission_change = predictions_data.get("emission_change_ton", 0)
            change_percent = predictions_data.get("emission_change_percent", 0)
            
            # GPT-5-nano için optimize edilmiş prompt
            prompt = f"""
Türkiye karbon emisyon analizi:

MEVCUT DURUM:
- Toplam fabrika: {total_factories}
- Mevcut emisyon: {total_emissions:.2f} ton CO2e/yıl
- 2026 tahmini: {predicted_total:.2f} ton CO2e/yıl
- Değişim: {change_percent:.2f}% ({emission_change:.2f} ton)

GÖREV: Bu veriler için kısa ve özlü sürdürülebilirlik analizi yap. Şunları içer:
1. Durum özeti (2 cümle)
2. Ana bulgular (3 madde)
3. Azaltma önerileri (3 madde)
4. Politika önerileri (3 madde)
5. Teknoloji yatırımları (3 madde)

JSON formatında yanıt ver:
{{
  "executive_summary": "özet",
  "key_findings": ["bulgu1", "bulgu2", "bulgu3"],
  "emission_reduction": ["öneri1", "öneri2", "öneri3"],
  "policy_suggestions": ["politika1", "politika2", "politika3"],
  "technology_investments": ["teknoloji1", "teknoloji2", "teknoloji3"]
}}
"""
            
            messages = [
                {
                    "role": "system",
                    "content": "Sen karbon emisyonu uzmanısın. Kısa, net ve actionable analizler yaparsın. Türkçe yanıt ver."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # API çağrısı yap
            response = self._make_api_request(messages)
            
            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                
                # JSON parse etmeye çalış
                try:
                    analysis = json.loads(content)
                    return {
                        "title": "GPT-5-nano Karbon Emisyonu Analizi",
                        "model": "openai/gpt-5-nano",
                        "executive_summary": analysis.get("executive_summary", ""),
                        "current_emissions": {
                            "key_findings": analysis.get("key_findings", []),
                            "total_factories": total_factories,
                            "total_emissions_ton": total_emissions
                        },
                        "future_predictions": {
                            "predicted_total_emissions_ton": predicted_total,
                            "emission_change_percent": change_percent,
                            "recommendations": {
                                "emission_reduction": analysis.get("emission_reduction", []),
                                "policy_suggestions": analysis.get("policy_suggestions", []),
                                "technology_investments": analysis.get("technology_investments", [])
                            }
                        },
                        "conclusion": f"GPT-5-nano ile analiz edilen veriler, Türkiye'deki {total_factories} fabrikanın karbon emisyonlarında %{change_percent:.2f} değişim öngörüyor."
                    }
                except json.JSONDecodeError:
                    # JSON parse edilemezse fallback
                    return self._create_fallback_analysis(total_factories, total_emissions, predicted_total, change_percent)
            
            # API hatası durumunda fallback
            return self._create_fallback_analysis(total_factories, total_emissions, predicted_total, change_percent)
            
        except Exception as e:
            print(f"GPT-5-nano analiz hatası: {str(e)}")
            return self._create_fallback_analysis(0, 0, 0, 0)
    
    def _create_fallback_analysis(self, factories: int, current: float, predicted: float, change: float) -> Dict:
        """
        Fallback analizi oluştur
        
        Args:
            factories: Fabrika sayısı
            current: Mevcut emisyon
            predicted: Tahmin edilen emisyon
            change: Değişim yüzdesi
            
        Returns:
            Fallback analizi
        """
        return {
            "title": "Karbon Emisyonu Analizi (Fallback)",
            "model": "fallback",
            "executive_summary": f"Türkiye'deki {factories} fabrikanın karbon emisyonları analiz edildi. 2026 yılında %{change:.2f} değişim bekleniyor.",
            "current_emissions": {
                "key_findings": [
                    "Türkiye genelinde fabrika emisyonları detaylı analiz edildi",
                    "Sektörel farklılıklar gözlemlendi",
                    "Bölgesel emisyon yoğunluk farklılıkları tespit edildi"
                ],
                "total_factories": factories,
                "total_emissions_ton": current
            },
            "future_predictions": {
                "predicted_total_emissions_ton": predicted,
                "emission_change_percent": change,
                "recommendations": {
                    "emission_reduction": [
                        "Enerji verimliliği yatırımları artırılmalı",
                        "Yenilenebilir enerji kullanımı teşvik edilmeli",
                        "Sürdürülebilir üretim süreçleri benimsensmeli"
                    ],
                    "policy_suggestions": [
                        "Karbon fiyatlandırma mekanizmaları oluşturulmalı",
                        "Emisyon standartları güçlendirilmeli", 
                        "Yeşil teknoloji yatırımları desteklenmeli"
                    ],
                    "technology_investments": [
                        "Karbon yakalama ve depolama teknolojileri",
                        "Akıllı enerji yönetim sistemleri",
                        "Temiz üretim teknolojileri"
                    ]
                }
            },
            "conclusion": "Sistemik yaklaşımla karbon nötr hedeflerine ulaşılabilir."
        }
    
    def generate_scenario_analysis(self, emissions_data: Dict) -> Dict:
        """
        Senaryo analizi oluştur
        
        Args:
            emissions_data: Emisyon verileri
            
        Returns:
            Senaryo analizi
        """
        try:
            # Kısa prompt ile hızlı senaryo analizi
            prompt = f"""
Türkiye fabrika emisyonları için 5 gelecek senaryosu oluştur:

VERİ ÖZET:
- {len([f for r in emissions_data.get('region_results', []) for f in r.get('factories', [])])} fabrika
- {sum([r.get('total_emissions_ton', 0) for r in emissions_data.get('region_results', [])]):.0f} ton CO2e/yıl

SENARYO TİPLERİ:
1. İyimser: Hızlı yeşil dönüşüm
2. Gerçekçi: Mevcut politikalarla devam
3. Kötümser: Yetersiz aksiyonlar
4. Disruptif: Teknolojik devrim
5. Politika odaklı: Güçlü düzenlemeler

Her senaryo için: isim, açıklama (1 cümle), 2026 emisyon değişimi (%)

JSON format:
{{
  "scenarios": [
    {{"name": "İyimser", "description": "açıklama", "emission_change_percent": -25}},
    ...
  ]
}}
"""
            
            messages = [
                {
                    "role": "system", 
                    "content": "Sen iklim politikası uzmanısın. Kısa ve net senaryolar oluşturursun."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self._make_api_request(messages)
            
            if response and "choices" in response:
                try:
                    content = response["choices"][0]["message"]["content"]
                    scenarios = json.loads(content)
                    return {
                        "title": "GPT-5-nano Gelecek Senaryoları",
                        "model": "openai/gpt-5-nano",
                        "scenarios": scenarios.get("scenarios", [])
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback senaryolar
            return self._create_fallback_scenarios()
            
        except Exception as e:
            print(f"GPT-5-nano senaryo hatası: {str(e)}")
            return self._create_fallback_scenarios()
    
    def _create_fallback_scenarios(self) -> Dict:
        """Fallback senaryolar oluştur"""
        return {
            "title": "Gelecek Senaryoları (Fallback)",
            "model": "fallback",
            "scenarios": [
                {
                    "name": "İyimser Senaryo",
                    "description": "Hızlı yeşil dönüşüm ve teknoloji adaptasyonu",
                    "emission_change_percent": -25
                },
                {
                    "name": "Gerçekçi Senaryo", 
                    "description": "Mevcut politikalar ve orta tempolu gelişim",
                    "emission_change_percent": -10
                },
                {
                    "name": "Kötümser Senaryo",
                    "description": "Yetersiz aksiyonlar ve yavaş ilerleme", 
                    "emission_change_percent": 5
                },
                {
                    "name": "Disruptif Senaryo",
                    "description": "Teknolojik devrim ve radikal dönüşüm",
                    "emission_change_percent": -40
                },
                {
                    "name": "Politika Odaklı",
                    "description": "Güçlü düzenlemeler ve teşviklerle hızlı değişim",
                    "emission_change_percent": -30
                }
            ]
        }


def main():
    """Ana fonksiyon - test için"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GPT-5-nano ile karbon analizi")
    parser.add_argument("--emissions", required=True, help="Emisyon verileri JSON dosyası")
    parser.add_argument("--predictions", required=True, help="Tahmin verileri JSON dosyası") 
    parser.add_argument("--output", default="data/gpt5_nano_analysis.json", help="Çıktı dosyası")
    
    args = parser.parse_args()
    
    # Verileri yükle
    with open(args.emissions, "r", encoding="utf-8") as f:
        emissions_data = json.load(f)
    
    with open(args.predictions, "r", encoding="utf-8") as f:
        predictions_data = json.load(f)
    
    # GPT-5-nano entegrasyonu
    gpt = OpenRouterGPTIntegration()
    
    # Analiz oluştur
    analysis = gpt.generate_carbon_analysis(emissions_data, predictions_data)
    
    # Kaydet
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # Web uygulaması için kopyala
    static_output = "static/data/gpt_sustainability_report.json"
    os.makedirs(os.path.dirname(static_output), exist_ok=True)
    with open(static_output, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"GPT-5-nano analizi {args.output} dosyasına kaydedildi.")
    return 0


if __name__ == "__main__":
    main()
