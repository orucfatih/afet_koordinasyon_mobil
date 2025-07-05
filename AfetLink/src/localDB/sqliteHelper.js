import SQLite from 'react-native-sqlite-storage';

// SQLite yapılandırması
SQLite.enablePromise(true);
let dbInstance = null;

export const initDB = async () => {
  if (dbInstance !== null) {
    return Promise.resolve(dbInstance);
  }

  try {
    dbInstance = await SQLite.openDatabase({ name: 'photos.db', location: 'default' });
    
    // Tabloyu oluştur
    await dbInstance.executeSql(
      `CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uri TEXT,
        timestamp TEXT,
        latitude REAL,
        longitude REAL,
        disaster_type TEXT,
        person_count TEXT,
        time_since_disaster TEXT,
        additional_info TEXT,
        sent INTEGER DEFAULT 0
      );`
    );
    
    return dbInstance;
  } catch (error) {
    console.error('Veritabanı başlatma hatası:', error);
    throw error;
  }
};

export const savePhoto = async (uri, latitude, longitude, disasterInfo = {}) => {
  try {
    // Veritabanının başlatıldığından emin ol
    const db = await initDB();
    const timestamp = new Date().toISOString();
    
    const { disasterType = null, personCount = null, timeSinceDisaster = null, additionalInfo = '' } = disasterInfo;
    
    // Fotoğrafı afet bilgileriyle kaydet
    const [result] = await db.executeSql(
      'INSERT INTO photos (uri, timestamp, latitude, longitude, disaster_type, person_count, time_since_disaster, additional_info, sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [uri, timestamp, latitude || null, longitude || null, disasterType, personCount, timeSinceDisaster, additionalInfo, 0]
    );
    
    console.log('Afet bildirimi başarıyla kaydedildi, ID:', result.insertId);
    return result;
  } catch (error) {
    console.error('Fotoğraf kaydetme hatası:', error);
    throw error;
  }
};

export const getUnsentPhotos = async () => {
  try {
    const db = await initDB();
    const [results] = await db.executeSql('SELECT * FROM photos WHERE sent = 0', []);
    
    const rows = [];
    for (let i = 0; i < results.rows.length; i++) {
      rows.push(results.rows.item(i));
    }
    
    return rows;
  } catch (error) {
    console.error('Gönderilmemiş fotoğrafları alma hatası:', error);
    return [];
  }
};

export const markPhotoAsSent = async (id) => {
  try {
    const db = await initDB();
    const [result] = await db.executeSql(
      'UPDATE photos SET sent = 1 WHERE id = ?',
      [id]
    );
    
    return result;
  } catch (error) {
    console.error('Fotoğrafı işaretleme hatası:', error);
    throw error;
  }
};

export const getPendingPhotoCount = async () => {
  try {
    const db = await initDB();
    const [results] = await db.executeSql('SELECT COUNT(*) as count FROM photos WHERE sent = 0', []);
    
    return results.rows.item(0).count;
  } catch (error) {
    console.error('Bekleyen fotoğraf sayısını alma hatası:', error);
    return 0;
  }
};

export const deletePhoto = async (id) => {
  try {
    const db = await initDB();
    const [result] = await db.executeSql(
      'DELETE FROM photos WHERE id = ?',
      [id]
    );
    
    return result;
  } catch (error) {
    console.error('Fotoğraf silme hatası:', error);
    throw error;
  }
};

export const checkDuplicatePhoto = async (timestamp, disasterType, personCount, timeSinceDisaster) => {
  try {
    const db = await initDB();
    const [results] = await db.executeSql(
      `SELECT id FROM photos WHERE timestamp = ? AND disaster_type = ? AND person_count = ? AND time_since_disaster = ? AND sent = 0`,
      [timestamp, disasterType, personCount, timeSinceDisaster]
    );
    
    if (results.rows.length > 1) {
      // Birden fazla aynı bildirim varsa, ilkini tut diğerlerini sil
      const duplicates = [];
      for (let i = 1; i < results.rows.length; i++) {
        duplicates.push(results.rows.item(i).id);
      }
      
      for (const duplicateId of duplicates) {
        await db.executeSql('DELETE FROM photos WHERE id = ?', [duplicateId]);
        console.log(`Duplicate fotoğraf silindi. ID: ${duplicateId}`);
      }
      
      return true; // Duplicate bulundu ve temizlendi
    }
    
    return false; // Duplicate yok
  } catch (error) {
    console.error('Duplicate kontrol hatası:', error);
    return false;
  }
};

export const cleanupDuplicates = async () => {
  try {
    const db = await initDB();
    
    // Aynı timestamp ve bilgilere sahip duplicate'ları bul ve temizle
    const [results] = await db.executeSql(
      `SELECT timestamp, disaster_type, person_count, time_since_disaster, COUNT(*) as count
       FROM photos 
       WHERE sent = 0 
       GROUP BY timestamp, disaster_type, person_count, time_since_disaster 
       HAVING COUNT(*) > 1`
    );
    
    let cleanedCount = 0;
    
    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      
      // Bu grup için tüm kayıtları al
      const [duplicates] = await db.executeSql(
        `SELECT id FROM photos 
         WHERE timestamp = ? AND disaster_type = ? AND person_count = ? AND time_since_disaster = ? AND sent = 0
         ORDER BY id ASC`,
        [row.timestamp, row.disaster_type, row.person_count, row.time_since_disaster]
      );
      
      // İlkini tut, diğerlerini sil
      for (let j = 1; j < duplicates.rows.length; j++) {
        await db.executeSql('DELETE FROM photos WHERE id = ?', [duplicates.rows.item(j).id]);
        cleanedCount++;
      }
    }
    
    if (cleanedCount > 0) {
      console.log(`${cleanedCount} duplicate fotoğraf temizlendi.`);
    }
    
    return cleanedCount;
  } catch (error) {
    console.error('Duplicate temizleme hatası:', error);
    return 0;
  }
};
