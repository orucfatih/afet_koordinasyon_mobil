"""
bu dosya sadece sunum ve test amaçlı kullanılır.
bu verilerin bir kısmı şimdilik veritabanına kaydedildi proje tamamen bitirildiğinde bu dosyayı kaldıracağım.

"""




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
    ["EKPMN001", "Hidrolik Kesici", "Kurtarma Ekipmanı", "Aktif", "15.03.2024", "25.04.2024", "Ahmet Yılmaz", "Ana Depo", "Düzenli bakım yapıldı"],
    ["EKPMN002", "Termal Kamera", "Arama Ekipmanı", "Bakımda", "10.03.2024", "10.04.2024", "Mehmet Demir", "Ana Depo", "Kalibrasyon gerekiyor"],
    ["EKPMN003", "Jeneratör", "Güç Ekipmanı", "Aktif", "12.03.2024", "12.05.2024", "Ali Öztürk", "Mobil Depo 1", "Yakıt dolu, hazır"],
    ["EKPMN004", "Sedye", "Sağlık Ekipmanı", "Aktif", "14.03.2024", "14.06.2024", "Fatma Şahin", "Saha", "Temizlik yapıldı"],
    ["EKPMN005", "Yangın Hortumu", "Yangın Ekipmanı", "Aktif", "11.03.2024", "11.05.2024", "Hüseyin Çelik", "Ana Depo", "Test edildi"],
    ["EKPMN006", "Merdiven", "Kurtarma Ekipmanı", "Onarımda", "13.03.2024", "30.04.2024", "Zeynep Yıldız", "Mobil Depo 2", "Basamak tamiri gerekiyor"],
    ["EKPMN007", "Telsiz Seti", "İletişim Ekipmanı", "Aktif", "16.03.2024", "16.06.2024", "Emine Arslan", "Saha", "Piller değiştirildi"],
    ["EKPMN008", "Su Pompası", "Su Tahliye", "Aktif", "17.03.2024", "17.04.2024", "Osman Kılıç", "Mobil Depo 1", "Hazır durumda"],
    ["EKPMN009", "İlk Yardım Çantası", "Sağlık Ekipmanı", "Aktif", "18.03.2024", "18.06.2024", "Ayşe Kaya", "Saha", "Malzemeler tamamlandı"],
    ["EKPMN010", "Halat Seti", "Kurtarma Ekipmanı", "Bakımda", "19.03.2024", "19.04.2024", "Mustafa Aydın", "Ana Depo", "Aşınma kontrolü"],
    ["EKPMN011", "Dizel Jeneratör", "Güç Ekipmanı - Jeneratörler", "Aktif", "20.03.2024", "20.05.2024", "Mehmet Demir", "Ana Depo", "Yakıt dolu, hazır"],
    ["EKPMN012", "Benzinli Jeneratör", "Güç Ekipmanı - Jeneratörler", "Aktif", "21.03.2024", "21.05.2024", "Ali Öztürk", "Mobil Depo 2", "Yakıt dolu, hazır"],
    ["EKPMN013", "Solar Jeneratör", "Güç Ekipmanı - Jeneratörler", "Aktif", "22.03.2024", "22.05.2024", "Hüseyin Çelik", "Saha", "Paneller temizlendi"],
    ["EKPMN014", "Akustik Dinleme Cihazı", "Arama Ekipmanı", "Aktif", "23.03.2024", "23.05.2024", "Ayşe Kaya", "Ana Depo", "Kalibre edildi"],
    ["EKPMN015", "Dalgıç Pompa", "Su Tahliye", "Aktif", "24.03.2024", "24.05.2024", "Osman Kılıç", "Mobil Depo 1", "Test edildi"]
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

# STK yönetimi için örnek veriler
STK_DATA = [
    ["AKUT", "Arama Kurtarma", "0532xxx xxxx", "50 personel", "Tüm Türkiye", "Aktif"],
    ["Kızılay", "Gıda", "0533xxx xxxx", "200 personel", "Tüm Türkiye", "Aktif"],
    ["Sağlık Gönüllüleri", "Sağlık", "0535xxx xxxx", "30 personel", "Marmara", "Aktif"]
]

