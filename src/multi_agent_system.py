#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Çoklu Ajan Mimarisi
------------------
Bu modül, karbon emisyonu analizi ve tahminleri için çoklu ajan mimarisi sağlar.
Her ajan belirli bir görevi yerine getirir ve ajanlar birbirleriyle iletişim kurabilir.
"""

import os
import json
import random
import math
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class Agent(ABC):
    """Temel ajan sınıfı"""
    
    def __init__(self, name: str):
        """
        Ajanı başlat
        
        Args:
            name: Ajan adı
        """
        self.name = name
        self.knowledge_base = {}
        self.messages = []
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Veriyi işle
        
        Args:
            data: İşlenecek veri
            
        Returns:
            İşlenmiş veri
        """
        pass
    
    def send_message(self, recipient: 'Agent', message: Dict) -> None:
        """
        Başka bir ajana mesaj gönder
        
        Args:
            recipient: Alıcı ajan
            message: Mesaj içeriği
        """
        recipient.receive_message(self, message)
    
    def receive_message(self, sender: 'Agent', message: Dict) -> None:
        """
        Başka bir ajandan mesaj al
        
        Args:
            sender: Gönderen ajan
            message: Mesaj içeriği
        """
        self.messages.append({
            "sender": sender.name,
            "content": message
        })
    
    def update_knowledge(self, key: str, value: Any) -> None:
        """
        Bilgi tabanını güncelle
        
        Args:
            key: Anahtar
            value: Değer
        """
        self.knowledge_base[key] = value
    
    def get_knowledge(self, key: str) -> Any:
        """
        Bilgi tabanından değer al
        
        Args:
            key: Anahtar
            
        Returns:
            Değer
        """
        return self.knowledge_base.get(key)


class DataCollectionAgent(Agent):
    """Veri toplama ajanı"""
    
    def __init__(self, name: str = "DataCollector"):
        """Ajanı başlat"""
        super().__init__(name)
    
    def process(self, data_path: str) -> Dict:
        """
        Veri dosyasını işle
        
        Args:
            data_path: Veri dosyası yolu
            
        Returns:
            İşlenmiş veri
        """
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Verileri işle
            processed_data = {
                "total_factory_count": data.get("total_factory_count", 0),
                "total_annual_emissions_ton": data.get("total_annual_emissions_ton", 0),
                "average_annual_emissions_ton": data.get("average_annual_emissions_ton", 0),
                "regions_with_factories": []
            }
            
            # Fabrika bulunan bölgeleri çıkar
            for region in data.get("region_results", []):
                if region.get("factory_count", 0) > 0:
                    processed_data["regions_with_factories"].append({
                        "name": region["region"],
                        "factory_count": region["factory_count"],
                        "total_emissions": region["total_annual_emissions_ton"]
                    })
            
            # Bilgi tabanını güncelle
            self.update_knowledge("processed_data", processed_data)
            
            return processed_data
        
        except Exception as e:
            print(f"Veri işleme hatası: {str(e)}")
            return {}


