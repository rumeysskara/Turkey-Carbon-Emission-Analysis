#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sürdürülebilir Tedarik Zinciri Optimizasyonu için API Modülleri
----------------------------------------------------------------
Bu dosya, sürdürülebilir tedarik zinciri optimizasyonu projesi için
çeşitli veri kaynaklarına erişim sağlayan API fonksiyonlarını içerir.
Özellikle ücretsiz API'lere odaklanılmıştır.
"""

import requests
import json
from typing import Dict, List, Any, Optional, Union


class EmissionDataAPIs:
    """Karbon emisyon verileri için API fonksiyonları"""
    
    @staticmethod
    def get_ghg_protocol_factors() -> Dict:
        """
        GHG Protocol emisyon faktörlerini çeker
        Not: GHG Protocol doğrudan bir API sunmaz, bu fonksiyon
        GHG Protocol'ün paylaştığı verileri işleyen bir örnektir
        
        Returns:
            GHG Protocol emisyon faktörleri
        """
        # Gerçek uygulamada, bu veriyi bir CSV veya Excel dosyasından okuyabilirsiniz
        # Burada örnek bir veri yapısı döndürüyoruz
        return {
            "electricity": {
                "turkey": 0.42,  # kg CO2e/kWh
                "germany": 0.35,
                "usa": 0.45
            },
            "fuel": {
                "diesel": 2.68,  # kg CO2e/liter
                "gasoline": 2.31,
                "lng": 1.86
            }
        }
    
    @staticmethod
    def get_epa_emission_data(category: str) -> Dict:
        """
        EPA'nın açık veri portalından emisyon verilerini çeker
        
        Args:
            category: Emisyon kategorisi (örn. "transportation", "electricity")
            
        Returns:
            Emisyon verileri
        """
        # EPA'nın açık veri portalı için URL
        url = f"https://www.epa.gov/enviro/envirofacts-data-service-api"
        
        # Bu bir örnek implementasyondur, gerçek API çağrısı için EPA'nın
        # dokümantasyonunu incelemeniz gerekir
        
        # Örnek veri döndürüyoruz
        sample_data = {
            "transportation": {
                "passenger_car": 0.17,  # kg CO2e/km
                "light_truck": 0.22,
                "heavy_truck": 0.85
            },
            "electricity": {
                "coal": 0.95,  # kg CO2e/kWh
                "natural_gas": 0.43,
                "renewable": 0.02
            }
        }
        
        return sample_data.get(category, {"error": "Category not found"})
    
    @staticmethod
    def get_world_bank_climate_data(country_code: str) -> Dict:
        """
        Dünya Bankası'nın iklim verilerini çeker
        
        Args:
            country_code: Ülke kodu (ISO 3166-1 alpha-2)
            
        Returns:
            İklim verileri
        """
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/EN.ATM.CO2E.PC?format=json"
        
        response = requests.get(url)
        return response.json()


class SupplierDataAPIs:
    """Tedarikçi verileri için API fonksiyonları"""
    
    @staticmethod
    def search_opencorporates(company_name: str, jurisdiction_code: Optional[str] = None) -> Dict:
        """
        Open Corporates API ile şirket araması yapar (sınırlı ücretsiz erişim)
        
        Args:
            company_name: Aranacak şirket adı
            jurisdiction_code: Ülke/bölge kodu (örn. "tr", "us")
            
        Returns:
            Şirket arama sonuçları
        """
        url = "https://api.opencorporates.com/v0.4/companies/search"
        params = {
            "q": company_name
        }
        
        if jurisdiction_code:
            params["jurisdiction_code"] = jurisdiction_code
            
        response = requests.get(url, params=params)
        return response.json()


class LogisticsDataAPIs:
    """Lojistik ve taşıma verileri için API fonksiyonları"""
    
    @staticmethod
    def get_local_suppliers(lat: float, lon: float, radius: int = 5000, type_: str = "industrial") -> Dict:
        """
        OpenStreetMap Overpass API kullanarak yerel tedarikçileri bulur (ücretsiz)
        
        Args:
            lat: Enlem
            lon: Boylam
            radius: Arama yarıçapı (metre)
            type_: Tesis tipi
            
        Returns:
            Yerel tedarikçi listesi
        """
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Overpass QL sorgusu
        query = f"""
        [out:json];
        (
          node["industrial"="{type_}"](around:{radius},{lat},{lon});
          way["industrial"="{type_}"](around:{radius},{lat},{lon});
          relation["industrial"="{type_}"](around:{radius},{lat},{lon});
        );
        out center;
        """
        
        response = requests.get(overpass_url, params={"data": query})
        return response.json()
    
    @staticmethod
    def geocode_address(address: str) -> Dict:
        """
        Nominatim API kullanarak adres kodlama (ücretsiz)
        
        Args:
            address: Kodlanacak adres
            
        Returns:
            Coğrafi koordinatlar
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        
        headers = {
            "User-Agent": "SustainableSupplyChainOptimizer/1.0"  # Nominatim API bir User-Agent gerektirir
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data and len(data) > 0:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "display_name": data[0]["display_name"]
            }
        
        return {"error": "Address not found"}
    
    @staticmethod
    def calculate_route_distance(origin_lat: float, origin_lon: float, 
                                dest_lat: float, dest_lon: float) -> Dict:
        """
        OSRM (Open Source Routing Machine) API kullanarak rota mesafesi hesaplama (ücretsiz)
        
        Args:
            origin_lat: Başlangıç noktası enlemi
            origin_lon: Başlangıç noktası boylamı
            dest_lat: Varış noktası enlemi
            dest_lon: Varış noktası boylamı
            
        Returns:
            Rota mesafesi ve süresi
        """
        url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        params = {
            "overview": "false"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["code"] == "Ok" and len(data["routes"]) > 0:
            distance_km = data["routes"][0]["distance"] / 1000  # metre -> km
            duration_min = data["routes"][0]["duration"] / 60  # saniye -> dakika
            
            # Basit emisyon hesaplama (örnek)
            # Ortalama kamyon emisyon faktörü: 0.85 kg CO2e/km
            emissions = distance_km * 0.85
            
            return {
                "distance_km": distance_km,
                "duration_min": duration_min,
                "emissions_kg_co2e": emissions
            }
        
        return {"error": "Route calculation failed"}


class LocalResourcesAPIs:
    """Yerel kaynak verileri için API fonksiyonları"""
    
    @staticmethod
    def get_eurostat_data(dataset_code: str, geo: str) -> Dict:
        """
        Eurostat açık verilerini çeker (ücretsiz)
        
        Args:
            dataset_code: Veri seti kodu
            geo: Ülke kodu
            
        Returns:
            Eurostat verileri
        """
        url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset_code}"
        params = {
            "geo": geo,
            "format": "json"
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    @staticmethod
    def get_geographical_indications(region: Optional[str] = None) -> Dict:
        """
        Coğrafi İşaretli Ürünler verisini çeker (örnek)
        
        Args:
            region: Bölge adı (isteğe bağlı)
            
        Returns:
            Coğrafi işaretli ürünler listesi
        """
        # Gerçek API olmadığı için örnek veri döndürüyoruz
        sample_data = {
            "geographical_indications": [
                {
                    "id": "1",
                    "name": "Antep Fıstığı",
                    "region": "Gaziantep",
                    "registration_date": "2000-01-15",
                    "product_type": "Kuruyemiş"
                },
                {
                    "id": "2",
                    "name": "Malatya Kayısısı",
                    "region": "Malatya",
                    "registration_date": "2001-07-24",
                    "product_type": "Meyve"
                }
            ]
        }
        
        if region:
            filtered_data = {
                "geographical_indications": [
                    item for item in sample_data["geographical_indications"]
                    if item["region"].lower() == region.lower()
                ]
            }
            return filtered_data
        
        return sample_data


class RegulationsAPIs:
    """Düzenleyici ve standart verileri için API fonksiyonları"""
    
    @staticmethod
    def get_gri_standards() -> Dict:
        """
        GRI (Global Reporting Initiative) standartlarını çeker (ücretsiz)
        
        Returns:
            GRI standartları listesi
        """
        # Gerçek API olmadığı için örnek veri döndürüyoruz
        sample_data = {
            "standards": [
                {
                    "id": "GRI-301",
                    "name": "Materials",
                    "description": "This Standard includes disclosures on the topic of materials.",
                    "category": "Environmental"
                },
                {
                    "id": "GRI-302",
                    "name": "Energy",
                    "description": "This Standard includes disclosures on the topic of energy.",
                    "category": "Environmental"
                },
                {
                    "id": "GRI-305",
                    "name": "Emissions",
                    "description": "This Standard includes disclosures on the topic of emissions.",
                    "category": "Environmental"
                }
            ]
        }
        
        return sample_data
    
    @staticmethod
    def get_un_sdg_data(goal_number: int) -> Dict:
        """
        Birleşmiş Milletler Sürdürülebilir Kalkınma Hedefleri verilerini çeker (ücretsiz)
        
        Args:
            goal_number: Hedef numarası (1-17)
            
        Returns:
            SDG verileri
        """
        url = f"https://unstats.un.org/SDGAPI/v1/sdg/Goal/{goal_number}/Target/List"
        response = requests.get(url)
        return response.json()


class EnvironmentalDataAPIs:
    """Çevresel veri API'leri"""
    
    @staticmethod
    def get_air_quality_data(lat: float, lon: float) -> Dict:
        """
        OpenAQ API kullanarak hava kalitesi verilerini çeker (ücretsiz)
        
        Args:
            lat: Enlem
            lon: Boylam
            
        Returns:
            Hava kalitesi verileri
        """
        url = "https://api.openaq.org/v2/latest"
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": 10000,  # 10 km
            "limit": 5
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    @staticmethod
    def get_copernicus_climate_data(variable: str, year: int, month: int) -> Dict:
        """
        Copernicus İklim Değişikliği Servisi verilerini çeker (ücretsiz, kayıt gerektirir)
        
        Args:
            variable: İklim değişkeni
            year: Yıl
            month: Ay
            
        Returns:
            İklim verileri
        """
        # Not: Gerçek Copernicus API'si için kayıt ve API anahtarı gereklidir
        # Bu bir örnek implementasyondur
        
        # Örnek veri döndürüyoruz
        sample_data = {
            "temperature": {
                "2023": {
                    "1": 8.2,  # Ocak ayı ortalama sıcaklık (°C)
                    "2": 9.1,
                    "3": 11.3
                }
            },
            "precipitation": {
                "2023": {
                    "1": 65.2,  # Ocak ayı toplam yağış (mm)
                    "2": 48.7,
                    "3": 52.1
                }
            }
        }
        
        if variable in sample_data and str(year) in sample_data[variable] and str(month) in sample_data[variable][str(year)]:
            return {
                "variable": variable,
                "year": year,
                "month": month,
                "value": sample_data[variable][str(year)][str(month)]
            }
        
        return {"error": "Data not found"}


class SupplyChainOptimizer:
    """Tedarik zinciri optimizasyonu için ana sınıf"""
    
    def __init__(self):
        self.emission_apis = EmissionDataAPIs()
        self.supplier_apis = SupplierDataAPIs()
        self.logistics_apis = LogisticsDataAPIs()
        self.local_resources_apis = LocalResourcesAPIs()
        self.regulations_apis = RegulationsAPIs()
        self.environmental_apis = EnvironmentalDataAPIs()
    
    def optimize_routes(self, origin_address: str, destination_addresses: List[str]) -> Dict:
        """
        Rotaları optimize eder (ücretsiz API'ler kullanarak)
        
        Args:
            origin_address: Başlangıç adresi
            destination_addresses: Varış adresleri listesi
            
        Returns:
            Optimize edilmiş rotalar
        """
        # Adresleri koordinatlara dönüştür
        origin_coords = self.logistics_apis.geocode_address(origin_address)
        
        if "error" in origin_coords:
            return {"error": f"Origin address could not be geocoded: {origin_address}"}
        
        destinations = []
        for address in destination_addresses:
            coords = self.logistics_apis.geocode_address(address)
            if "error" not in coords:
                destinations.append({
                    "address": address,
                    "coords": coords
                })
        
        # Rotaları hesapla
        optimized_routes = []
        total_emissions = 0.0
        
        for destination in destinations:
            route_data = self.logistics_apis.calculate_route_distance(
                origin_coords["lat"],
                origin_coords["lon"],
                destination["coords"]["lat"],
                destination["coords"]["lon"]
            )
            
            if "error" not in route_data:
                optimized_routes.append({
                    "origin": origin_address,
                    "destination": destination["address"],
                    "distance_km": route_data["distance_km"],
                    "duration_min": route_data["duration_min"],
                    "emissions_kg_co2e": route_data["emissions_kg_co2e"]
                })
                
                total_emissions += route_data["emissions_kg_co2e"]
        
        return {
            "optimized_routes": optimized_routes,
            "total_emissions": total_emissions
        }
    
    def find_sustainable_suppliers(self, product_type: str, location_address: str, 
                                 max_distance: float) -> Dict:
        """
        Sürdürülebilir tedarikçileri bulur (ücretsiz API'ler kullanarak)
        
        Args:
            product_type: Ürün tipi
            location_address: Konum adresi
            max_distance: Maksimum mesafe (km)
            
        Returns:
            Sürdürülebilir tedarikçi önerileri
        """
        # Adresi koordinatlara dönüştür
        location_coords = self.logistics_apis.geocode_address(location_address)
        
        if "error" in location_coords:
            return {"error": f"Location address could not be geocoded: {location_address}"}
        
        # Yerel tedarikçileri bul
        local_suppliers = self.logistics_apis.get_local_suppliers(
            location_coords["lat"], 
            location_coords["lon"], 
            radius=int(max_distance * 1000)  # km to meters
        )
        
        # Tedarikçileri filtrele ve sırala
        suppliers = []
        
        if "elements" in local_suppliers:
            for element in local_suppliers["elements"]:
                if "tags" in element and product_type.lower() in str(element["tags"]).lower():
                    # Sürdürülebilirlik puanını hesapla (örnek)
                    # Gerçek uygulamada daha karmaşık bir hesaplama yapılabilir
                    
                    # Mesafeye dayalı puan (daha yakın = daha sürdürülebilir)
                    distance_km = element.get("distance", 0) / 1000  # metre -> km
                    distance_score = max(0, 100 - (distance_km / max_distance) * 100)
                    
                    # Çevresel faktörlere dayalı puan (örnek)
                    # Gerçek uygulamada hava kalitesi, enerji kaynakları gibi faktörler kullanılabilir
                    environmental_score = 75  # Örnek değer
                    
                    # Toplam sürdürülebilirlik puanı
                    sustainability_score = (distance_score * 0.6) + (environmental_score * 0.4)
                    
                    suppliers.append({
                        "id": element.get("id"),
                        "name": element.get("tags", {}).get("name", f"Supplier {element.get('id')}"),
                        "distance_km": distance_km,
                        "sustainability_score": sustainability_score,
                        "coordinates": [
                            element.get("lat"), 
                            element.get("lon")
                        ]
                    })
        
        # Sürdürülebilirlik puanına göre sırala
        suppliers.sort(key=lambda x: x["sustainability_score"], reverse=True)
        
        return {
            "suppliers": suppliers,
            "count": len(suppliers)
        }
    
    def calculate_environmental_impact(self, routes: List[Dict], suppliers: List[Dict]) -> Dict:
        """
        Tedarik zincirinin çevresel etkisini hesaplar
        
        Args:
            routes: Rota listesi
            suppliers: Tedarikçi listesi
            
        Returns:
            Çevresel etki analizi
        """
        # Toplam emisyonları hesapla
        total_emissions = sum(route.get("emissions_kg_co2e", 0) for route in routes)
        
        # Tedarikçilerin ortalama sürdürülebilirlik puanını hesapla
        avg_sustainability = 0
        if suppliers:
            avg_sustainability = sum(supplier.get("sustainability_score", 0) for supplier in suppliers) / len(suppliers)
        
        # Yerel kaynak kullanım oranını hesapla
        local_suppliers = [s for s in suppliers if s.get("distance_km", 0) < 50]  # 50 km'den yakın tedarikçiler "yerel" kabul edilir
        local_sourcing_ratio = len(local_suppliers) / len(suppliers) if suppliers else 0
        
        return {
            "total_emissions_kg_co2e": total_emissions,
            "avg_supplier_sustainability": avg_sustainability,
            "local_sourcing_ratio": local_sourcing_ratio,
            "environmental_impact_score": 100 - (total_emissions / 1000) + (avg_sustainability / 2) + (local_sourcing_ratio * 25)
        }


# Kullanım örneği
if __name__ == "__main__":
    # Tedarik zinciri optimizasyonu örneği
    optimizer = SupplyChainOptimizer()
    
    print("Sürdürülebilir Tedarik Zinciri Optimizasyonu Örneği\n")
    
    # Örnek: İstanbul'dan Ankara, İzmir ve Antalya'ya rotaları optimize et
    print("Rotaları optimize ediliyor...")
    optimized_routes = optimizer.optimize_routes(
        "Istanbul, Turkey",
        ["Ankara, Turkey", "Izmir, Turkey", "Antalya, Turkey"]
    )
    
    if "error" not in optimized_routes:
        print("\nOptimize Edilmiş Rotalar:")
        for route in optimized_routes["optimized_routes"]:
            print(f"  {route['origin']} -> {route['destination']}: {route['distance_km']:.1f} km, {route['emissions_kg_co2e']:.2f} kg CO2e")
        print(f"Toplam Emisyon: {optimized_routes['total_emissions']:.2f} kg CO2e")
    else:
        print(f"Hata: {optimized_routes['error']}")
    
    # Örnek: İstanbul'da elektronik parça tedarikçileri bul
    print("\nSürdürülebilir tedarikçiler aranıyor...")
    sustainable_suppliers = optimizer.find_sustainable_suppliers(
        "electronics",
        "Istanbul, Turkey",
        50.0  # 50 km yarıçap
    )
    
    if "error" not in sustainable_suppliers:
        print("\nSürdürülebilir Tedarikçiler:")
        for supplier in sustainable_suppliers["suppliers"]:
            print(f"  {supplier['name']}: {supplier['distance_km']:.1f} km, Sürdürülebilirlik Puanı: {supplier['sustainability_score']:.1f}/100")
    else:
        print(f"Hata: {sustainable_suppliers['error']}")
    
    # Çevresel etki analizi
    if "error" not in optimized_routes and "error" not in sustainable_suppliers:
        print("\nÇevresel etki analizi yapılıyor...")
        environmental_impact = optimizer.calculate_environmental_impact(
            optimized_routes["optimized_routes"],
            sustainable_suppliers["suppliers"]
        )
        
        print("\nÇevresel Etki Analizi:")
        print(f"  Toplam Emisyon: {environmental_impact['total_emissions_kg_co2e']:.2f} kg CO2e")
        print(f"  Ortalama Tedarikçi Sürdürülebilirlik Puanı: {environmental_impact['avg_supplier_sustainability']:.1f}/100")
        print(f"  Yerel Kaynak Kullanım Oranı: {environmental_impact['local_sourcing_ratio']:.2%}")
        print(f"  Çevresel Etki Puanı: {environmental_impact['environmental_impact_score']:.1f}/100")
