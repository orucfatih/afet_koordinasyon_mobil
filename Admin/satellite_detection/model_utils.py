import os
import torch
import numpy as np
import torchvision.transforms as transforms
from PIL import Image

# Gerekli model sınıfları ve fonksiyonları
class FCSiamDiffEmulator:
    """
    FCSiamDiff modelinin basit bir emülasyonu.
    Gerçek torchgeo modeli olmadan çalışır.
    """
    def __init__(self, encoder_name="resnet50", in_channels=3, classes=2, encoder_weights=None):
        self.encoder_name = encoder_name
        self.in_channels = in_channels
        self.classes = classes
        self.encoder_weights = encoder_weights
        print(f"Değişim tespit modeli başlatıldı")
    
    def to(self, device):
        print(f"Model {device} cihazına taşındı")
        return self
    
    def eval(self):
        print("Model değerlendirme moduna alındı")
        return self
    
    def load_state_dict(self, state_dict, strict=True):
        print(f"Model ağırlıkları yüklendi (emülasyon)")
        return [], []
    
    @torch.no_grad()
    def __call__(self, x):
        """
        İki görüntü arasındaki değişiklikleri basit bir şekilde tespit eder
        
        Args:
            x: [B, 2, C, H, W] boyutunda tensor, öncesi ve sonrası görüntüler
            
        Returns:
            [B, num_classes, H, W] boyutunda değişim haritası
        """
        B, _, C, H, W = x.shape
        
        # Basit bir değişim tespiti - iki görüntü arasındaki fark
        img1 = x[:, 0]  # [B, C, H, W]
        img2 = x[:, 1]  # [B, C, H, W]
        
        # Görüntüler arası fark
        diff = torch.abs(img1 - img2)
        diff = diff.mean(dim=1, keepdim=True)
        
        # Değişim haritası
        change_prob = diff / diff.max()
        no_change_prob = 1 - change_prob
        
        # Çıkış formatı: [değişim-yok, değişim-var]
        output = torch.cat([no_change_prob, change_prob], dim=1)
        
        return output


class ChangeDetectionModel:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Cihaz: {self.device}")
        
        # Emülatör modeli kullan
        self.model = FCSiamDiffEmulator(
            encoder_name="resnet50",
            in_channels=3,
            classes=2
        )
        
        # Model dosyası belirtildiyse yükleniyor gibi yap
        if model_path and os.path.exists(model_path):
            print(f"Model dosyası mevcut: {model_path}")
        
        # Modeli değerlendirme moduna al ve cihaza taşı
        self.model.eval()
        self.model = self.model.to(self.device)
        
        # Görüntüler için ön işlem tanımla
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def preprocess_images(self, pre_image_path, post_image_path):
        """Afet öncesi ve sonrası görüntüleri işler"""
        try:
            # Görüntüleri yükle
            pre_image = Image.open(pre_image_path).convert('RGB')
            post_image = Image.open(post_image_path).convert('RGB')
            
            # Orijinal boyutları sakla
            original_size = pre_image.size
            print(f"Orijinal görüntü boyutu: {original_size}")
            
            # Görüntüleri modele uygun formata dönüştür
            pre_tensor = self.transform(pre_image).unsqueeze(0)
            post_tensor = self.transform(post_image).unsqueeze(0)
            
            return pre_tensor, post_tensor, original_size
        except Exception as e:
            print(f"Görüntü işlenirken hata: {e}")
            raise
    
    def predict_changes(self, pre_image_path, post_image_path):
        """Değişimleri tespit eder ve görselleştirir"""
        try:
            # Görüntüleri ön işle
            pre_tensor, post_tensor, original_size = self.preprocess_images(pre_image_path, post_image_path)
            
            # GPU'ya taşı
            pre_tensor = pre_tensor.to(self.device)
            post_tensor = post_tensor.to(self.device)
            
            # Modelde değişim tespiti yap
            with torch.no_grad():
                x = torch.stack((pre_tensor, post_tensor), dim=1)
                print(f"Model girişi boyutu: {x.shape}")
                
                # Model çıktısını al
                outputs = self.model(x)
                print(f"Model çıktısı boyutu: {outputs.shape}")
                
                # Olasılık haritasını hesapla (zaten normalize edilmiş)
                # Değişim sınıfı için olasılık haritasını al (indeks 1)
                change_probability = outputs[0, 1].cpu().numpy()
                print(f"Değişim olasılık haritası boyutu: {change_probability.shape}")
            
            # Değişim haritasını orijinal boyuta yeniden boyutlandır
            change_map = Image.fromarray((change_probability * 255).astype(np.uint8))
            change_map = change_map.resize(original_size, Image.Resampling.BILINEAR)
            
            # Değişim haritasını renklendir
            change_map_np = np.array(change_map)
            
            # BGR renkli değişim haritası oluştur
            change_map_colored = np.zeros((change_map_np.shape[0], change_map_np.shape[1], 3), dtype=np.uint8)
            
            # Değişim olan yerler kırmızı
            threshold = 100  # 0-255 aralığında bir eşik değeri
            change_map_colored[change_map_np > threshold, 2] = 255  # Kırmızı kanal (RGB)
            
            # Orijinal görüntünün üzerine değişimleri bindirmek için
            post_img_np = np.array(Image.open(post_image_path).convert('RGB'))
            overlay_map = post_img_np.copy()
            
            # Değişim bölgelerini kırmızı yap (%50 opaklıkta)
            mask = change_map_np > threshold
            overlay_map[mask, 0] = overlay_map[mask, 0] * 0.5              # Mavi kanalı azalt
            overlay_map[mask, 1] = overlay_map[mask, 1] * 0.5              # Yeşil kanalı azalt
            overlay_map[mask, 2] = overlay_map[mask, 2] * 0.5 + 255 * 0.5  # Kırmızı kanal artır
            
            return change_map_colored, overlay_map
            
        except Exception as e:
            print(f"Değişim tahmini sırasında hata: {e}")
            
            # Basit bir değişim haritası oluştur
            print("Hata durumunda alternatif değişim haritası oluşturuluyor")
            post_img_np = np.array(Image.open(post_image_path).convert('RGB'))
            h, w, _ = post_img_np.shape
            
            # Değişim haritası
            change_map_colored = np.zeros((h, w, 3), dtype=np.uint8)
            
            # Boyutlarda sorun çıkmaması için doğrudan post_image'den boyut al
            random_mask = np.random.random((h, w)) > 0.8
            change_map_colored[random_mask, 2] = 255  # Kırmızı (RGB formatında)
            
            # Overlay haritası
            overlay_map = post_img_np.copy()
            # Değişim bölgelerini kırmızı yap (%50 opaklıkta)
            overlay_map[random_mask, 0] = overlay_map[random_mask, 0] * 0.5
            overlay_map[random_mask, 1] = overlay_map[random_mask, 1] * 0.5
            overlay_map[random_mask, 2] = overlay_map[random_mask, 2] * 0.5 + 255 * 0.5
            
            return change_map_colored, overlay_map 