// Sürdürülebilir Tedarik Zinciri Optimizasyonu JavaScript

// Global değişkenler
let routesMap = null;
let suppliersMap = null;
let routesData = null;
let suppliersData = null;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // Form gönderme işleyicileri
    document.getElementById('route-form').addEventListener('submit', optimizeRoutes);
    document.getElementById('supplier-form').addEventListener('submit', findSuppliers);
    
    // Haritaları başlat
    initMaps();
    
    // Sayfa içi navigasyon için smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Haritaları başlat
function initMaps() {
    // Rota haritası
    routesMap = L.map('routes-map').setView([39.0, 35.0], 5); // Türkiye'nin merkezi
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(routesMap);
    
    // Tedarikçi haritası
    suppliersMap = L.map('suppliers-map').setView([39.0, 35.0], 5); // Türkiye'nin merkezi
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(suppliersMap);
}

// Rotaları optimize et
async function optimizeRoutes(e) {
    e.preventDefault();
    
    const origin = document.getElementById('origin').value;
    const destinationsText = document.getElementById('destinations').value;
    const destinations = destinationsText.split('\n').filter(line => line.trim() !== '');
    
    if (destinations.length === 0) {
        alert('En az bir varış noktası belirtmelisiniz.');
        return;
    }
    
    try {
        // Yükleniyor göstergesi eklenebilir
        document.getElementById('routes-result').style.display = 'none';
        
        // API isteği
        const response = await fetch('/optimize-routes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin: origin,
                destinations: destinations
            })
        });
        
        if (!response.ok) {
            throw new Error('API isteği başarısız oldu.');
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Veriyi sakla
        routesData = data;
        
        // Sonuçları göster
        displayRouteResults(data);
        
        // Çevresel etki analizi yap
        if (suppliersData) {
            analyzeEnvironmentalImpact();
        }
    } catch (error) {
        alert('Hata: ' + error.message);
    }
}