STK_DETAILS = {
    "AKUT": {
        "Görev Tipi": "Arama Kurtarma",
        "Konum": "Tüm Türkiye",
        "Başlangıç": "2024-03-15 08:00",
        "Bitiş": "2024-03-15 16:00",
        "Görevli Ekipler": ["EKP001", "EKP007"],
        "Kullanılan Ekipmanlar": ["EKPMN002", "EKPMN007"],
        "Sonuç": "2 kişi enkazdan sağ çıkarıldı",
        "Detaylı Rapor": "Deprem sonrası yıkılan 3 katlı binada arama kurtarma çalışması yapıldı. Termal kamera ile tespit edilen 2 kişi sağ olarak kurtarıldı."
    },
    "Kızılay": {
        "Görev Tipi": "Gıda Dağıtımı",
        "Konum": "Tüm Türkiye",
        "Başlangıç": "2024-03-15 09:00",
        "Bitiş": "2024-03-15 17:00",
        "Görevli Ekipler": ["EKP003"],
        "Kullanılan Ekipmanlar": ["EKPMN001"],
        "Sonuç": "1000 aileye gıda yardımı yapıldı",
        "Detaylı Rapor": "Deprem bölgesinde gıda dağıtımı yapıldı. 1000 aileye temel gıda malzemeleri ulaştırıldı."
    },
    "Sağlık Gönüllüleri": {
        "Görev Tipi": "Sağlık Taraması",
        "Konum": "Marmara",
        "Başlangıç": "2024-03-15 10:00",
        "Bitiş": "2024-03-15 18:00",
        "Görevli Ekipler": ["EKP002", "EKP005"],
        "Kullanılan Ekipmanlar": ["EKPMN004", "EKPMN009"],
        "Sonuç": "150 kişi tarandı",
        "Detaylı Rapor": "Deprem bölgesinde sağlık taraması yapıldı. 15 kişi hastaneye sevk edildi, 45 kişiye yerinde müdahale edildi."
    }
}

# Vefat eden vatandaşlar için örnek veriler
CITIZEN_DATA = {
    "12345678901": {
        "kisisel_bilgiler": {
            "tc": "12345678901",
            "ad": "Mehmet",
            "soyad": "Yılmaz",
            "dogum_tarihi": "1975-05-15",
            "cinsiyet": "Erkek",
            "uyruk": "T.C.",
            "medeni_hal": "Evli"
        },
        "nufus_kayit": {
            "anne_adi": "Fatma",
            "baba_adi": "Ahmet",
            "dogum_yeri": "Kahramanmaraş",
            "es_adi": "Ayşe Yılmaz",
            "cocuklar": ["Ali Yılmaz", "Zeynep Yılmaz"],
            "olum_kaydi": {
                "durum": "Var",
                "tarih": "2024-02-06",
                "yer": "Kahramanmaraş"
            }
        },
        "olum_belgesi": {
            "durum": "Var",
            "belge_no": "2024-001",
            "duzenleyen_kurum": "Kahramanmaraş Devlet Hastanesi",
            "neden": "Deprem - Göçük Altında Kalma"
        },
        "sosyal_guvenlik": {
            "sgk_durumu": "Pasif",
            "son_guncellenme": "2024-02-06"
        },
        "yerlesim": {
            "il": "Kahramanmaraş",
            "ilce": "Onikişubat",
            "mahalle": "Yenişehir Mah.",
            "adres": "Deprem Cad. No:15"
        }
    },
    "98765432109": {
        "kisisel_bilgiler": {
            "tc": "98765432109",
            "ad": "Ayşe",
            "soyad": "Demir",
            "dogum_tarihi": "1980-12-23",
            "cinsiyet": "Kadın",
            "uyruk": "T.C.",
            "medeni_hal": "Evli"
        },
        "nufus_kayit": {
            "anne_adi": "Hatice",
            "baba_adi": "Mustafa",
            "dogum_yeri": "Hatay",
            "es_adi": "Hasan Demir",
            "cocuklar": ["Elif Demir"],
            "olum_kaydi": {
                "durum": "Var",
                "tarih": "2024-02-06",
                "yer": "Hatay"
            }
        },
        "olum_belgesi": {
            "durum": "Var",
            "belge_no": "2024-002",
            "duzenleyen_kurum": "Hatay Devlet Hastanesi",
            "neden": "Deprem - Bina Çökmesi"
        },
        "sosyal_guvenlik": {
            "sgk_durumu": "Pasif",
            "son_guncellenme": "2024-02-06"
        },
        "yerlesim": {
            "il": "Hatay",
            "ilce": "Antakya",
            "mahalle": "Cumhuriyet Mah.",
            "adres": "Kurtuluş Sok. No:7"
        }
    },
    "45678901234": {
        "kisisel_bilgiler": {
            "tc": "45678901234",
            "ad": "Ali",
            "soyad": "Kaya",
            "dogum_tarihi": "1990-08-10",
            "cinsiyet": "Erkek",
            "uyruk": "T.C.",
            "medeni_hal": "Bekar"
        },
        "nufus_kayit": {
            "anne_adi": "Zeynep",
            "baba_adi": "İbrahim",
            "dogum_yeri": "Adıyaman",
            "es_adi": "",
            "cocuklar": [],
            "olum_kaydi": {
                "durum": "Var",
                "tarih": "2024-02-06",
                "yer": "Adıyaman"
            }
        },
        "olum_belgesi": {
            "durum": "Var",
            "belge_no": "2024-003",
            "duzenleyen_kurum": "Adıyaman Devlet Hastanesi",
            "neden": "Deprem - Göçük Altında Kalma"
        },
        "sosyal_guvenlik": {
            "sgk_durumu": "Pasif",
            "son_guncellenme": "2024-02-06"
        },
        "yerlesim": {
            "il": "Adıyaman",
            "ilce": "Merkez",
            "mahalle": "Fatih Mah.",
            "adres": "Yeni Cad. No:42"
        }
    }
}




