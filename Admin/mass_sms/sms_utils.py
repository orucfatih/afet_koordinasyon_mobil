import re
from typing import List, Dict, Tuple

class SMSUtils:
    @staticmethod
    def calculate_sms_count(message: str) -> int:
        """SMS sayısını hesapla"""
        # Türkçe karakterleri kontrol et
        has_turkish_chars = bool(re.search('[çğıöşüÇĞİÖŞÜ]', message))
        
        # Türkçe karakter varsa karakter limiti 70, yoksa 160
        char_limit = 70 if has_turkish_chars else 160
        message_length = len(message)
        
        if message_length == 0:
            return 0
        
        return (message_length - 1) // char_limit + 1
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Telefon numarası formatını doğrula"""
        # Türkiye telefon numarası formatı: +90XXXXXXXXXX veya 0XXXXXXXXXX
        pattern = r'^(\+90|0)[5-9][0-9]{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """Telefon numarasını standart formata çevir"""
        # Boşlukları ve tire işaretlerini kaldır
        phone = re.sub(r'[\s-]', '', phone)
        
        # Başında 0 varsa +90 ile değiştir
        if phone.startswith('0'):
            phone = '+90' + phone[1:]
        # Başında + yoksa +90 ekle
        elif not phone.startswith('+'):
            phone = '+90' + phone
            
        return phone
    
    @staticmethod
    def estimate_cost(message: str, recipient_count: int) -> float:
        """Tahmini SMS maliyetini hesapla"""
        sms_count = SMSUtils.calculate_sms_count(message)
        # Örnek maliyet hesabı: her SMS başına 0.1 TL
        return sms_count * recipient_count * 0.1
    
    @staticmethod
    def chunk_recipients(recipients: List[str], chunk_size: int = 1000) -> List[List[str]]:
        """Alıcı listesini belirtilen boyutta parçalara ayır"""
        return [recipients[i:i + chunk_size] for i in range(0, len(recipients), chunk_size)]
    
    @staticmethod
    def validate_message_content(message: str) -> Tuple[bool, str]:
        """Mesaj içeriğini doğrula"""
        if not message.strip():
            return False, "Mesaj içeriği boş olamaz."
            
        if len(message) > 1000:  # Maksimum karakter sınırı
            return False, "Mesaj çok uzun. Maksimum 1000 karakter girebilirsiniz."
            
        return True, "" 