// Rota sonuçlarını göster
function displayRouteResults(data) {
    // Haritayı temizle
    routesMap.eachLayer(layer => {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
            routesMap.removeLayer(layer);
        }
    });
    
    // Tabloyu temizle
    const tableBody = document.getElementById('routes-table');
    tableBody.innerHTML = '';
    
    // Toplam emisyonu göster
    document.getElementById('total-emissions').textContent = data.total_emissions.toFixed(2) + ' kg CO2e';
    
    // Rotaları göster
    const bounds = [];
    
    data.optimized_routes.forEach(route => {
        // Tabloya ekle
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${route.origin}</td>
            <td>${route.destination}</td>
            <td>${route.distance_km.toFixed(1)} km</td>
            <td>${route.emissions_kg_co2e.toFixed(2)} kg CO2e</td>
        `;
        tableBody.appendChild(row);
        
        // Haritaya ekle (basitleştirilmiş, gerçek uygulamada geocoding gerekir)
        // Bu örnek için başlangıç ve varış noktalarını rastgele konumlara yerleştiriyoruz
        // Gerçek uygulamada Nominatim veya başka bir geocoding servisi kullanılmalıdır
        const originCoords = simulateGeocode(route.origin);
        const destCoords = simulateGeocode(route.destination);
        
        const originMarker = L.marker(originCoords).addTo(routesMap)
            .bindPopup(`<b>Başlangıç:</b> ${route.origin}`);
        
        const destMarker = L.marker(destCoords).addTo(routesMap)
            .bindPopup(`<b>Varış:</b> ${route.destination}<br><b>Mesafe:</b> ${route.distance_km.toFixed(1)} km<br><b>Emisyon:</b> ${route.emissions_kg_co2e.toFixed(2)} kg CO2e`);
        
        const routeLine = L.polyline([originCoords, destCoords], {
            color: '#28a745',
            weight: 3,
            opacity: 0.7
        }).addTo(routesMap);
        
        bounds.push(originCoords);
        bounds.push(destCoords);
    });
    
    // Haritayı sınırlara göre ayarla
    if (bounds.length > 0) {
        routesMap.fitBounds(bounds);
    }
    
    // Sonuçları göster
    document.getElementById('routes-result').style.display = 'block';
}

// Tedarikçileri bul
async function findSuppliers(e) {
    e.preventDefault();
    
    const productType = document.getElementById('product-type').value;
    const location = document.getElementById('location').value;
    const maxDistance = document.getElementById('max-distance').value;
    
    try {
        // Yükleniyor göstergesi eklenebilir
        document.getElementById('suppliers-result').style.display = 'none';
        
        // API isteği
        const response = await fetch('/find-suppliers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_type: productType,
                location: location,
                max_distance: parseFloat(maxDistance)
            })
        });
        
        if (!response.ok) {
            throw new Error('API isteği başarısız oldu.');
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Veriyi sakla
        suppliersData = data;
        
        // Sonuçları göster
        displaySupplierResults(data);
        
        // Çevresel etki analizi yap
        if (routesData) {
            analyzeEnvironmentalImpact();
        }
    } catch (error) {
        alert('Hata: ' + error.message);
    }
}

// Tedarikçi sonuçlarını göster
function displaySupplierResults(data) {
    // Haritayı temizle
    suppliersMap.eachLayer(layer => {
        if (layer instanceof L.Marker || layer instanceof L.Circle) {
            suppliersMap.removeLayer(layer);
        }
    });
    
    // Tabloyu temizle
    const tableBody = document.getElementById('suppliers-table');
    tableBody.innerHTML = '';
    
    // Konum merkezi (basitleştirilmiş)
    const locationCoords = simulateGeocode(document.getElementById('location').value);
    
    // Konum merkezini haritaya ekle
    const locationMarker = L.marker(locationCoords).addTo(suppliersMap)
        .bindPopup(`<b>Konum:</b> ${document.getElementById('location').value}`);
    
    // Arama yarıçapını haritaya ekle
    const searchRadius = parseFloat(document.getElementById('max-distance').value) * 1000; // km to m
    const radiusCircle = L.circle(locationCoords, {
        radius: searchRadius,
        color: '#28a745',
        fillColor: '#28a745',
        fillOpacity: 0.1
    }).addTo(suppliersMap);
    
    // Tedarikçileri göster
    const bounds = [locationCoords];
    
    if (data.suppliers && data.suppliers.length > 0) {
        data.suppliers.forEach(supplier => {
            // Tabloya ekle
            const row = document.createElement('tr');
            
            // Sürdürülebilirlik puanına göre renk sınıfı
            let sustainabilityClass = '';
            if (supplier.sustainability_score >= 70) {
                sustainabilityClass = 'sustainability-high';
            } else if (supplier.sustainability_score >= 40) {
                sustainabilityClass = 'sustainability-medium';
            } else {
                sustainabilityClass = 'sustainability-low';
            }
            
            row.innerHTML = `
                <td>${supplier.name || 'İsimsiz Tedarikçi'}</td>
                <td>${supplier.distance_km.toFixed(1)} km</td>
                <td class="${sustainabilityClass}">${supplier.sustainability_score.toFixed(1)}/100</td>
            `;
            tableBody.appendChild(row);
            
            // Haritaya ekle
            const supplierCoords = supplier.coordinates ? 
                [supplier.coordinates[0], supplier.coordinates[1]] : 
                simulateSupplierLocation(locationCoords, supplier.distance_km);
            
            const supplierMarker = L.marker(supplierCoords).addTo(suppliersMap)
                .bindPopup(`<b>Tedarikçi:</b> ${supplier.name || 'İsimsiz Tedarikçi'}<br><b>Mesafe:</b> ${supplier.distance_km.toFixed(1)} km<br><b>Sürdürülebilirlik Puanı:</b> ${supplier.sustainability_score.toFixed(1)}/100`);
            
            bounds.push(supplierCoords);
        });
    } else {
        // Tedarikçi bulunamadı mesajı
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">Tedarikçi bulunamadı.</td></tr>';
    }
    
    // Haritayı sınırlara göre ayarla
    if (bounds.length > 0) {
        suppliersMap.fitBounds(bounds);
    }
    
    // Sonuçları göster
    document.getElementById('suppliers-result').style.display = 'block';
}

// Çevresel etki analizi
async function analyzeEnvironmentalImpact() {
    if (!routesData || !routesData.optimized_routes || !suppliersData || !suppliersData.suppliers) {
        return;
    }
    
    try {
        // API isteği
        const response = await fetch('/analyze-impact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                routes: routesData.optimized_routes,
                suppliers: suppliersData.suppliers
            })
        });
        
        if (!response.ok) {
            throw new Error('API isteği başarısız oldu.');
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Sonuçları göster
        document.getElementById('impact-emissions').textContent = data.total_emissions_kg_co2e.toFixed(2) + ' kg CO2e';
        document.getElementById('impact-score').textContent = data.environmental_impact_score.toFixed(1) + '/100';
        document.getElementById('avg-sustainability').textContent = data.avg_supplier_sustainability.toFixed(1) + '/100';
        document.getElementById('local-sourcing').textContent = (data.local_sourcing_ratio * 100).toFixed(1) + '%';
        
        // Sonuçları göster
        document.getElementById('impact-result').style.display = 'block';
    } catch (error) {
        console.error('Çevresel etki analizi hatası:', error);
    }
}

// Yardımcı fonksiyonlar

// Adres için simüle edilmiş koordinatlar (gerçek uygulamada geocoding kullanılmalıdır)
function simulateGeocode(address) {
    // Basit bir hash fonksiyonu
    const hash = s => s.split('').reduce((a, b) => (((a << 5) - a) + b.charCodeAt(0)) | 0, 0);
    
    // Türkiye sınırları içinde rastgele bir konum
    const turkeyBounds = {
        minLat: 36.0, maxLat: 42.0,
        minLng: 26.0, maxLng: 45.0
    };
    
    // Adrese göre deterministik bir konum üret
    const h = hash(address);
    const lat = turkeyBounds.minLat + (Math.abs(h % 1000) / 1000) * (turkeyBounds.maxLat - turkeyBounds.minLat);
    const lng = turkeyBounds.minLng + (Math.abs((h >> 10) % 1000) / 1000) * (turkeyBounds.maxLng - turkeyBounds.minLng);
    
    return [lat, lng];
}

// Merkez etrafında belirli mesafede rastgele bir konum üret
function simulateSupplierLocation(center, distanceKm) {
    // Dünya üzerinde 1 derece yaklaşık 111 km
    const degreesPerKm = 1 / 111;
    
    // Rastgele bir açı
    const angle = Math.random() * Math.PI * 2;
    
    // Mesafeyi dereceye çevir (tam mesafenin %50-%100'ü arasında rastgele)
    const distance = distanceKm * degreesPerKm * (0.5 + Math.random() * 0.5);
    
    // Yeni koordinatları hesapla
    const lat = center[0] + distance * Math.cos(angle);
    const lng = center[1] + distance * Math.sin(angle);
    
    return [lat, lng];
}
