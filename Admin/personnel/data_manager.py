# data_manager.py
import firebase_admin
from firebase_admin import credentials, db
from PyQt5.QtWidgets import QMessageBox

class DatabaseManager:
    """Firebase veritabanı işlemlerini yöneten sınıf"""
    def __init__(self, credential_path, database_url):
        """Firebase bağlantısını başlatır"""
        try:
            self.cred = credentials.Certificate(credential_path)
            if not firebase_admin._apps:  # Zaten başlatılmışsa tekrar başlatma
                firebase_admin.initialize_app(self.cred, {
                    'databaseURL': database_url
                })
            self.db = db.reference()  # Veritabanı referansı
            print("Firebase bağlantısı başarılı!")
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Firebase başlatılamadı: {e}")
            self.db = None

    def get_teams(self):
        """Tüm ekipleri Firebase'den alır"""
        try:
            teams_data = self.db.child("teams").get()
            return teams_data if teams_data else {}
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Ekipler alınırken hata oluştu: {e}")
            return {}

    def get_team(self, team_id):
        """Belirli bir ekibin verilerini alır"""
        try:
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            team_data = self.db.child("teams").child(safe_team_id).get()
            return team_data if team_data else None
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Ekip alınırken hata oluştu: {e}")
            return None

    def add_team(self, team_id, team_data):
        """Yeni bir ekip ekler"""
        try:
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            self.db.child("teams").child(safe_team_id).set(team_data)
            print(f"Ekip Firebase'e eklendi: {team_id}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Ekip eklenirken hata oluştu: {e}")
            return False

    def delete_team(self, team_id):
        """Bir ekibi siler"""
        try:
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            self.db.child("teams").child(safe_team_id).delete()
            print(f"Ekip Firebase'den silindi: {team_id}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Ekip silinirken hata oluştu: {e}")
            return False

    def add_personnel(self, team_id, personnel_data):
        """Bir ekibe personel ekler"""
        try:
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            team_ref = self.db.child("teams").child(safe_team_id)
            team_data = team_ref.get() or {}
            personnel_list = team_data.get("members", [])
            personnel_list.append(personnel_data)
            team_ref.update({"members": personnel_list})
            print(f"Personel ekibe eklendi: {team_id}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Personel eklenirken hata oluştu: {e}")
            return False

    def remove_personnel(self, team_id, personnel_data):
        """Bir ekipten personeli çıkarır"""
        try:
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            team_ref = self.db.child("teams").child(safe_team_id)
            team_data = team_ref.get() or {}
            personnel_list = team_data.get("members", [])
            updated_list = [p for p in personnel_list if p.get("Members_ID") != personnel_data.get("Members_ID")]
            team_ref.update({"members": updated_list})
            print(f"Personel ekipten çıkarıldı: {team_id}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Personel çıkarılırken hata oluştu: {e}")
            return False

    def update_personnel(self, team_id, old_personnel, updated_personnel):
        """Bir ekibin içindeki personel bilgilerini günceller"""
        try:
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            team_ref = self.db.child("teams").child(safe_team_id)
            team_data = team_ref.get() or {}
            personnel_list = team_data.get("members", [])
            index = next((i for i, p in enumerate(personnel_list) if p.get("Members_ID") == old_personnel.get("Members_ID")), None)
            if index is not None:
                personnel_list[index] = updated_personnel
                team_ref.update({"members": personnel_list})
                print(f"Personel güncellendi: {team_id}")
                return True
            return False
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Personel güncellenirken hata oluştu: {e}")
            return False

    def check_personnel_exists(self, tc_number):
        """Tüm ekiplerde belirli bir TC numarasına sahip personelin varlığını kontrol eder"""
        try:
            teams_data = self.get_teams()
            for team_id, team_info in teams_data.items():
                for member in team_info.get("members", []):
                    if member.get("TC") == tc_number:
                        return True, team_id  # Personel var ve ekip ID'si
            return False, None  # Personel yok
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Personel kontrolü sırasında hata oluştu: {e}")
            return False, None