#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI GPT Entegrasyonu
----------------------
Bu modül, OpenAI GPT modelini kullanarak karbon emisyonu analizi ve tahminleri için
yapay zeka destekli öneriler ve analizler sunar.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional


class GPTIntegration:
    """OpenAI GPT entegrasyonu için sınıf"""
    
    def __init__(self, config_path: str = "config/openai_config.json", use_openrouter: bool = False):
        """
        Sınıfı başlat
        
        Args:
            config_path: Yapılandırma dosyası yolu
            use_openrouter: OpenRouter kullanılsın mı
        """
        self.use_openrouter = use_openrouter
        
        if use_openrouter:
            # OpenRouter entegrasyonunu kullan
            try:
                from .openrouter_integration import OpenRouterGPTIntegration
                self.openrouter = OpenRouterGPTIntegration()
                self.config = self.openrouter.config
                self.api_key = self.openrouter.api_key
                self.model = self.openrouter.model
                self.api_url = self.openrouter.api_url
            except ImportError:
                print("OpenRouter entegrasyonu bulunamadı, OpenAI kullanılıyor")
                use_openrouter = False
        
        if not use_openrouter:
            # Normal OpenAI entegrasyonu
            self.config = self._load_config(config_path)
            self.api_key = self.config.get("OPENAI_API_KEY", self.config.get("api_key", ""))
            self.model = self.config.get("model", "gpt-4o-mini")
            self.api_url = "https://api.openai.com/v1/chat/completions"
    
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
            print(f"Yapılandırma dosyası yüklenemedi: {str(e)}")
            return {}
    
    def _is_model_available(self, model_name: str) -> bool:
        """
        Model mevcut mu kontrol et
        
        Args:
            model_name: Kontrol edilecek model adı
            
        Returns:
            Model mevcut mu
        """
        available_models = [
            "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", 
            "gpt-3.5-turbo", "gpt-5-mini", "gpt-5"
        ]
        return model_name in available_models
    
    def generate_analysis(self, data: Dict, prompt_template: str) -> Dict:
        """
        GPT modelini kullanarak analiz oluştur
        
        Args:
            data: Analiz için kullanılacak veri
            prompt_template: İstek şablonu
            
        Returns:
            Analiz sonuçları
        """
        # API isteği için veriyi hazırla
        prompt = prompt_template.format(**data)
        
        # API isteği gönder
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Sen bir karbon emisyonu ve sürdürülebilirlik uzmanısın. Verilen fabrika emisyon verilerini analiz ederek içgörüler ve öneriler sunuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # API yanıtını işle
            result = response.json()
            analysis_text = result["choices"][0]["message"]["content"]
            
            # Analiz metnini JSON formatına dönüştür
            try:
                # Önce JSON olarak ayrıştırmayı dene
                analysis_json = json.loads(analysis_text)
                return analysis_json
            except json.JSONDecodeError:
                # JSON olarak ayrıştırılamazsa metin olarak döndür
                return {"analysis": analysis_text}
            
        except Exception as e:
            print(f"GPT analizi oluşturulamadı: {str(e)}")
            # Hata durumunda simüle edilmiş bir analiz döndür
            return self._generate_simulated_analysis(data)
    
    def _generate_simulated_analysis(self, data: Dict) -> Dict:
        """
        Simüle edilmiş bir analiz oluştur (API çağrısı başarısız olduğunda)
        
        Args:
            data: Analiz için kullanılacak veri
            
        Returns:
            Simüle edilmiş analiz
        """
        # Temel verileri çıkar
        total_emissions = data.get("total_annual_emissions_ton", 0)
        factory_count = data.get("total_factory_count", 0)
        
        # Simüle edilmiş analiz
        return {
            "summary": {
                "title": "Türkiye'deki Fabrikaların Karbon Emisyonu Analizi",
                "overview": f"Türkiye genelinde {factory_count} fabrika analiz edilmiş olup, bu fabrikaların toplam yıllık karbon emisyonu {total_emissions:.2f} ton CO2e'dir.",
                "key_findings": [
                    "Emisyonların büyük bir kısmı sanayi yoğun bölgelerde yoğunlaşmaktadır.",
                    "Fabrika boyutları ve teknoloji seviyeleri emisyon değerlerini önemli ölçüde etkilemektedir.",
                    "Yenilenebilir enerji ve enerji verimliliği yatırımları emisyonları azaltabilir."
                ]
            },
            "recommendations": {
                "emission_reduction": [
                    "Enerji verimliliği projelerinin uygulanması",
                    "Yenilenebilir enerji kaynaklarının kullanımının artırılması",
                    "Karbon yakalama ve depolama teknolojilerinin değerlendirilmesi"
                ],
                "policy_suggestions": [
                    "Emisyon yoğun bölgelerde daha sıkı düzenlemeler getirilmesi",
                    "Düşük karbonlu üretim için teşviklerin artırılması",
                    "Karbon fiyatlandırma mekanizmalarının uygulanması"
                ]
            }
        }
    
    def analyze_emissions_data(self, data: Dict) -> Dict:
        """
        Emisyon verilerini analiz et
        
        Args:
            data: Emisyon verileri
            
        Returns:
            Analiz sonuçları
        """
        # İstek şablonu
        prompt_template = """
        Aşağıdaki Türkiye'deki fabrikaların karbon emisyonu verilerini analiz et ve JSON formatında içgörüler ve öneriler sun:

        Toplam Fabrika Sayısı: {total_factory_count}
        Toplam Yıllık Emisyon: {total_annual_emissions_ton:.2f} ton CO2e
        Ortalama Yıllık Emisyon: {average_annual_emissions_ton:.2f} ton CO2e/fabrika

        En çok fabrika bulunan şehirler ve emisyon değerleri:
        {top_cities_info}

        Bu verileri analiz ederek aşağıdaki JSON formatında bir yanıt oluştur:
        {{
            "summary": {{
                "title": "Türkiye'deki Fabrikaların Karbon Emisyonu Analizi",
                "overview": "Genel bir özet...",
                "key_findings": ["Bulgu 1", "Bulgu 2", "Bulgu 3"]
            }},
            "insights": {{
                "emission_patterns": "Emisyon paternleri hakkında içgörüler...",
                "regional_differences": "Bölgesel farklılıklar hakkında içgörüler...",
                "sector_analysis": "Sektörel analiz hakkında içgörüler..."
            }},
            "recommendations": {{
                "emission_reduction": ["Öneri 1", "Öneri 2", "Öneri 3"],
                "policy_suggestions": ["Politika 1", "Politika 2", "Politika 3"],
                "sustainable_practices": ["Uygulama 1", "Uygulama 2", "Uygulama 3"]
            }}
        }}
        
        Sadece JSON yanıtı ver, başka açıklama ekleme.
        """
        
        # En çok fabrika bulunan şehirleri belirle
        regions = data.get("region_results", [])
        regions_by_factories = sorted(regions, key=lambda x: x.get("factory_count", 0), reverse=True)
        top_cities = regions_by_factories[:5] if len(regions_by_factories) >= 5 else regions_by_factories
        
        top_cities_info = "\n".join([
            f"- {city['region']}: {city['factory_count']} fabrika, {city['total_annual_emissions_ton']:.2f} ton CO2e/yıl"
            for city in top_cities
        ])
        
        # Veriyi hazırla
        analysis_data = {
            "total_factory_count": data.get("total_factory_count", 0),
            "total_annual_emissions_ton": data.get("total_annual_emissions_ton", 0),
            "average_annual_emissions_ton": data.get("average_annual_emissions_ton", 0),
            "top_cities_info": top_cities_info
        }
        
        # Analizi oluştur
        return self.generate_analysis(analysis_data, prompt_template)
    
    def analyze_emission_predictions(self, predictions: Dict) -> Dict:
        """
        Emisyon tahminlerini analiz et
        
        Args:
            predictions: Emisyon tahminleri
            
        Returns:
            Analiz sonuçları
        """
        # İstek şablonu
        prompt_template = """
        Aşağıdaki Türkiye'deki fabrikaların gelecek yıl karbon emisyonu tahminlerini analiz et ve JSON formatında içgörüler ve öneriler sun:

        Mevcut Toplam Emisyon (2025): {current_total_emissions_ton:.2f} ton CO2e/yıl
        Tahmin Edilen Toplam Emisyon (2026): {predicted_total_emissions_ton:.2f} ton CO2e/yıl
        Emisyon Değişimi: {emission_change_ton:.2f} ton CO2e ({emission_change_percent:.2f}%)

        En yüksek emisyon değişimi gösteren şehirler:
        {top_cities_info}

        Bu verileri analiz ederek aşağıdaki JSON formatında bir yanıt oluştur:
        {{
            "summary": {{
                "title": "Türkiye'deki Fabrikaların 2026 Yılı Karbon Emisyonu Tahminleri",
                "overview": "Genel bir özet...",
                "trend": "artış" veya "azalış",
                "key_findings": ["Bulgu 1", "Bulgu 2", "Bulgu 3"]
            }},
            "insights": {{
                "trend_analysis": "Trend analizi hakkında içgörüler...",
                "regional_trends": "Bölgesel trendler hakkında içgörüler...",
                "risk_assessment": "Risk değerlendirmesi hakkında içgörüler..."
            }},
            "recommendations": {{
                "emission_reduction": ["Öneri 1", "Öneri 2", "Öneri 3"],
                "policy_suggestions": ["Politika 1", "Politika 2", "Politika 3"],
                "technology_investments": ["Teknoloji 1", "Teknoloji 2", "Teknoloji 3"]
            }},
            "future_scenarios": {{
                "best_case": "En iyi senaryo...",
                "expected_case": "Beklenen senaryo...",
                "worst_case": "En kötü senaryo..."
            }}
        }}
        
        Sadece JSON yanıtı ver, başka açıklama ekleme.
        """
        
        # En yüksek emisyon değişimi gösteren şehirleri belirle
        city_predictions = predictions.get("city_predictions", [])
        cities_by_change = sorted(city_predictions, key=lambda x: abs(x.get("emission_change_percent", 0)), reverse=True)
        top_cities = cities_by_change[:5] if len(cities_by_change) >= 5 else cities_by_change
        
        top_cities_info = "\n".join([
            f"- {city['region']}: {city['current_total_emissions_ton']:.2f} → {city['predicted_total_emissions_ton']:.2f} ton CO2e/yıl ({city['emission_change_percent']:.2f}%)"
            for city in top_cities
        ])
        
        # Veriyi hazırla
        analysis_data = {
            "current_total_emissions_ton": predictions.get("current_total_emissions_ton", 0),
            "predicted_total_emissions_ton": predictions.get("predicted_total_emissions_ton", 0),
            "emission_change_ton": predictions.get("emission_change_ton", 0),
            "emission_change_percent": predictions.get("emission_change_percent", 0),
            "top_cities_info": top_cities_info
        }
        
        # Analizi oluştur
        return self.generate_analysis(analysis_data, prompt_template)
    
    def generate_sustainability_report(self, emissions_data: Dict, predictions_data: Dict) -> Dict:
        """
        Sürdürülebilirlik raporu oluştur
        
        Args:
            emissions_data: Emisyon verileri
            predictions_data: Emisyon tahminleri
            
        Returns:
            Sürdürülebilirlik raporu
        """
        # Emisyon verilerini analiz et
        emissions_analysis = self.analyze_emissions_data(emissions_data)
        
        # Tahminleri analiz et
        predictions_analysis = self.analyze_emission_predictions(predictions_data)
        
        # Sürdürülebilirlik raporu oluştur
        report = {
            "title": "Türkiye'deki Fabrikaların Karbon Emisyonu Sürdürülebilirlik Raporu",
            "executive_summary": "Bu rapor, Türkiye genelindeki fabrikaların mevcut karbon emisyonlarını ve gelecek yıl için tahminleri analiz etmektedir. Rapor, emisyon azaltma stratejileri ve sürdürülebilir uygulamalar için öneriler sunmaktadır.",
            "current_emissions": emissions_analysis,
            "future_predictions": predictions_analysis,
            "conclusion": f"Türkiye'deki fabrikaların karbon emisyonlarının sürdürülebilir şekilde yönetilmesi, hem çevresel etkilerin azaltılması hem de ekonomik rekabet avantajı sağlanması açısından kritik öneme sahiptir. Bu raporda sunulan analizler ve öneriler, emisyonların azaltılması ve sürdürülebilir üretim uygulamalarının geliştirilmesi için bir yol haritası sunmaktadır."
        }
        
        return report
    
    def generate_reports_from_files(self, emissions_file: str, predictions_file: str, output_file: str) -> None:
        """
        Dosyalardan verileri okur ve sürdürülebilirlik raporunu dosyaya kaydeder
        
        Args:
            emissions_file: Emisyon verileri dosyası
            predictions_file: Emisyon tahminleri dosyası
            output_file: Çıktı dosyası
        """
        # Dosyalardan verileri oku
        with open(emissions_file, "r", encoding="utf-8") as f:
            emissions_data = json.load(f)
        
        with open(predictions_file, "r", encoding="utf-8") as f:
            predictions_data = json.load(f)
        
        # Sürdürülebilirlik raporu oluştur
        report = self.generate_sustainability_report(emissions_data, predictions_data)
        
        # Sonuçları kaydet
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"Sürdürülebilirlik raporu {output_file} dosyasına kaydedildi.")


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenAI GPT kullanarak karbon emisyonu analizleri ve raporları oluşturur"
    )
    
    parser.add_argument("--emissions", default="data/all_turkey_factory_emissions.json",
                        help="Emisyon verilerinin bulunduğu dosya")
    parser.add_argument("--predictions", default="data/carbon_predictions.json",
                        help="Emisyon tahminlerinin bulunduğu dosya")
    parser.add_argument("--output", default="data/gpt_sustainability_report.json",
                        help="Sürdürülebilirlik raporunun kaydedileceği dosya")
    
    args = parser.parse_args()
    
    gpt = GPTIntegration()
    gpt.generate_reports_from_files(args.emissions, args.predictions, args.output)
    
    # Web uygulaması için static klasörüne de kopyala
    static_output = "static/data/gpt_sustainability_report.json"
    gpt.generate_reports_from_files(args.emissions, args.predictions, static_output)
    
    return 0


if __name__ == "__main__":
    main()
