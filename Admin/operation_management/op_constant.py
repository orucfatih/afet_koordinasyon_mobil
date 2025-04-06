"""
Operation Management modülü için sabitler
"""

# Görev öncelikleri
TASK_PRIORITIES = [
    "Düşük (1)",
    "Orta (2)",
    "Yüksek (3)",
    "Kritik (4)"
]

# Ekip tablosu başlıkları
TEAM_TABLE_HEADERS = [
    "Ekip ID",
    "Ekip Lideri",
    "Kurum",
    "Durum",
    "İletişim",
    "Uzmanlık",
    "Personel",
    "Ekipman"
]

# Ekip durum renkleri
STATUS_COLORS = {
    "Müsait": "#4CAF50",
    "Meşgul": "#f44336"
}

# Ekip uzmanlık alanları
EXPERTISE_OPTIONS = [
    "Arama Kurtarma",
    "Sağlık",
    "Lojistik",
    "İnşaat",
    "Güvenlik",
    "İletişim",
    "İtfaiye",
    "Enkaz Kaldırma",
    "Diğer"
]

# Ekip durumu seçenekleri
TEAM_STATUS_OPTIONS = [
    "Müsait",
    "Meşgul"
]

# Filtre seçenekleri
FILTER_ALL_TEXT = "Tümü"

# Ekipman durumu seçenekleri
EQUIPMENT_STATUS_OPTIONS = [
    "Tam Donanımlı",
    "Kısmi Donanımlı",
    "Temel Ekipman",
    "Ekipman Yok"
] 