"""
Download Folder Sorter
Sortiert Dateien im Download-Ordner basierend auf dem Dateityp in entsprechende Unterordner.
"""

import os
import shutil
from pathlib import Path

# Dateityp-Kategorien mit zugehörigen Erweiterungen
FILE_CATEGORIES = {
    "Bilder": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".heic"],
    "Dokumente": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Programme": [".exe", ".msi", ".dmg", ".deb", ".rpm"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".sql"],
    "Sonstiges": []  # Für alle anderen Dateitypen
}


def get_category(file_extension: str) -> str:
    """Ermittelt die Kategorie basierend auf der Dateierweiterung."""
    file_extension = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension in extensions:
            return category
    return "Sonstiges"


def sort_downloads():
    """Sortiert alle Dateien im Download-Ordner in kategoriebasierte Unterordner."""
    # Download-Ordner Pfad (Windows Standard)
    download_folder = Path.home() / "Downloads"
    
    if not download_folder.exists():
        print(f"❌ Download-Ordner nicht gefunden: {download_folder}")
        return
    
    print(f"📂 Sortiere Dateien in: {download_folder}\n")
    
    moved_count = 0
    skipped_count = 0
    
    # Alle Dateien im Download-Ordner durchgehen
    for item in download_folder.iterdir():
        # Nur Dateien verarbeiten, keine Ordner
        if item.is_file():
            # Kategorie basierend auf Erweiterung bestimmen
            category = get_category(item.suffix)
            
            # Zielordner erstellen, falls nicht vorhanden
            target_folder = download_folder / category
            target_folder.mkdir(exist_ok=True)
            
            # Zieldatei-Pfad
            target_path = target_folder / item.name
            
            # Falls Datei mit gleichem Namen existiert, umbenennen
            if target_path.exists():
                base_name = item.stem
                extension = item.suffix
                counter = 1
                while target_path.exists():
                    target_path = target_folder / f"{base_name}_{counter}{extension}"
                    counter += 1
            
            try:
                # Datei verschieben
                shutil.move(str(item), str(target_path))
                print(f"✅ {item.name} → {category}/")
                moved_count += 1
            except Exception as e:
                print(f"⚠️ Fehler bei {item.name}: {e}")
                skipped_count += 1
    
    print(f"\n{'='*50}")
    print(f"📊 Zusammenfassung:")
    print(f"   ✅ Verschoben: {moved_count} Dateien")
    print(f"   ⚠️ Übersprungen: {skipped_count} Dateien")
    print(f"{'='*50}")


if __name__ == "__main__":
    print("=" * 50)
    print("🗂️  Download-Ordner Sortierer")
    print("=" * 50 + "\n")
    
    # Sicherheitsabfrage
    response = input("Möchtest du den Download-Ordner jetzt sortieren? (j/n): ")
    if response.lower() in ["j", "ja", "y", "yes"]:
        sort_downloads()
        print("\n✨ Sortierung abgeschlossen!")
    else:
        print("\n❌ Sortierung abgebrochen.")
