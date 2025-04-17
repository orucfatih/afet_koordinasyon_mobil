import SQLite from 'react-native-sqlite-storage';

const db = SQLite.openDatabase({ name: 'photos.db', location: 'default' });

export const initDB = () => {
  db.transaction(tx => {
    tx.executeSql(
      `CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uri TEXT,
        timestamp TEXT,
        latitude REAL,
        longitude REAL,
        sent INTEGER DEFAULT 0
      );`
    );
  });
};

export const savePhoto = (uri, latitude, longitude) => {
  try {const timestamp = new Date().toISOString();
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        'INSERT INTO photos (uri, timestamp, latitude, longitude, sent) VALUES (?, ?, ?, ?, ?)',
        [uri, timestamp, latitude, longitude, 0],
        (_, result) => resolve(result),
        (_, error) => reject(error)
      );
    });
  });} catch(error){
    throw error;
  }
};

export const getUnsentPhotos = () => {
  return new Promise((resolve) => {
    db.transaction(tx => {
      tx.executeSql(
        'SELECT * FROM photos WHERE sent = 0',
        [],
        (_, result) => {
          resolve(result.rows.raw());
        }
      );
    });
  });
};

export const markPhotoAsSent = (id) => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        'UPDATE photos SET sent = 1 WHERE id = ?',
        [id],
        (_, result) => resolve(result),
        (_, error) => reject(error)
      );
    });
  });
};
