#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Karbon Emisyonu Tahmin Senaryoları
---------------------------------
Bu modül, fabrikaların gelecek yıl karbon emisyonları için farklı senaryolar sunar.
Gemma 3N modeli entegrasyonu ile gelişmiş analizler içerir.
"""

import os
import json
import random
from typing import Dict, List, Any, Optional


class EmissionScenarios:
    """Emisyon senaryoları sınıfı"""
    
    def __init__(self):
        """Sınıfı başlat"""
        pass
    
    def generate_scenarios(self, emissions_data: Dict) -> Dict:
        """
        Farklı senaryolar oluştur
        
        Args:
            emissions_data: Emisyon verileri
            
        Returns:
            Senaryo analizleri
        """
        total_emissions = emissions_data.get("total_annual_emissions_ton", 0)
        
        scenarios = {
            "optimistic": self._create_optimistic_scenario(total_emissions),
            "moderate": self._create_moderate_scenario(total_emissions),
            "pessimistic": self._create_pessimistic_scenario(total_emissions),
            "disruptive_innovation": self._create_disruptive_scenario(total_emissions),
            "climate_policy_shift": self._create_policy_shift_scenario(total_emissions)
        }
        
        return scenarios
    
    def generate_ai_scenarios_with_gpt(self, data: Dict) -> Dict:
        """
        GPT kullanarak AI destekli senaryolar oluşturur
        
        Args:
            data: Emisyon verileri
            
        Returns:
            AI destekli senaryolar
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.gpt_integration import GPTIntegration
            
            gpt = GPTIntegration()
            
            # Senaryo oluşturma için prompt
            prompt_template = """
            Aşağıdaki Türkiye'deki fabrikaların karbon emisyonu verilerini analiz ederek, 2026-2030 yılları için 5 farklı gelecek senaryosu oluştur:

            Toplam Fabrika Sayısı: {total_factory_count}
            Toplam Yıllık Emisyon: {total_annual_emissions_ton:.2f} ton CO2e
            Ortalama Yıllık Emisyon: {average_annual_emissions_ton:.2f} ton CO2e/fabrika

            En çok fabrika bulunan şehirler:
            {top_cities_info}

            Bu verileri analiz ederek aşağıdaki JSON formatında 5 senaryo oluştur:
            {{
                "scenarios": {{
                    "optimistic": {{
                        "name": "İyimser Senaryo",
                        "description": "Yeşil teknolojilere yoğun yatırım",
                        "emission_change_percent": -25,
                        "factors": ["Yenilenebilir enerji", "Teknoloji yatırımı", "AB Green Deal"],
                        "timeline": "2026-2030"
                    }},
                    "moderate": {{
                        "name": "Orta Senaryo", 
                        "description": "Mevcut politikaların devamı",
                        "emission_change_percent": -8,
                        "factors": ["Mevcut düzenlemeler", "Gradual improvements"],
                        "timeline": "2026-2030"
                    }},
                    "pessimistic": {{
                        "name": "Kötümser Senaryo",
                        "description": "Ekonomik zorluklar nedeniyle gecikme",
                        "emission_change_percent": 5,
                        "factors": ["Ekonomik kriz", "Yatırım eksikliği"],
                        "timeline": "2026-2030"
                    }},
                    "disruptive": {{
                        "name": "Çağ Atlamalı Senaryo",
                        "description": "Karbon yakalama teknolojileri devreye girer",
                        "emission_change_percent": -40,
                        "factors": ["Carbon capture", "Breakthrough technologies"],
                        "timeline": "2026-2030"
                    }},
                    "policy_driven": {{
                        "name": "Politika Yönlendirmeli Senaryo",
                        "description": "Katı emisyon düzenlemeleri",
                        "emission_change_percent": -18,
                        "factors": ["Carbon tax", "Strict regulations"],
                        "timeline": "2026-2030"
                    }}
                }},
                "analysis": {{
                    "summary": "Bu senaryolar analizi...",
                    "key_insights": ["İçgörü 1", "İçgörü 2", "İçgörü 3"]
                }}
            }}
            
            Sadece JSON yanıtı ver, başka açıklama ekleme.
            """
            
            # En çok fabrika bulunan şehirleri belirle
            regions = data.get("region_results", [])
            regions_by_factories = sorted(regions, key=lambda x: x.get("factory_count", 0), reverse=True)
            top_cities = regions_by_factories[:5] if len(regions_by_factories) >= 5 else regions_by_factories
            
            top_cities_info = "\\n".join([
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
            
            # GPT ile analiz yap
            ai_response = gpt.generate_analysis(analysis_data, prompt_template)
            
            # AI yanıtından senaryoları çıkar
            if isinstance(ai_response, dict) and "scenarios" in ai_response:
                return ai_response
            else:
                # Fallback: normal senaryoları döndür
                return self.generate_scenarios(data)
                
        except Exception as e:
            print(f"AI senaryo oluşturma hatası: {e}")
            # Hata durumunda normal senaryoları döndür
            return self.generate_scenarios(data)
    
    def _create_optimistic_scenario(self, total_emissions: float) -> Dict:
        """
        İyimser senaryo oluştur
        
        Args:
            total_emissions: Toplam emisyon
            
        Returns:
            Senaryo detayları
        """
        growth_factor = 1.01
        reduction_factor = 0.85
        predicted_emissions = total_emissions * growth_factor * reduction_factor
        
        return {
            "description": "Yüksek teknoloji yatırımı ve düşük büyüme",
            "growth_factor": growth_factor,
            "reduction_factor": reduction_factor,
            "predicted_emissions": predicted_emissions,
            "emission_change": predicted_emissions - total_emissions,
            "emission_change_percent": ((predicted_emissions - total_emissions) / total_emissions) * 100 if total_emissions > 0 else 0,
            "gemma_analysis": {
                "title": "İyimser Senaryo: Teknoloji Odaklı Yeşil Dönüşüm",
                "summary": f"Bu senaryoda, yüksek teknoloji yatırımları ve düşük ekonomik büyüme ile emisyonlarda {abs((predicted_emissions - total_emissions) / total_emissions * 100):.2f}% oranında azalma beklenmektedir.",
                "factors": [
                    "Yenilenebilir enerji kaynaklarına geçiş hızlanacak",
                    "Karbon yakalama teknolojileri yaygınlaşacak",
                    "Enerji verimliliği projeleri artacak",
                    "Döngüsel ekonomi uygulamaları gelişecek",
                    "Düşük karbonlu üretim teşvikleri artacak"
                ],
                "probability": "Orta",
                "impact": "Yüksek",
                "key_industries": ["Yenilenebilir Enerji", "Teknoloji", "AR-GE"],
                "policy_requirements": [
                    "Karbon vergisi uygulaması",
                    "Yenilenebilir enerji teşvikleri",
                    "Yeşil dönüşüm fonları",
                    "Sürdürülebilirlik raporlama zorunluluğu"
                ],
                "regional_impacts": [
                    "Yenilenebilir enerji potansiyeli yüksek bölgelerde ekonomik canlanma",
                    "Sanayi yoğun bölgelerde teknoloji dönüşümü",
                    "Kırsal alanlarda sürdürülebilir tarım uygulamaları",
                    "Şehirlerde akıllı şebeke sistemleri"
                ]
            }
        }
    
    def _create_moderate_scenario(self, total_emissions: float) -> Dict:
        """
        Ilımlı senaryo oluştur
        
        Args:
            total_emissions: Toplam emisyon
            
        Returns:
            Senaryo detayları
        """
        growth_factor = 1.03
        reduction_factor = 0.95
        predicted_emissions = total_emissions * growth_factor * reduction_factor
        
        return {
            "description": "Orta düzey teknoloji yatırımı ve orta düzey büyüme",
            "growth_factor": growth_factor,
            "reduction_factor": reduction_factor,
            "predicted_emissions": predicted_emissions,
            "emission_change": predicted_emissions - total_emissions,
            "emission_change_percent": ((predicted_emissions - total_emissions) / total_emissions) * 100 if total_emissions > 0 else 0,
            "gemma_analysis": {
                "title": "Ilımlı Senaryo: Dengeli Geçiş",
                "summary": f"Bu senaryoda, orta düzey teknoloji yatırımları ve orta düzey ekonomik büyüme ile emisyonlarda {((predicted_emissions - total_emissions) / total_emissions * 100):.2f}% oranında değişim beklenmektedir.",
                "factors": [
                    "Mevcut teknolojilerin kademeli iyileştirilmesi",
                    "Kısmi yenilenebilir enerji entegrasyonu",
                    "Seçici sektörlerde emisyon azaltma çabaları",
                    "Ekonomik büyüme ile sürdürülebilirlik arasında denge",
                    "Orta düzeyde politika değişiklikleri"
                ],
                "probability": "Yüksek",
                "impact": "Orta",
                "key_industries": ["İmalat", "Enerji", "Lojistik"],
                "policy_requirements": [
                    "Kademeli emisyon azaltma hedefleri",
                    "Sektörel teşvikler",
                    "Enerji verimliliği standartları",
                    "Sürdürülebilir finansman araçları"
                ],
                "regional_impacts": [
                    "Büyük şehirlerde kademeli emisyon azaltımı",
                    "Sanayi bölgelerinde verimlilik artışı",
                    "Bölgesel farklılıkların devam etmesi",
                    "Enerji yoğun bölgelerde kısmi dönüşüm"
                ]
            }
        }
    
    def _create_pessimistic_scenario(self, total_emissions: float) -> Dict:
        """
        Kötümser senaryo oluştur
        
        Args:
            total_emissions: Toplam emisyon
            
        Returns:
            Senaryo detayları
        """
        growth_factor = 1.05
        reduction_factor = 0.98
        predicted_emissions = total_emissions * growth_factor * reduction_factor
        
        return {
            "description": "Düşük teknoloji yatırımı ve yüksek büyüme",
            "growth_factor": growth_factor,
            "reduction_factor": reduction_factor,
            "predicted_emissions": predicted_emissions,
            "emission_change": predicted_emissions - total_emissions,
            "emission_change_percent": ((predicted_emissions - total_emissions) / total_emissions) * 100 if total_emissions > 0 else 0,
            "gemma_analysis": {
                "title": "Kötümser Senaryo: Ekonomik Büyüme Odaklı",
                "summary": f"Bu senaryoda, düşük teknoloji yatırımları ve yüksek ekonomik büyüme ile emisyonlarda {((predicted_emissions - total_emissions) / total_emissions * 100):.2f}% oranında artış beklenmektedir.",
                "factors": [
                    "Ekonomik büyümeye öncelik verilmesi",
                    "Fosil yakıt kullanımının devam etmesi",
                    "Teknoloji yatırımlarının yetersiz kalması",
                    "Düşük karbon politikalarının ertelenmesi",
                    "Küresel iklim hedeflerinden sapma"
                ],
                "probability": "Düşük-Orta",
                "impact": "Çok Yüksek (Negatif)",
                "key_industries": ["Fosil Yakıtlar", "Ağır Sanayi", "İnşaat"],
                "policy_requirements": [
                    "Emisyon azaltma hedeflerinin gevşetilmesi",
                    "Kısa vadeli ekonomik teşvikler",
                    "Düşük çevresel standartlar",
                    "Karbon yoğun endüstrilere destek"
                ],
                "regional_impacts": [
                    "Sanayi bölgelerinde artan hava kirliliği",
                    "Enerji yoğun bölgelerde emisyon artışı",
                    "Kırsal alanlarda çevresel bozulma",
                    "Bölgesel eşitsizliklerin artması"
                ]
            }
        }
    
    def _create_disruptive_scenario(self, total_emissions: float) -> Dict:
        """
        Yenilikçi senaryo oluştur
        
        Args:
            total_emissions: Toplam emisyon
            
        Returns:
            Senaryo detayları
        """
        growth_factor = 1.02
        reduction_factor = 0.75
        predicted_emissions = total_emissions * growth_factor * reduction_factor
        
        return {
            "description": "Yenilikçi teknolojilerde beklenmeyen atılımlar",
            "growth_factor": growth_factor,
            "reduction_factor": reduction_factor,
            "predicted_emissions": predicted_emissions,
            "emission_change": predicted_emissions - total_emissions,
            "emission_change_percent": ((predicted_emissions - total_emissions) / total_emissions) * 100 if total_emissions > 0 else 0,
            "gemma_analysis": {
                "title": "Yenilikçi Senaryo: Teknolojik Atılım",
                "summary": f"Bu senaryoda, yenilikçi teknolojilerde beklenmeyen atılımlar ile emisyonlarda {abs((predicted_emissions - total_emissions) / total_emissions * 100):.2f}% oranında azalma beklenmektedir.",
                "factors": [
                    "Yeşil hidrojen teknolojisinde büyük atılım",
                    "Yapay zeka destekli enerji optimizasyonu",
                    "Karbon yakalama teknolojilerinde devrim",
                    "Yeni nesil batarya teknolojileri",
                    "Biyoteknoloji tabanlı endüstriyel süreçler"
                ],
                "probability": "Düşük",
                "impact": "Çok Yüksek (Pozitif)",
                "key_industries": ["Yeşil Teknoloji", "Biyoteknoloji", "Yapay Zeka"],
                "policy_requirements": [
                    "AR-GE yatırımlarının artırılması",
                    "Yenilikçi teknolojilere vergi muafiyeti",
                    "Pilot projelerin desteklenmesi",
                    "Üniversite-sanayi işbirliği teşvikleri"
                ],
                "regional_impacts": [
                    "Teknoloji merkezlerinde ekonomik canlanma",
                    "Enerji üretim bölgelerinde dönüşüm",
                    "Akıllı şehir uygulamalarının yaygınlaşması",
                    "Yeşil teknoloji kümelenmelerinin oluşması"
                ]
            }
        }
    
    def _create_policy_shift_scenario(self, total_emissions: float) -> Dict:
        """
        Politika değişimi senaryosu oluştur
        
        Args:
            total_emissions: Toplam emisyon
            
        Returns:
            Senaryo detayları
        """
        growth_factor = 1.00
        reduction_factor = 0.80
        predicted_emissions = total_emissions * growth_factor * reduction_factor
        
        return {
            "description": "Uluslararası iklim politikalarında köklü değişim",
            "growth_factor": growth_factor,
            "reduction_factor": reduction_factor,
            "predicted_emissions": predicted_emissions,
            "emission_change": predicted_emissions - total_emissions,
            "emission_change_percent": ((predicted_emissions - total_emissions) / total_emissions) * 100 if total_emissions > 0 else 0,
            "gemma_analysis": {
                "title": "Politika Değişimi Senaryosu: Uluslararası İklim Hareketi",
                "summary": f"Bu senaryoda, uluslararası iklim politikalarında köklü değişim ile emisyonlarda {abs((predicted_emissions - total_emissions) / total_emissions * 100):.2f}% oranında azalma beklenmektedir.",
                "factors": [
                    "Küresel karbon fiyatlandırma mekanizması",
                    "Sınırda karbon düzenlemelerinin yaygınlaşması",
                    "Zorunlu sürdürülebilirlik raporlaması",
                    "Uluslararası iklim finansmanının artması",
                    "Sektörel net sıfır hedeflerinin zorunlu hale gelmesi"
                ],
                "probability": "Orta",
                "impact": "Yüksek",
                "key_industries": ["Tüm Sektörler", "Finans", "Danışmanlık"],
                "policy_requirements": [
                    "Uluslararası anlaşmalara tam uyum",
                    "Ulusal mevzuatın güncellenmesi",
                    "Karbon muhasebesi altyapısı",
                    "Yeşil dönüşüm destek programları"
                ],
                "regional_impacts": [
                    "Tüm bölgelerde emisyon azaltma çabaları",
                    "İhracat odaklı bölgelerde hızlı dönüşüm",
                    "Kamu yatırımlarında yeşil kriterlerin uygulanması",
                    "Bölgesel emisyon ticaret sistemlerinin kurulması"
                ]
            }
        }
    
    def generate_scenarios_from_file(self, input_file: str, output_file: str, use_ai: bool = True) -> None:
        """
        Dosyadan emisyon verilerini okur ve senaryo analizlerini dosyaya kaydeder
        
        Args:
            input_file: Girdi dosyası yolu
            output_file: Çıktı dosyası yolu
            use_ai: AI destekli senaryolar mı kullanılacak
        """
        # Dosyadan verileri oku
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Senaryoları oluştur
        if use_ai:
            scenarios = self.generate_ai_scenarios_with_gpt(data)
        else:
            scenarios = self.generate_scenarios(data)
        
        # Sonuçları kaydet
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(scenarios, f, ensure_ascii=False, indent=2)
        
        print(f"Senaryo analizleri {output_file} dosyasına kaydedildi.")


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Karbon emisyonu için farklı senaryolar oluşturur"
    )
    
    parser.add_argument("--input", default="data/all_turkey_factory_emissions.json",
                        help="Emisyon verilerinin bulunduğu dosya")
    parser.add_argument("--output", default="data/emission_scenarios.json",
                        help="Senaryo analizlerinin kaydedileceği dosya")
    parser.add_argument("--ai", action="store_true", default=True,
                        help="AI destekli senaryolar kullan")
    
    args = parser.parse_args()
    
    scenarios = EmissionScenarios()
    scenarios.generate_scenarios_from_file(args.input, args.output, args.ai)
    
    # Web uygulaması için static klasörüne de kopyala
    static_output = "static/data/emission_scenarios.json"
    scenarios.generate_scenarios_from_file(args.input, static_output, args.ai)
    
    return 0


if __name__ == "__main__":
    main()
