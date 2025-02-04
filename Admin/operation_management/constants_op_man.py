# Tablo başlıkları
TEAM_TABLE_HEADERS = [
    "Ekip ID", "Ekip Lideri", "Kurum", "Durum", "İletişim",
    "Uzmanlık", "Personel Sayısı", "Ekipman Durumu"
]

EQUIPMENT_TABLE_HEADERS = [
    "Ekipman ID", "Ekipman Adı", "Tür", "Durum",
    "Son Kontrol", "Sorumlu Personel"
]

HISTORY_TABLE_HEADERS = [
    "Tarih", "Görev Tipi", "Konum", "Süre",
    "Öncelik", "Sonuç", "Detaylar"
]

# Durum renkleri
STATUS_COLORS = {
    "Müsait": "#4CAF50",
    "Meşgul": "#f44336",
    "Bakımda": "#FFA500"
}

# Görev öncelik seviyeleri ve renkleri
TASK_PRIORITY_COLORS = {
    "Düşük (1)": "#4CAF50",    # Yeşil
    "Orta (2)": "#FFA500",     # Turuncu
    "Yüksek (3)": "#FF5722",   # Kırmızımsı turuncu
    "Acil (4)": "#f44336"      # Kırmızı
}

TASK_PRIORITIES = ["Düşük (1)", "Orta (2)", "Yüksek (3)", "Acil (4)"] 