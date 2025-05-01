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
        person_count INTEGER,
        hours_under_rubble INTEGER,
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

export const savePhoto = async (uri, latitude, longitude, rubbleInfo = {}) => {
  try {
    // Veritabanının başlatıldığından emin ol
    const db = await initDB();
    const timestamp = new Date().toISOString();
    
    const { personCount = 0, hoursUnderRubble = 0, additionalInfo = '' } = rubbleInfo;
    
    // Fotoğrafı enkaz bilgileriyle kaydet
    const [result] = await db.executeSql(
      'INSERT INTO photos (uri, timestamp, latitude, longitude, person_count, hours_under_rubble, additional_info, sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [uri, timestamp, latitude || null, longitude || null, personCount, hoursUnderRubble, additionalInfo, 0]
    );
    
    console.log('Enkaz bildirimi başarıyla kaydedildi, ID:', result.insertId);
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
