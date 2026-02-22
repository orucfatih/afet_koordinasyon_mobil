const functions = require("firebase-functions");
const fetch = require("node-fetch");
const cheerio = require("cheerio");
const iconv = require("iconv-lite");

exports.scrapeKoeriEarthquakes = functions.https.onRequest(async (req, res) => {
    const url = "http://www.koeri.boun.edu.tr/scripts/lst9.asp";

    try {
        // HTTP isteği gönder
        const response = await fetch(url, {
            headers: {
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to retrieve data. Status code: ${response.status}`);
        }

        // Veriyi buffer olarak al ve ISO-8859-9'dan UTF-8'e çevir
        const buffer = await response.arrayBuffer();
        const decodedData = iconv.decode(Buffer.from(buffer), "ISO-8859-9");

        // HTML'i ayrıştır
        const $ = cheerio.load(decodedData);
        const preTag = $("pre").text();

        if (!preTag) {
            throw new Error("Could not find earthquake data on the page.");
        }

        // Veriyi satırlara böl
        const lines = preTag.trim().split("\n");
        const dataLines = lines.filter((line) => /^\d{4}/.test(line.trim()));

        // Deprem verilerini ayrıştır
        const earthquakes = dataLines.map((line) => {
            const parts = line.trim().split(/\s+/);
            if (parts.length >= 9) {
                const date = `${parts[0]} ${parts[1]}`; // Tarih ve saat
                const lat = parts[2];                   // Enlem
                const lon = parts[3];                   // Boylam
                const depth = parts[4];                 // Derinlik
                const magnitude = parts[6];             // ML (yerel büyüklük)
                const place = parts.slice(8).join(" "); // Yer bilgisi

                return {
                    Date: date,
                    Lat: lat,          // Enlem eklendi
                    Lon: lon,          // Boylam eklendi
                    Depth: depth,      // Derinlik eklendi (isteğe bağlı)
                    Magnitude: magnitude,
                    Place: place,
                };
            }
            return null;
        }).filter((item) => item !== null);

        // JSON yanıtı oluştur
        const jsonResponse = {
            status: "success",
            data: earthquakes,
            count: earthquakes.length,
            timestamp: new Date().toISOString(),
        };

        res.set("Content-Type", "application/json; charset=utf-8");
        res.status(200).json(jsonResponse);
    } catch (error) {
        console.error("Error in scrapeKoeriEarthquakes:", error);
        res.status(500).json({
            error: `An error occurred: ${error.message}`,
        });
    }
});