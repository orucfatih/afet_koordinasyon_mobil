# sample_data.py

TEAM_DATA = [
    ("T001", "Ahmet Yılmaz", "AFAD", "Müsait", "0555-111-2233"),
    ("T002", "Mehmet Demir", "STK-A", "Görevde", "0555-222-3344"),
    ("T003", "Ayşe Kaya", "AFAD", "Müsait", "0555-333-4455"),
    ("T004", "Ali Öztürk", "STK-B", "Görevde", "0555-444-5566"),
    ("T005", "Fatma Şahin", "AFAD", "Müsait", "0555-555-6677")
]

NOTIFICATIONS = [
    "Acil: Su Baskını - Mahmutlar Mah.",
    "Yangın İhbarı - Atatürk Cad.",
    "Bina Hasarı - Cumhuriyet Mah."
]

TASKS = [
    "Arama Kurtarma - Merkez",
    "Gıda Dağıtımı - Doğu Bölgesi",
    "Sağlık Taraması - Batı Bölgesi"
]

MESSAGES = [
    {
        "sender": "Saha Ekibi 1",
        "message": "Bölgede elektrik kesintisi devam ediyor.",
        "timestamp": "14:30"
    },
    {
        "sender": "112 Acil",
        "message": "2 ambulans bölgeye yönlendirildi.",
        "timestamp": "14:45"
    },
    {
        "sender": "İtfaiye",
        "message": "Yangın kontrol altına alındı.",
        "timestamp": "15:00"
    }
]

NOTIFICATION_DETAILS = {
    "Acil: Su Baskını - Mahmutlar Mah.": 
        "Konum: Mahmutlar Mahallesi, Ana Cadde No:15\n"
        "Durum: Zemin katta su baskını\n"
        "Etkilenen Alan: Yaklaşık 500m²\n"
        "İhtiyaçlar: Su tahliye pompası, kum torbaları\n"
        "İletişim: Mahalle Muhtarı (555-123-4567)",
    "Yangın İhbarı - Atatürk Cad.": 
        "Konum: Atatürk Caddesi No:78\n"
        "Durum: 3 katlı binada yangın\n"
        "Risk: Yüksek\n"
        "Müdahale Eden Ekip: İtfaiye 3 araç\n"
        "Destek İhtiyacı: Ambulans, Güvenlik",
    "Bina Hasarı - Cumhuriyet Mah.":
        "Konum: Cumhuriyet Mahallesi, Okul Sokak\n"
        "Yapı Türü: 5 katlı apartman\n"
        "Hasar Durumu: Orta seviye çatlaklar\n"
        "Risk Değerlendirmesi: Yapısal analiz gerekli\n"
        "Tahliye Durumu: Kısmi tahliye önerisi"
}

TASK_DETAILS = {
    "Arama Kurtarma - Merkez": 
        "Görev Tipi: Arama Kurtarma\n"
        "Lokasyon: Şehir Merkezi, Park Caddesi\n"
        "Ekip Sayısı: 3 ekip (12 personel)\n"
        "Ekipman: Termal kamera, Arama köpeği\n"
        "Durum: Devam ediyor\n"
        "Başlangıç: 10:30\n"
        "Tahmini Bitiş: 18:00",
    "Gıda Dağıtımı - Doğu Bölgesi":
        "Görev: Gıda ve Su Dağıtımı\n"
        "Bölge: Doğu Mahalleler\n"
        "Dağıtım Noktası Sayısı: 5\n"
        "Görevli Personel: 15\n"
        "Araç Sayısı: 3 kamyonet\n"
        "Dağıtılacak: 1000 gıda kolisi, 2000L su",
    "Sağlık Taraması - Batı Bölgesi":
        "Görev: Mobil Sağlık Taraması\n"
        "Kapsam: 5 mahalle\n"
        "Sağlık Personeli: 8 doktor, 12 hemşire\n"
        "Mobil Ünite: 2 araç\n"
        "Hedef Kitle: Yaşlılar ve çocuklar öncelikli\n"
        "İlerleme: 2/5 mahalle tamamlandı"
}

AFAD_TEAMS = {
    "Arama Kurtarma Ekibi 1": {
        "type": "Arama Kurtarma Ekibi",
        "status": "Aktif Görevde",
        "active_task": "Deprem bölgesinde arama çalışması",
        "task_location": "Kahramanmaraş Merkez",
        "task_start_time": "2024-03-16 08:00",
        "task_priority": "Acil",
        "personnel": [
            {
                "name": "Ahmet Yılmaz",
                "title": "Ekip Lideri",
                "phone": "555-0001",
                "home_phone": "312-0001",
                "email": "ahmet@example.com",
                "address": "Ankara, Çankaya",
                "specialization": "Arama Kurtarma Uzmanı",
                "experience": "10",
                "status": "Aktif",
                "last_location": "Kahramanmaraş",
                "last_update": "10 dk önce"
            },
            {
                "name": "Mehmet Demir",
                "title": "Kurtarma Uzmanı",
                "phone": "555-0002",
                "home_phone": "312-0002",
                "email": "mehmet@example.com",
                "address": "Ankara, Keçiören",
                "specialization": "Teknik Kurtarma",
                "experience": "8",
                "status": "Aktif",
                "last_location": "Kahramanmaraş",
                "last_update": "15 dk önce"
            }
        ]
    }
}
