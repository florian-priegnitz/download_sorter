"""
Duplicate Mover
Liest die Duplikate-Liste und verschiebt markierte Duplikate in einen speziellen Ordner.

WICHTIG: Dieses Skript LÖSCHT KEINE Dateien!
         Es werden nur Dateien in den Duplikate-Ordner VERSCHOBEN.
         Du kannst sie dort überprüfen und selbst entscheiden, ob du sie löschen möchtest.
"""

import shutil
from pathlib import Path
from datetime import datetime


def read_duplicate_list(list_file: Path) -> list:
    """
    Liest die maschinenlesbare Duplikate-Liste.
    Gibt eine Liste von Tupeln zurück: (action, path, size, hash)
    """
    duplicates = []
    
    if not list_file.exists():
        print(f"❌ Datei nicht gefunden: {list_file}")
        return duplicates
    
    with open(list_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Kommentare und Leerzeilen überspringen
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) == 4:
                action, path, size, file_hash = parts
                duplicates.append({
                    'action': action,
                    'path': Path(path),
                    'size': int(size),
                    'hash': file_hash
                })
    
    return duplicates


def format_size(size_bytes: int) -> str:
    """Formatiert Bytes in lesbare Größe."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def move_duplicates(duplicates: list, target_folder: Path) -> tuple:
    """
    Verschiebt alle als DUPLICATE markierten Dateien in den Zielordner.
    Behält die Ordnerstruktur relativ zum Download-Ordner bei.
    """
    moved = 0
    failed = 0
    freed_space = 0
    
    download_folder = Path.home() / "Downloads"
    
    for entry in duplicates:
        if entry['action'] != 'DUPLICATE':
            continue
        
        source = entry['path']
        
        if not source.exists():
            print(f"⚠️ Datei nicht gefunden: {source.name}")
            failed += 1
            continue
        
        # Relativen Pfad zum Download-Ordner beibehalten
        try:
            relative_path = source.relative_to(download_folder)
        except ValueError:
            # Datei nicht im Download-Ordner
            relative_path = source.name
        
        target = target_folder / relative_path
        
        # Zielordner erstellen
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Bei Namenskonflikt umbenennen
        if target.exists():
            base = target.stem
            ext = target.suffix
            counter = 1
            while target.exists():
                target = target.parent / f"{base}_{counter}{ext}"
                counter += 1
        
        try:
            shutil.move(str(source), str(target))
            print(f"✅ {source.name} → Duplikate/")
            moved += 1
            freed_space += entry['size']
        except Exception as e:
            print(f"❌ Fehler bei {source.name}: {e}")
            failed += 1
    
    return moved, failed, freed_space


def main():
    print("=" * 60)
    print("📦 Duplikate-Verschieber")
    print("=" * 60 + "\n")
    
    download_folder = Path.home() / "Downloads"
    list_file = download_folder / "duplikate_liste.txt"
    
    # Duplikate-Liste einlesen
    print(f"📄 Lese Liste: {list_file}\n")
    duplicates = read_duplicate_list(list_file)
    
    if not duplicates:
        print("❌ Keine Duplikate in der Liste gefunden.")
        print("   Führe zuerst 'find_duplicates.py' aus und speichere die Berichte.")
        return
    
    # Statistik anzeigen
    keep_count = sum(1 for d in duplicates if d['action'] == 'KEEP')
    dup_count = sum(1 for d in duplicates if d['action'] == 'DUPLICATE')
    total_size = sum(d['size'] for d in duplicates if d['action'] == 'DUPLICATE')
    
    print(f"📊 Gefunden in Liste:")
    print(f"   ✅ Originale (KEEP): {keep_count}")
    print(f"   📋 Duplikate (DUPLICATE): {dup_count}")
    print(f"   💾 Freizugebender Speicher: {format_size(total_size)}\n")
    
    # Vorschau der zu verschiebenden Dateien
    print("-" * 60)
    print("📋 Zu verschiebende Dateien:\n")
    for entry in duplicates:
        if entry['action'] == 'DUPLICATE':
            print(f"   📄 {entry['path'].name} ({format_size(entry['size'])})")
    print("\n" + "-" * 60)
    
    # Zielordner
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_folder = download_folder / f"Duplikate_{timestamp}"
    
    print(f"\n📂 Zielordner: {target_folder}\n")
    
    # Bestätigung
    response = input("🔄 Duplikate jetzt verschieben? (j/n): ")
    if response.lower() not in ["j", "ja", "y", "yes"]:
        print("\n❌ Abgebrochen.")
        return
    
    print("\n" + "=" * 60)
    print("🚀 Verschiebe Duplikate...\n")
    
    # Zielordner erstellen
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Duplikate verschieben
    moved, failed, freed = move_duplicates(duplicates, target_folder)
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"   ✅ Verschoben: {moved} Dateien")
    print(f"   ❌ Fehlgeschlagen: {failed} Dateien")
    print(f"   💾 Freigegebener Speicher: {format_size(freed)}")
    print(f"   📂 Zielordner: {target_folder}")
    print("=" * 60)
    
    if moved > 0:
        print("\n💡 Die Duplikate wurden in den Ordner verschoben.")
        print("   Du kannst den Ordner überprüfen und bei Bedarf löschen.")


if __name__ == "__main__":
    main()
