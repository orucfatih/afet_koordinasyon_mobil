TEAM_DATA = [
    ["EKP001", "Ahmet Yılmaz", "AFAD", "Müsait", "0532xxxxxxx", "USAR (Arama-Kurtarma)", "8", "Tam Donanımlı"],
    ["EKP002", "Mehmet Demir", "Sağlık Bakanlığı", "Meşgul", "0533xxxxxxx", "Sağlık Ekibi", "6", "Tam Donanımlı"],
    ["EKP003", "Ayşe Kaya", "Kızılay", "Müsait", "0535xxxxxxx", "Barınma-İaşe", "10", "Tam Donanımlı"],
    ["EKP004", "Ali Öztürk", "İtfaiye", "Meşgul", "0536xxxxxxx", "Yangın Söndürme", "6", "Tam Donanımlı"],
    ["EKP005", "Fatma Şahin", "UMKE", "Müsait", "0537xxxxxxx", "İlk Yardım", "4", "Tam Donanımlı"],
    ["EKP006", "Mustafa Aydın", "Belediye", "Müsait", "0538xxxxxxx", "Enkaz Kaldırma", "12", "Tam Donanımlı"],
    ["EKP007", "Zeynep Yıldız", "AFAD", "Meşgul", "0539xxxxxxx", "Koordinasyon", "5", "Tam Donanımlı"],
    ["EKP008", "Hüseyin Çelik", "Jandarma", "Müsait", "0531xxxxxxx", "Güvenlik", "8", "Tam Donanımlı"],
    ["EKP009", "Emine Arslan", "AFAD", "Müsait", "0532xxxxxxx", "Lojistik Destek", "6", "Tam Donanımlı"],
    ["EKP010", "Osman Kılıç", "Telekom", "Meşgul", "0533xxxxxxx", "Haberleşme", "4", "Tam Donanımlı"]
]

NOTIFICATIONS = [
    "Acil: Su Baskını - Mahmutlar Mah.",
    "Yangın İhbarı - Atatürk Cad.",
    "Bina Hasarı - Cumhuriyet Mah."
]