# Vatandaş geri bildirimleri için örnek veriler
CITIZEN_FEEDBACK_DATA = [
    {
        "id": 1,
        "title": "Mobil Uygulama Çöküyor",
        "content": "Yardım başvurusu sırasında uygulama aniden kapanıyor. Android 12 kullanıyorum.",
        "date": "2024-04-21 14:30",
        "email": "ahmet.yilmaz@example.com",
        "status": "Yeni",
        "location": "Şehitkamil, Gaziantep",
        "priority": "Yüksek"
    },
    {
        "id": 2,
        "title": "Konum Bilgisi Yanlış Gösteriliyor",
        "content": "Uygulama konumumu yanlış algılıyor, yardımı yanlış bölgeye yönlendirdim.",
        "date": "2024-04-21 10:15",
        "email": "ayse.kaya@example.com",
        "status": "İnceleniyor",
        "location": "Onikişubat, Kahramanmaraş",
        "priority": "Orta"
    },
    {
        "id": 3,
        "title": "Enkaz Kaldırma Talebi",
        "content": "Binamızın yanındaki yıkıntı hala kaldırılmadı. Güvenlik riski oluşturuyor ve çocuklar için tehlikeli.",
        "date": "2024-04-20 16:45",
        "email": "mehmet.demir@example.com",
        "status": "Çözümlendi",
        "location": "Antakya, Hatay",
        "priority": "Yüksek",
        "resolution_notes": "Enkaz kaldırma ekibi 22 Nisan'da bölgeye yönlendirildi."
    },
    {
        "id": 4,
        "title": "Bildirimler Çok Geç Geliyor",
        "content": "Yardım dağıtım bildirimleri 1 saatten geç geliyor. Bildirim sistemi güncellenebilir mi?",
        "date": "2024-04-20 09:30",
        "email": "zeynep.ozturk@example.com",
        "status": "İnceleniyor",
        "location": "Merkez, Adıyaman",
        "priority": "Düşük"
    },
    {
        "id": 5,
        "title": "Uygulama Üzerinden Fotoğraf Gönderilemiyor",
        "content": "Yardım isteği oluştururken fotoğraf eklemeye çalışınca hata veriyor.",
        "date": "2024-04-19 11:20",
        "email": "hasan.sahin@example.com",
        "status": "Yeni",
        "location": "Akdeniz, Mersin",
        "priority": "Orta"
    },
    {
        "id": 6,
        "title": "Gıda Yardımı Teşekkürü",
        "content": "Dün mahallemize gelen gıda yardımı için teşekkür ederiz. Ekipler çok ilgiliydi ve organizasyon düzenliydi.",
        "date": "2024-04-19 08:55",
        "email": "fatma.yildiz@example.com",
        "status": "Kapatıldı",
        "location": "Dulkadiroğlu, Kahramanmaraş",
        "priority": "Düşük",
        "resolution_notes": "Teşekkür notu kayda alındı, ilgili ekibe iletildi."
    },
    {
        "id": 7,
        "title": "Karanlık Mod Eksik",
        "content": "Geceleri uygulamayı kullanmak zor oluyor. Karanlık mod desteği eklenebilir mi?",
        "date": "2024-04-18 17:40",
        "email": "mustafa.akin@example.com",
        "status": "İnceleniyor",
        "location": "Yüreğir, Adana",
        "priority": "Düşük"
    },
    {
        "id": 8,
        "title": "Veriler Offline Kaydedilmiyor",
        "content": "İnternet yokken yardım talebi oluşturamıyorum. Bağlantı gelince otomatik gönderme seçeneği olmalı.",
        "date": "2024-04-18 14:10",
        "email": "elif.celik@example.com",
        "status": "Yeni",
        "location": "Osmaniye Merkez, Osmaniye",
        "priority": "Orta"
    },
    {
        "id": 9,
        "title": "Afet Koordinasyon Merkezi Önerisi",
        "content": "Mahallemizde boş olan belediye binası afet koordinasyon merkezi olarak kullanılabilir.",
        "date": "2024-04-17 13:25",
        "email": "ali.toprak@example.com",
        "status": "Çözümlendi",
        "location": "Battalgazi, Malatya",
        "priority": "Düşük",
        "resolution_notes": "Öneri değerlendirildi, belediye binasının kullanımı için gereken izinler alındı."
    },
    {
        "id": 10,
        "title": "Şikayet Takip Ekranı Karmaşık",
        "content": "Geri bildirim takibi için ekran çok karışık. Daha sade ve kullanıcı dostu olabilir.",
        "date": "2024-04-17 10:05",
        "email": "deniz.coskun@example.com",
        "status": "İnceleniyor",
        "location": "Şahinbey, Gaziantep",
        "priority": "Orta"
    }
]