class AnalysisAgent(Agent):
    """Analiz ajanı"""
    
    def __init__(self, name: str = "Analyzer"):
        """Ajanı başlat"""
        super().__init__(name)
    
    def process(self, data: Dict) -> Dict:
        """
        Veriyi analiz et
        
        Args:
            data: Analiz edilecek veri
            
        Returns:
            Analiz sonuçları
        """
        analysis_results = {
            "summary": {},
            "regional_insights": [],
            "emission_patterns": {},
            "risk_assessment": {}
        }
        
        # Özet istatistikler
        total_factories = data.get("total_factory_count", 0)
        total_emissions = data.get("total_annual_emissions_ton", 0)
        avg_emissions = data.get("average_annual_emissions_ton", 0)
        
        analysis_results["summary"] = {
            "total_factories": total_factories,
            "total_emissions": total_emissions,
            "avg_emissions": avg_emissions,
            "emission_per_factory": total_emissions / total_factories if total_factories > 0 else 0
        }
        
        # Bölgesel içgörüler
        regions = data.get("regions_with_factories", [])
        
        # Emisyon yoğunluğuna göre sırala
        regions_by_emissions = sorted(regions, key=lambda x: x["total_emissions"], reverse=True)
        
        # Fabrika sayısına göre sırala
        regions_by_factories = sorted(regions, key=lambda x: x["factory_count"], reverse=True)
        
        # En yüksek emisyona sahip bölgeler
        top_emission_regions = regions_by_emissions[:5] if len(regions_by_emissions) >= 5 else regions_by_emissions
        
        # En fazla fabrikaya sahip bölgeler
        top_factory_regions = regions_by_factories[:5] if len(regions_by_factories) >= 5 else regions_by_factories
        
        analysis_results["regional_insights"] = {
            "top_emission_regions": top_emission_regions,
            "top_factory_regions": top_factory_regions
        }
        
        # Emisyon paternleri
        if regions:
            # Bölge başına ortalama emisyon
            emissions_per_region = [region["total_emissions"] for region in regions]
            avg_emission_per_region = sum(emissions_per_region) / len(emissions_per_region)
            
            # Emisyon dağılımı
            emission_distribution = {
                "min": min(emissions_per_region),
                "max": max(emissions_per_region),
                "avg": avg_emission_per_region,
                "median": sorted(emissions_per_region)[len(emissions_per_region) // 2]
            }
            
            analysis_results["emission_patterns"] = {
                "emission_distribution": emission_distribution
            }
        
        # Risk değerlendirmesi
        high_emission_regions = [region for region in regions if region["total_emissions"] > avg_emissions * 1.5]
        low_emission_regions = [region for region in regions if region["total_emissions"] < avg_emissions * 0.5]
        
        analysis_results["risk_assessment"] = {
            "high_emission_regions": high_emission_regions,
            "low_emission_regions": low_emission_regions,
            "high_risk_count": len(high_emission_regions),
            "low_risk_count": len(low_emission_regions)
        }
        
        # Bilgi tabanını güncelle
        self.update_knowledge("analysis_results", analysis_results)
        
        return analysis_results


class PredictionAgent(Agent):
    """Tahmin ajanı"""
    
    def __init__(self, name: str = "Predictor"):
        """Ajanı başlat"""
        super().__init__(name)
        
        # Büyüme faktörleri (sektöre göre)
        self.growth_factors = {
            "factory": 1.02,  # Genel fabrika
            "manufacturing": 1.03,  # İmalat
            "chemical": 1.04,  # Kimya
            "textile": 1.01,  # Tekstil
            "food": 1.02,  # Gıda
            "electronics": 1.05,  # Elektronik
            "metal": 1.03,  # Metal
            "automotive": 1.04,  # Otomotiv
            "cement": 1.02,  # Çimento
            "steel": 1.03,  # Çelik
            "glass": 1.02,  # Cam
            "paper": 1.01,  # Kağıt
            "plastic": 1.03,  # Plastik
            "furniture": 1.02,  # Mobilya
            "machinery": 1.03  # Makine
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
    
    def process(self, data: Dict) -> Dict:
        """
        Gelecek yıl tahminlerini yap
        
        Args:
            data: Tahmin için kullanılacak veri
            
        Returns:
            Tahmin sonuçları
        """
        predictions = {
            "summary": {},
            "regional_predictions": [],
            "future_scenarios": {}
        }
        
        # Genel tahminler
        total_emissions = data.get("total_annual_emissions_ton", 0)
        
        # Rastgele büyüme faktörü (1.01 ile 1.05 arası)
        growth_factor = 1.01 + random.random() * 0.04
        
        # Teknoloji yatırımı seviyesi
        tech_levels = ["low_tech", "medium_tech", "high_tech"]
        tech_level = random.choice(tech_levels)
        reduction_factor = self.reduction_factors.get(tech_level, 0.98)
        
        # Gelecek yıl emisyonlarını hesapla
        predicted_emissions = total_emissions * growth_factor * reduction_factor
        
        # Emisyon değişimini hesapla
        emission_change = predicted_emissions - total_emissions
        emission_change_percent = (emission_change / total_emissions) * 100 if total_emissions > 0 else 0
        
        predictions["summary"] = {
            "current_emissions": total_emissions,
            "predicted_emissions": predicted_emissions,
            "emission_change": emission_change,
            "emission_change_percent": emission_change_percent,
            "growth_factor": growth_factor,
            "tech_level": tech_level,
            "reduction_factor": reduction_factor
        }
        
        # Bölgesel tahminler
        regions = data.get("regions_with_factories", [])
        regional_predictions = []
        
        for region in regions:
            region_name = region["name"].split(",")[0]
            region_emissions = region["total_emissions"]
            
            # Şehre özel büyüme faktörü
            city_factor = self.city_growth_factors.get(region_name, 1.02)
            
            # Rastgele varyasyon ekle (+/- %5)
            variation = 1 + (random.random() * 0.1 - 0.05)
            
            # Şehir için teknoloji seviyesi
            city_tech_level = random.choice(tech_levels)
            city_reduction = self.reduction_factors.get(city_tech_level, 0.98)
            
            # Şehir için gelecek yıl emisyonlarını hesapla
            predicted_city_emissions = region_emissions * city_factor * variation * city_reduction
            
            # Emisyon değişimini hesapla
            city_emission_change = predicted_city_emissions - region_emissions
            city_change_percent = (city_emission_change / region_emissions) * 100 if region_emissions > 0 else 0
            
            regional_predictions.append({
                "region": region["name"],
                "current_emissions": region_emissions,
                "predicted_emissions": predicted_city_emissions,
                "emission_change": city_emission_change,
                "emission_change_percent": city_change_percent,
                "growth_factor": city_factor,
                "tech_level": city_tech_level
            })
        
        predictions["regional_predictions"] = regional_predictions
        
        # Farklı senaryolar
        scenarios = {
            "optimistic": {
                "description": "Yüksek teknoloji yatırımı ve düşük büyüme",
                "growth_factor": 1.01,
                "reduction_factor": 0.85,
                "predicted_emissions": total_emissions * 1.01 * 0.85
            },
            "moderate": {
                "description": "Orta düzey teknoloji yatırımı ve orta düzey büyüme",
                "growth_factor": 1.03,
                "reduction_factor": 0.95,
                "predicted_emissions": total_emissions * 1.03 * 0.95
            },
            "pessimistic": {
                "description": "Düşük teknoloji yatırımı ve yüksek büyüme",
                "growth_factor": 1.05,
                "reduction_factor": 0.98,
                "predicted_emissions": total_emissions * 1.05 * 0.98
            }
        }
        
        predictions["future_scenarios"] = scenarios
        
        # Bilgi tabanını güncelle
        self.update_knowledge("predictions", predictions)
        
        return predictions


class RecommendationAgent(Agent):
    """Öneri ajanı"""
    
    def __init__(self, name: str = "Recommender"):
        """Ajanı başlat"""
        super().__init__(name)
    
    def process(self, data: Dict) -> Dict:
        """
        Öneriler oluştur
        
        Args:
            data: Öneri oluşturmak için kullanılacak veri
            
        Returns:
            Öneriler
        """
        recommendations = {
            "emission_reduction": [],
            "policy_suggestions": [],
            "technology_investments": [],
            "strategic_recommendations": {
                "short_term": [],
                "medium_term": [],
                "long_term": []
            }
        }
        
        # Emisyon azaltma önerileri
        emission_reduction_options = [
            "Enerji verimliliği projelerinin uygulanması",
            "Yenilenebilir enerji kaynaklarının kullanımının artırılması",
            "Karbon yakalama ve depolama teknolojilerinin değerlendirilmesi",
            "Üretim süreçlerinin optimizasyonu",
            "Atık yönetimi ve geri dönüşüm sistemlerinin iyileştirilmesi",
            "Enerji tasarruflu ekipmanların kullanımı",
            "Isı geri kazanım sistemlerinin kurulması",
            "Bina yalıtımının iyileştirilmesi",
            "Düşük karbonlu yakıtlara geçiş",
            "Çalışanlar için enerji tasarrufu eğitimleri",
            "Karbon ayak izi izleme ve raporlama sistemlerinin kurulması",
            "Tedarik zinciri optimizasyonu ile lojistik kaynaklı emisyonların azaltılması"
        ]
        
        # Politika önerileri
        policy_suggestions = [
            "Emisyon yoğun bölgelerde daha sıkı düzenlemeler getirilmesi",
            "Düşük karbonlu üretim için teşviklerin artırılması",
            "Karbon fiyatlandırma mekanizmalarının uygulanması",
            "Yeşil sertifikasyon programlarının geliştirilmesi",
            "Enerji verimliliği standartlarının yükseltilmesi",
            "Yenilenebilir enerji kullanımı için vergi indirimleri",
            "Endüstriyel simbiyoz projelerinin teşvik edilmesi",
            "Sürdürülebilirlik raporlamasının zorunlu hale getirilmesi",
            "Döngüsel ekonomi prensiplerinin teşvik edilmesi",
            "Yeşil finansman olanaklarının artırılması",
            "Karbon nötr hedeflerin belirlenmesi",
            "Sektörel emisyon azaltma hedeflerinin belirlenmesi"
        ]
        
        # Teknoloji yatırımları
        technology_investments = [
            "Enerji verimli üretim teknolojilerine yatırım yapılması",
            "Yenilenebilir enerji sistemlerinin kurulması",
            "Dijital izleme ve optimizasyon sistemlerinin uygulanması",
            "Yapay zeka destekli enerji yönetim sistemleri",
            "Nesnelerin interneti (IoT) tabanlı sensör ağları",
            "Akıllı fabrika sistemleri",
            "Blok zinciri tabanlı tedarik zinciri izleme",
            "Karbon yakalama teknolojileri",
            "Biyobazlı malzemelerin kullanımı",
            "Hidrojen ve yakıt hücresi teknolojileri",
            "Enerji depolama sistemleri",
            "Elektrikli araç filosuna geçiş"
        ]
        
        # Kısa vadeli stratejik öneriler
        short_term = [
            "Enerji verimliliği denetimlerinin gerçekleştirilmesi",
            "Emisyon izleme sistemlerinin kurulması",
            "Çalışanlar için sürdürülebilirlik eğitimlerinin düzenlenmesi",
            "Enerji tüketiminin optimize edilmesi",
            "Atık azaltma programlarının başlatılması",
            "Tedarikçi değerlendirme kriterlerine sürdürülebilirlik ölçütlerinin eklenmesi",
            "Karbon ayak izi hesaplama metodolojisinin geliştirilmesi",
            "Sürdürülebilirlik hedeflerinin belirlenmesi",
            "Enerji tasarruf kampanyalarının başlatılması",
            "İç karbon fiyatlandırma sisteminin oluşturulması"
        ]
        
        # Orta vadeli stratejik öneriler
        medium_term = [
            "Enerji verimli ekipmanların yenilenmesi",
            "Yenilenebilir enerji yatırımlarının yapılması",
            "Tedarik zinciri optimizasyonu projelerinin başlatılması",
            "Sürdürülebilir ürün tasarımına geçiş",
            "Karbon nötr pilot tesislerin kurulması",
            "Endüstriyel simbiyoz projelerinin geliştirilmesi",
            "Dijital dönüşüm projelerinin hayata geçirilmesi",
            "Sürdürülebilir hammadde tedarik stratejilerinin geliştirilmesi",
            "Ürün yaşam döngüsü analizlerinin yapılması",
            "Yeşil bina sertifikasyonu"
        ]
        
        # Uzun vadeli stratejik öneriler
        long_term = [
            "Karbon nötr üretim hedeflerinin belirlenmesi",
            "Döngüsel ekonomi modellerinin uygulanması",
            "Endüstriyel simbiyoz projelerinin geliştirilmesi",
            "Tam entegre sürdürülebilirlik yönetim sistemleri",
            "Yenilikçi düşük karbonlu teknolojilerin geliştirilmesi",
            "Sürdürülebilir iş modellerine tam geçiş",
            "Tedarik zincirinin tamamen dekarbonizasyonu",
            "Endüstriyel ekosistemlerin kurulması",
            "Sıfır atık tesislerine dönüşüm",
            "Karbon negatif teknolojilerin uygulanması"
        ]
        
        # Rastgele öneriler seç
        recommendations["emission_reduction"] = random.sample(emission_reduction_options, min(7, len(emission_reduction_options)))
        recommendations["policy_suggestions"] = random.sample(policy_suggestions, min(5, len(policy_suggestions)))
        recommendations["technology_investments"] = random.sample(technology_investments, min(6, len(technology_investments)))
        
        recommendations["strategic_recommendations"]["short_term"] = random.sample(short_term, min(5, len(short_term)))
        recommendations["strategic_recommendations"]["medium_term"] = random.sample(medium_term, min(5, len(medium_term)))
        recommendations["strategic_recommendations"]["long_term"] = random.sample(long_term, min(5, len(long_term)))
        
        # Bilgi tabanını güncelle
        self.update_knowledge("recommendations", recommendations)
        
        return recommendations


class ReportGenerationAgent(Agent):
    """Rapor oluşturma ajanı"""
    
    def __init__(self, name: str = "ReportGenerator"):
        """Ajanı başlat"""
        super().__init__(name)
    
    def process(self, data: Dict) -> Dict:
        """
        Rapor oluştur
        
        Args:
            data: Rapor oluşturmak için kullanılacak veri
            
        Returns:
            Rapor
        """
        report = {
            "title": "Türkiye'deki Fabrikaların Karbon Emisyonu Sürdürülebilirlik Raporu",
            "executive_summary": "",
            "current_emissions": {},
            "future_predictions": {},
            "recommendations": {},
            "conclusion": ""
        }
        
        # Yönetici özeti
        total_factories = data.get("total_factory_count", 0)
        total_emissions = data.get("total_annual_emissions_ton", 0)
        
        executive_summary = (
            f"Bu rapor, Türkiye genelindeki {total_factories} fabrikanın mevcut karbon emisyonlarını ve "
            f"gelecek yıl için tahminleri analiz etmektedir. Toplam yıllık emisyon {total_emissions:.2f} ton CO2e olarak "
            f"hesaplanmıştır. Rapor, emisyon azaltma stratejileri ve sürdürülebilir uygulamalar için öneriler sunmaktadır."
        )
        
        report["executive_summary"] = executive_summary
        
        # Mevcut emisyonlar
        analysis_results = data.get("analysis_results", {})
        report["current_emissions"] = analysis_results
        
        # Gelecek tahminleri
        predictions = data.get("predictions", {})
        report["future_predictions"] = predictions
        
        # Öneriler
        recommendations = data.get("recommendations", {})
        report["recommendations"] = recommendations
        
        # Sonuç
        conclusion = (
            f"Türkiye'deki fabrikaların karbon emisyonlarının sürdürülebilir şekilde yönetilmesi, "
            f"hem çevresel etkilerin azaltılması hem de ekonomik rekabet avantajı sağlanması açısından kritik öneme sahiptir. "
            f"Bu raporda sunulan analizler ve öneriler, emisyonların azaltılması ve sürdürülebilir üretim uygulamalarının "
            f"geliştirilmesi için bir yol haritası sunmaktadır."
        )
        
        report["conclusion"] = conclusion
        
        # Bilgi tabanını güncelle
        self.update_knowledge("report", report)
        
        return report


class MultiAgentSystem:
    """Çoklu ajan sistemi"""
    
    def __init__(self):
        """Sistemi başlat"""
        # Ajanları oluştur
        self.data_collector = DataCollectionAgent()
        self.analyzer = AnalysisAgent()
        self.predictor = PredictionAgent()
        self.recommender = RecommendationAgent()
        self.report_generator = ReportGenerationAgent()
        
        # Ajanları listeye ekle
        self.agents = [
            self.data_collector,
            self.analyzer,
            self.predictor,
            self.recommender,
            self.report_generator
        ]
    
    def run(self, data_path: str) -> Dict:
        """
        Sistemi çalıştır
        
        Args:
            data_path: Veri dosyası yolu
            
        Returns:
            Sonuç raporu
        """
        # Veri toplama
        print("Veri toplama ajanı çalışıyor...")
        processed_data = self.data_collector.process(data_path)
        
        # Analiz
        print("Analiz ajanı çalışıyor...")
        analysis_results = self.analyzer.process(processed_data)
        
        # Tahmin
        print("Tahmin ajanı çalışıyor...")
        predictions = self.predictor.process(processed_data)
        
        # Öneriler
        print("Öneri ajanı çalışıyor...")
        recommendations = self.recommender.process({**processed_data, **analysis_results, **predictions})
        
        # Rapor oluşturma
        print("Rapor oluşturma ajanı çalışıyor...")
        report = self.report_generator.process({
            **processed_data,
            "analysis_results": analysis_results,
            "predictions": predictions,
            "recommendations": recommendations
        })
        
        return report
    
    def save_report(self, report: Dict, output_path: str) -> None:
        """
        Raporu dosyaya kaydet
        
        Args:
            report: Rapor
            output_path: Çıktı dosyası yolu
        """
        # Dizini oluştur
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Raporu kaydet
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"Rapor {output_path} dosyasına kaydedildi.")


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Çoklu ajan sistemi ile karbon emisyonu analizi ve tahminleri"
    )
    
    parser.add_argument("--input", default="data/all_turkey_factory_emissions.json",
                        help="Emisyon verilerinin bulunduğu dosya")
    parser.add_argument("--output", default="data/multi_agent_report.json",
                        help="Raporun kaydedileceği dosya")
    
    args = parser.parse_args()
    
    # Çoklu ajan sistemini başlat
    system = MultiAgentSystem()
    
    # Sistemi çalıştır
    report = system.run(args.input)
    
    # Raporu kaydet
    system.save_report(report, args.output)
    
    # Web uygulaması için static klasörüne de kopyala
    static_output = "static/data/multi_agent_report.json"
    system.save_report(report, static_output)
    
    return 0


if __name__ == "__main__":
    main()
