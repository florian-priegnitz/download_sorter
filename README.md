# 📂 Download Sorter

Eine Sammlung von Python-Skripten zur Organisation und Bereinigung deines Download-Ordners.

## ✨ Features

- **Automatische Sortierung** nach Dateitypen (Bilder, Dokumente, Videos, etc.)
- **Duplikate finden** mittels SHA256-Hash-Vergleich
- **Sichere Duplikat-Verwaltung** - nur Verschieben, kein automatisches Löschen

## 📋 Skripte

| Skript | Beschreibung |
|--------|--------------|
| `sort_downloads.py` | Sortiert Dateien nach Typ in Unterordner |
| `find_duplicates.py` | Findet identische Dateien per Hash |
| `move_duplicates.py` | Verschiebt gefundene Duplikate zur Überprüfung |

---

## 🗂️ sort_downloads.py

Sortiert alle Dateien im Download-Ordner in kategoriebasierte Unterordner.

### Kategorien

| Ordner | Dateitypen |
|--------|------------|
| `Bilder` | jpg, png, gif, svg, webp, ico, tiff, heic |
| `Dokumente` | pdf, doc, docx, txt, odt, rtf, xls, xlsx, ppt, pptx, csv |
| `Videos` | mp4, avi, mkv, mov, wmv, flv, webm, m4v |
| `Audio` | mp3, wav, flac, aac, ogg, wma, m4a |
| `Archive` | zip, rar, 7z, tar, gz, bz2 |
| `Programme` | exe, msi, dmg, deb, rpm |
| `Code` | py, js, html, css, java, cpp, c, h, json, xml, sql |
| `Sonstiges` | Alle anderen Dateitypen |

### Verwendung

```bash
python sort_downloads.py
```

### Beispiel

```
Downloads/
├── foto.jpg          → Bilder/foto.jpg
├── dokument.pdf      → Dokumente/dokument.pdf
├── video.mp4         → Videos/video.mp4
└── setup.exe         → Programme/setup.exe
```

---

## 🔍 find_duplicates.py

Findet identische Dateien im Download-Ordner (inkl. Unterordner) durch einen zweistufigen Prozess.

### Funktionsweise

1. **Vorfilterung**: Gruppiert Dateien nach Größe (schnell)
2. **Hash-Vergleich**: Berechnet SHA256 nur für potenzielle Duplikate

### Verwendung

```bash
python find_duplicates.py
```

### Ausgabe

Das Skript erstellt zwei Dateien:

| Datei | Zweck |
|-------|-------|
| `duplikate_bericht.txt` | Lesbarer Bericht mit Statistiken |
| `duplikate_liste.txt` | Maschinenlesbare Liste für `move_duplicates.py` |

### Format der Verarbeitungsliste

```
KEEP|C:\Users\...\Downloads\original.jpg|2048576|a1b2c3d4...
DUPLICATE|C:\Users\...\Downloads\Bilder\kopie.jpg|2048576|a1b2c3d4...
```

- `KEEP` = Original behalten
- `DUPLICATE` = Kann verschoben werden

---

## 📦 move_duplicates.py

Verschiebt gefundene Duplikate in einen separaten Ordner zur manuellen Überprüfung.

> ⚠️ **WICHTIG**: Dieses Skript löscht KEINE Dateien! Es verschiebt sie nur.

### Verwendung

```bash
python move_duplicates.py
```

### Voraussetzung

Die Datei `duplikate_liste.txt` muss existieren (wird von `find_duplicates.py` erstellt).

### Zielordner

Duplikate werden in einen Zeitstempel-Ordner verschoben:
```
Downloads/Duplikate_20260118_103045/
```

### Features

- ✅ Vorschau aller zu verschiebenden Dateien
- ✅ Bestätigung vor dem Verschieben
- ✅ Erhält die relative Ordnerstruktur
- ✅ Automatische Umbenennung bei Namenskonflikten

---

## 🚀 Empfohlener Workflow

```mermaid
graph LR
    A[1. Sortieren] --> B[2. Duplikate finden]
    B --> C[3. Duplikate verschieben]
    C --> D[4. Manuell überprüfen]
    D --> E[5. Ggf. löschen]
```

```bash
# 1. Download-Ordner nach Dateitypen sortieren
python sort_downloads.py

# 2. Duplikate finden und Liste erstellen
python find_duplicates.py

# 3. Duplikate in separaten Ordner verschieben
python move_duplicates.py

# 4. Duplikate-Ordner manuell überprüfen und ggf. löschen
```

---

## 💻 Systemanforderungen

- Python 3.6 oder höher
- Windows (nutzt `Path.home() / "Downloads"` für den Standard-Download-Ordner)
- Keine externen Abhängigkeiten (nur Standardbibliothek)

## 📁 Projektstruktur

```
download_sorter/
├── README.md
├── sort_downloads.py
├── find_duplicates.py
└── move_duplicates.py
```

## ⚠️ Sicherheitshinweise

- **Kein automatisches Löschen**: Alle Skripte fragen vor kritischen Aktionen nach Bestätigung
- **Originale bleiben erhalten**: `move_duplicates.py` verschiebt nur `DUPLICATE`-markierte Dateien
- **Beschränkt auf Downloads**: Alle Skripte arbeiten nur im Download-Ordner

## 📄 Lizenz

MIT License - Frei zur Verwendung und Modifikation.