# Feedback yanıtları için örnek veriler
FEEDBACK_REPLIES = {
    3: [
        {
            "reply_id": 1,
            "feedback_id": 3,
            "sender": "Ahmet Yılmaz (Enkaz Kaldırma Koordinatörü)",
            "content": "Talebiniz alınmıştır. Enkaz kaldırma ekibimiz 22 Nisan tarihinde bölgeye yönlendirilecektir.",
            "date": "2024-04-21 09:15",
            "is_public": True
        },
        {
            "reply_id": 2,
            "feedback_id": 3,
            "sender": "Mehmet Demir",
            "content": "Teşekkür ederim, bilgilendirme için.",
            "date": "2024-04-21 10:30",
            "is_public": True
        }
    ],
    6: [
        {
            "reply_id": 3,
            "feedback_id": 6,
            "sender": "Ayşe Kaya (Yardım Koordinatörü)",
            "content": "Olumlu geri bildiriminiz için teşekkür ederiz. İletinizi ilgili ekibe aktardık.",
            "date": "2024-04-19 14:20",
            "is_public": True
        }
    ],
    9: [
        {
            "reply_id": 4,
            "feedback_id": 9,
            "sender": "Mustafa Öztürk (Koordinasyon Merkezi Sorumlusu)",
            "content": "Öneriniz için teşekkürler. Belediye binasının kullanımı için gerekli izinler alındı ve önümüzdeki hafta koordinasyon merkezi olarak faaliyete geçecektir.",
            "date": "2024-04-18 11:45",
            "is_public": True
        }
    ]
}

# Örnek istatistikler
FEEDBACK_STATISTICS = {
    "total": 10,
    "new": 3,
    "in_progress": 4,
    "resolved": 2,
    "closed": 1,
    "high_priority": 3,
    "medium_priority": 4,
    "low_priority": 3
}