TASKS = [
    "Enkaz Taraması - Atatürk Mah. Blok 5 - Acil (4)",
    "Yaralı Tahliyesi - Merkez Hastanesi - Yüksek (3)",
    "Su Dağıtımı - Cumhuriyet Meydanı - Orta (2)"
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
    "Enkaz Taraması - Atatürk Mah. Blok 5 - Acil (4)": (
        "Ekip: EKP001 - Ahmet Yılmaz (AFAD)\n"
        "Başlık: Enkaz Taraması\n"
        "Lokasyon: Atatürk Mah. Blok 5\n"
        "Öncelik: Acil (4)\n"
        "Detaylar: 5 katlı binada ses sinyali alındı. Termal kamera ve dinleme cihazları ile tarama yapılacak."
    ),
    "Yaralı Tahliyesi - Merkez Hastanesi - Yüksek (3)": (
        "Ekip: EKP002 - Mehmet Demir (Sağlık Bakanlığı)\n"
        "Başlık: Yaralı Tahliyesi\n"
        "Lokasyon: Merkez Hastanesi\n"
        "Öncelik: Yüksek (3)\n"
        "Detaylar: 10 yaralının hastaneye güvenli transferi sağlanacak. 2 ambulans hazır beklemede."
    ),
    "Su Dağıtımı - Cumhuriyet Meydanı - Orta (2)": (
        "Ekip: EKP003 - Ayşe Kaya (Kızılay)\n"
        "Başlık: Su Dağıtımı\n"
        "Lokasyon: Cumhuriyet Meydanı\n"
        "Öncelik: Orta (2)\n"
        "Detaylar: 1000 adet su şişesi dağıtımı yapılacak. Mobil su tankeri konumlandırılacak."
    )
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

#kaynak yönetimi sayfası için örnek veriler
RESOURCE_DATA = [
    ["İçme Suyu", "Su", "1000 Lt", "Ana Depo", "Hazır"],
    ["Kuru Gıda", "Gıda", "500 Kg", "Batı Deposu", "Hazır"],
    ["Ateş Düşürücü", "İlaç", "1000 Kutu", "Sağlık Deposu", "Hazır"],
    ["Kışlık Çadır", "Çadır", "100 Adet", "Doğu Deposu", "Hazır"]
]

EQUIPMENT_DATA = [
    ["EKPMN001", "Hidrolik Kesici", "Kurtarma Ekipmanı", "Aktif", "15.03.2024", "Ahmet Yılmaz"],
    ["EKPMN002", "Termal Kamera", "Arama Ekipmanı", "Bakımda", "10.03.2024", "Mehmet Demir"],
    ["EKPMN003", "Jeneratör", "Güç Ekipmanı", "Aktif", "12.03.2024", "Ali Öztürk"],
    ["EKPMN004", "Sedye", "Sağlık Ekipmanı", "Aktif", "14.03.2024", "Fatma Şahin"],
    ["EKPMN005", "Yangın Hortumu", "Yangın Ekipmanı", "Aktif", "11.03.2024", "Hüseyin Çelik"],
    ["EKPMN006", "Merdiven", "Kurtarma Ekipmanı", "Onarımda", "13.03.2024", "Zeynep Yıldız"],
    ["EKPMN007", "Telsiz Seti", "İletişim Ekipmanı", "Aktif", "16.03.2024", "Emine Arslan"],
    ["EKPMN008", "Su Pompası", "Su Tahliye", "Aktif", "17.03.2024", "Osman Kılıç"],
    ["EKPMN009", "İlk Yardım Çantası", "Sağlık Ekipmanı", "Aktif", "18.03.2024", "Ayşe Kaya"],
    ["EKPMN010", "Halat Seti", "Kurtarma Ekipmanı", "Bakımda", "19.03.2024", "Mustafa Aydın"]
]

TASK_HISTORY_DATA = [
    ["2024-03-15", "Arama Kurtarma", "Kahramanmaraş Merkez", "8 saat", "Acil (4)", "2 kişi kurtarıldı", "Detaylar için tıklayın"],
    ["2024-03-14", "Yangın Söndürme", "Atatürk Cad. No:45", "3 saat", "Yüksek (3)", "Yangın kontrol altına alındı", "Detaylar için tıklayın"],
    ["2024-03-14", "Sağlık Taraması", "Cumhuriyet Mah.", "6 saat", "Orta (2)", "150 kişi tarandı", "Detaylar için tıklayın"],
    ["2024-03-13", "Su Tahliyesi", "Yeni Mah.", "5 saat", "Orta (2)", "3 bina tahliye edildi", "Detaylar için tıklayın"],
    ["2024-03-12", "Gıda Dağıtımı", "Çamlık Bölgesi", "4 saat", "Düşük (1)", "200 aileye ulaşıldı", "Detaylar için tıklayın"],
    ["2024-03-12", "Enkaz Kaldırma", "Fatih Cad.", "10 saat", "Yüksek (3)", "Yol trafiğe açıldı", "Detaylar için tıklayın"],
    ["2024-03-11", "İlk Yardım", "Spor Salonu", "12 saat", "Acil (4)", "35 kişiye müdahale edildi", "Detaylar için tıklayın"],
    ["2024-03-10", "Güvenlik Desteği", "Çarşı Merkezi", "8 saat", "Orta (2)", "Bölge güvenliği sağlandı", "Detaylar için tıklayın"],
    ["2024-03-09", "Altyapı Onarımı", "Sanayi Bölgesi", "15 saat", "Yüksek (3)", "Su şebekesi onarıldı", "Detaylar için tıklayın"],
    ["2024-03-08", "Koordinasyon", "Kriz Merkezi", "24 saat", "Acil (4)", "5 ekip koordine edildi", "Detaylar için tıklayın"]
]

# Görev geçmişi detayları
TASK_HISTORY_DETAILS = {
    "2024-03-15 Arama Kurtarma": {
        "Görev Tipi": "Arama Kurtarma",
        "Konum": "Kahramanmaraş Merkez, Atatürk Mah. No:23",
        "Başlangıç": "2024-03-15 08:00",
        "Bitiş": "2024-03-15 16:00",
        "Görevli Ekipler": ["EKP001", "EKP007"],
        "Kullanılan Ekipmanlar": ["EKPMN002", "EKPMN007"],
        "Sonuç": "2 kişi enkazdan sağ çıkarıldı",
        "Detaylı Rapor": "Deprem sonrası yıkılan 3 katlı binada arama kurtarma çalışması yapıldı. Termal kamera ile tespit edilen 2 kişi sağ olarak kurtarıldı."
    },
    "2024-03-14 Yangın Söndürme": {
        "Görev Tipi": "Yangın Söndürme",
        "Konum": "Atatürk Cad. No:45",
        "Başlangıç": "2024-03-14 14:30",
        "Bitiş": "2024-03-14 17:30",
        "Görevli Ekipler": ["EKP004"],
        "Kullanılan Ekipmanlar": ["EKPMN005"],
        "Sonuç": "Yangın kontrol altına alındı",
        "Detaylı Rapor": "İş yerinde çıkan yangına müdahale edildi. Can kaybı yok, maddi hasar minimal düzeyde."
    },
    "2024-03-14 Sağlık Taraması": {
        "Görev Tipi": "Sağlık Taraması",
        "Konum": "Cumhuriyet Mah.",
        "Başlangıç": "2024-03-14 09:00",
        "Bitiş": "2024-03-14 15:00",
        "Görevli Ekipler": ["EKP002", "EKP005"],
        "Kullanılan Ekipmanlar": ["EKPMN004", "EKPMN009"],
        "Sonuç": "150 kişi tarandı",
        "Detaylı Rapor": "Deprem bölgesinde sağlık taraması yapıldı. 15 kişi hastaneye sevk edildi, 45 kişiye yerinde müdahale edildi."
    }
}

# Mesajlaşma için örnek veriler
MESSAGE_CONTACTS = {
    "Ekip Liderleri": [
        {"id": "EKP001", "name": "Ahmet Yılmaz", "title": "AFAD Ekip Lideri", "status": "Çevrimiçi"},
        {"id": "EKP002", "name": "Mehmet Demir", "title": "Sağlık Ekibi Lideri", "status": "Meşgul"},
        {"id": "EKP003", "name": "Ayşe Kaya", "title": "Kızılay Ekip Lideri", "status": "Çevrimiçi"}
    ],
    "Kurumlar": [
        {"id": "KRM001", "name": "AFAD Merkez", "type": "Kurum", "status": "Aktif"},
        {"id": "KRM002", "name": "İl Sağlık Müdürlüğü", "type": "Kurum", "status": "Aktif"},
        {"id": "KRM003", "name": "İl Emniyet Müdürlüğü", "type": "Kurum", "status": "Aktif"},
        {"id": "KRM004", "name": "Belediye Kriz Merkezi", "type": "Kurum", "status": "Aktif"}
    ],
    "Kriz Masaları": [
        {"id": "KRZ001", "name": "İl Kriz Masası", "location": "Valilik", "status": "Aktif"},
        {"id": "KRZ002", "name": "Bölge Kriz Masası", "location": "AFAD Merkez", "status": "Aktif"},
        {"id": "KRZ003", "name": "Sağlık Kriz Masası", "location": "Hastane", "status": "Aktif"}
    ]
}

MESSAGE_HISTORY = {
    "EKP001": [
        {"sender": "Sistem", "message": "Ahmet Yılmaz ile sohbet başlatıldı", "timestamp": "10:00", "type": "system"},
        {"sender": "Siz", "message": "Merhaba Ahmet Bey, bölgedeki son durum nedir?", "timestamp": "10:01", "type": "sent"},
        {"sender": "Ahmet Yılmaz", "message": "Merhaba, şu an 3 kişilik ekiple arama çalışması yapıyoruz.", "timestamp": "10:02", "type": "received"}
    ],
    "KRM001": [
        {"sender": "Sistem", "message": "AFAD Merkez ile sohbet başlatıldı", "timestamp": "09:30", "type": "system"},
        {"sender": "AFAD Merkez", "message": "Yeni deprem riski haritası paylaşıldı.", "timestamp": "09:31", "type": "received"},
        {"sender": "Siz", "message": "Haritayı aldım, ekipleri buna göre yönlendireceğim.", "timestamp": "09:32", "type": "sent"}
    ]
}
