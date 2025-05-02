import { PermissionsAndroid, Platform, Alert } from 'react-native';
import Contacts from 'react-native-contacts/src/NativeContacts';
import SendSMS from 'react-native-sms';

// SMS izni kontrolü
export const checkAndRequestSmsPermission = async () => {
  if (Platform.OS === 'android') {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.SEND_SMS,
        {
          title: 'SMS İzni Gerekli',
          message: 'Mesaj gönderebilmek için SMS iznini vermeniz gerekmektedir.',
          buttonPositive: 'Tamam',
        }
      );
      if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
        Alert.alert(
          'SMS İzni Gerekli',
          'Mesaj gönderebilmek için SMS iznini vermeniz gerekmektedir.'
        );
        return false;
      }
      return true;
    } catch (error) {
      console.error('SMS izni alınırken hata:', error);
      return false;
    }
  }
  return true;
};

// Kişiler izni kontrolü
export const checkAndRequestContactsPermission = async () => {
  if (Platform.OS === 'android') {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.READ_CONTACTS,
        {
          title: 'Kişilere Erişim İzni',
          message: 'Kişilerinize erişmek için izin gerekiyor',
          buttonPositive: 'Tamam',
        }
      );
      
      if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
        Alert.alert('İzin Reddedildi', 'Kişilere erişim izni verilmedi.');
        return false;
      }
      return true;
    } catch (error) {
      console.error('Kişiler izni alınırken hata:', error);
      return false;
    }
  }
  return true;
};

// Konum izni kontrolü
export const checkAndRequestLocationPermission = async () => {
  if (Platform.OS === 'android') {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
      );
      if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
        Alert.alert(
          'Konum İzni Gerekli',
          'Konum servislerini kullanabilmek için izin vermeniz gerekmektedir.'
        );
        return false;
      }
      return true;
    } catch (error) {
      console.error('Konum izni alınırken hata:', error);
      return false;
    }
  }
  return true;
};

// Kişileri getir
export const getAllContacts = () => {
  return new Promise((resolve, reject) => {
    Contacts.getAll()
      .then(contacts => {
        if (contacts && contacts.length > 0) {
          // Kişileri uygun formata dönüştür
          const formattedContacts = contacts
            .filter(c => c.phoneNumbers && c.phoneNumbers.length > 0)
            .map(c => ({
              id: c.recordID,
              name: c.displayName || `${c.givenName} ${c.familyName}`.trim(),
              phoneNumbers: c.phoneNumbers
            }))
            .sort((a, b) => a.name.localeCompare(b.name)); // Alfabetik sıralama
            
          resolve(formattedContacts);
        } else {
          resolve([]);
        }
      })
      .catch(error => {
        console.error('Kişiler alınırken hata:', error);
        reject(error);
      });
  });
};

// SMS Gönder
export const sendSmsToContacts = (contacts, message, setProgress) => {
  return new Promise(async (resolve, reject) => {
    try {
      let successCount = 0;
      let failCount = 0;
      
      // Her kişi için SMS gönder
      for (let i = 0; i < contacts.length; i++) {
        const contact = contacts[i];
        if (!contact.phoneNumber) continue;
        
        try {
          // SendSMS.send kullanımı - callback yapısı ile
          SendSMS.send({
            body: message,
            recipients: [contact.phoneNumber],
            successTypes: ['sent', 'queued'],
            allowAndroidSendWithoutReadPermission: true
          }, (completed, cancelled, error) => {
            if (completed) {
              successCount++;
            } else if (cancelled) {
              // Kullanıcı SMS uygulamasına yönlendirildi, bunu başarılı sayıyoruz
              successCount++;
              console.log(`${contact.name} kişisine SMS gönderimi için kullanıcı arayüzü açıldı`);
            } else if (error) {
              failCount++;
              console.error(`${contact.name} kişisine SMS gönderilirken hata:`, error);
            }
          });
          
          // Hepsini aynı anda göndermemek için küçük bir gecikme
          await new Promise(resolve => setTimeout(resolve, 300));
        } catch (error) {
          console.error(`${contact.name} kişisine SMS gönderilirken hata:`, error);
          failCount++;
        }
        
        // İlerleme durumunu güncelle
        if (setProgress) {
          setProgress(((i + 1) / contacts.length) * 100);
        }
      }
      
      resolve({ successCount, failCount });
    } catch (error) {
      console.error('Mesaj gönderilirken hata:', error);
      reject(error);
    }
  });
}; 