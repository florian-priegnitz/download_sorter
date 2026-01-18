"""
Duplicate File Finder
Findet doppelte Dateien im Download-Ordner (inkl. Unterordner) basierend auf Dateigröße und Hash.
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict


def calculate_hash(file_path: Path, block_size: int = 65536) -> str:
    """Berechnet den SHA256-Hash einer Datei."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()
    except (PermissionError, OSError) as e:
        return None


def format_size(size_bytes: int) -> str:
    """Formatiert Bytes in lesbare Größe (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def find_duplicates(folder: Path) -> dict:
    """
    Findet doppelte Dateien in einem Ordner (rekursiv).
    
    Strategie:
    1. Gruppiere alle Dateien nach Größe
    2. Für Gruppen mit >1 Datei: Berechne Hash
    3. Gruppiere nach Hash → echte Duplikate
    """
    print(f"📂 Durchsuche: {folder}\n")
    
    # Schritt 1: Alle Dateien nach Größe gruppieren
    print("🔍 Schritt 1: Sammle Dateien und gruppiere nach Größe...")
    size_groups = defaultdict(list)
    file_count = 0
    
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
                file_count += 1
            except (PermissionError, OSError):
                continue
    
    print(f"   ✅ {file_count} Dateien gefunden")
    
    # Nur Größen-Gruppen mit mehr als einer Datei behalten
    potential_duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
    potential_count = sum(len(files) for files in potential_duplicates.values())
    print(f"   📋 {potential_count} potenzielle Duplikate (gleiche Größe)\n")
    
    if not potential_duplicates:
        return {}
    
    # Schritt 2: Hash für potenzielle Duplikate berechnen
    print("🔐 Schritt 2: Berechne Hashes für Kandidaten...")
    hash_groups = defaultdict(list)
    processed = 0
    
    for size, files in potential_duplicates.items():
        for file_path in files:
            file_hash = calculate_hash(file_path)
            if file_hash:
                hash_groups[file_hash].append((file_path, size))
            processed += 1
            # Fortschritt anzeigen
            if processed % 50 == 0:
                print(f"   ⏳ {processed}/{potential_count} Dateien verarbeitet...")
    
    print(f"   ✅ {processed} Dateien gehasht\n")
    
    # Nur echte Duplikate (gleicher Hash) behalten
    duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}
    
    return duplicates


def print_report(duplicates: dict):
    """Gibt einen Bericht über gefundene Duplikate aus."""
    if not duplicates:
        print("=" * 60)
        print("✨ Keine Duplikate gefunden!")
        print("=" * 60)
        return
    
    total_groups = len(duplicates)
    total_files = sum(len(files) for files in duplicates.values())
    total_wasted = sum((len(files) - 1) * files[0][1] for files in duplicates.values())
    
    print("=" * 60)
    print("📊 DUPLIKATE-BERICHT")
    print("=" * 60)
    print(f"\n🔢 Gefundene Duplikat-Gruppen: {total_groups}")
    print(f"📁 Betroffene Dateien: {total_files}")
    print(f"💾 Verschwendeter Speicher: {format_size(total_wasted)}\n")
    print("-" * 60)
    
    for i, (file_hash, files) in enumerate(duplicates.items(), 1):
        size = files[0][1]
        print(f"\n🔹 Gruppe {i} | Größe: {format_size(size)} | Hash: {file_hash[:12]}...")
        print("-" * 40)
        for file_path, _ in files:
            print(f"   📄 {file_path}")
    
    print("\n" + "=" * 60)
    print("💡 Tipp: Überprüfe die Duplikate manuell und lösche die nicht benötigten.")
    print("=" * 60)


def export_report(duplicates: dict, output_file: Path):
    """Exportiert den Bericht in eine Textdatei (lesbar)."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("DUPLIKATE-BERICHT\n")
        f.write("=" * 60 + "\n\n")
        
        if not duplicates:
            f.write("Keine Duplikate gefunden!\n")
            return
        
        total_groups = len(duplicates)
        total_files = sum(len(files) for files in duplicates.values())
        total_wasted = sum((len(files) - 1) * files[0][1] for files in duplicates.values())
        
        f.write(f"Gefundene Duplikat-Gruppen: {total_groups}\n")
        f.write(f"Betroffene Dateien: {total_files}\n")
        f.write(f"Verschwendeter Speicher: {format_size(total_wasted)}\n\n")
        f.write("-" * 60 + "\n")
        
        for i, (file_hash, files) in enumerate(duplicates.items(), 1):
            size = files[0][1]
            f.write(f"\nGruppe {i} | Größe: {format_size(size)} | Hash: {file_hash[:12]}...\n")
            for file_path, _ in files:
                f.write(f"   {file_path}\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"\n📝 Lesbarer Bericht: {output_file}")


def export_for_processing(duplicates: dict, output_file: Path):
    """
    Exportiert Duplikate in einem maschinenlesbaren Format für weitere Verarbeitung.
    
    Format:
    - Leerzeilen trennen Gruppen
    - Erste Zeile jeder Gruppe: #KEEP: (Original behalten)
    - Folgende Zeilen: #DUPLICATE: (können verschoben/gelöscht werden)
    - Jede Zeile enthält: Pfad|Größe_in_Bytes|Hash
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# DUPLIKATE-LISTE FÜR AUTOMATISCHE VERARBEITUNG\n")
        f.write("# Format: Aktion|Pfad|Größe|Hash\n")
        f.write("# KEEP = Original behalten, DUPLICATE = kann verschoben werden\n")
        f.write("#" + "=" * 60 + "\n\n")
        
        for file_hash, files in duplicates.items():
            # Erste Datei als "Original" markieren (behalten)
            first_file, size = files[0]
            f.write(f"KEEP|{first_file}|{size}|{file_hash}\n")
            
            # Restliche als Duplikate markieren (können verschoben werden)
            for file_path, size in files[1:]:
                f.write(f"DUPLICATE|{file_path}|{size}|{file_hash}\n")
            
            f.write("\n")  # Leerzeile zwischen Gruppen
    
    print(f"📋 Verarbeitungsliste: {output_file}")


def main():
    print("=" * 60)
    print("🔍 Duplikat-Finder für Download-Ordner")
    print("=" * 60 + "\n")
    
    # Download-Ordner (Windows Standard)
    download_folder = Path.home() / "Downloads"
    
    if not download_folder.exists():
        print(f"❌ Download-Ordner nicht gefunden: {download_folder}")
        return
    
    # Duplikate finden
    duplicates = find_duplicates(download_folder)
    
    # Bericht ausgeben
    print_report(duplicates)
    
    # Optional: Berichte exportieren
    if duplicates:
        response = input("\n📝 Berichte als Textdateien speichern? (j/n): ")
        if response.lower() in ["j", "ja", "y", "yes"]:
            # Lesbarer Bericht
            report_file = download_folder / "duplikate_bericht.txt"
            export_report(duplicates, report_file)
            
            # Maschinenlesbare Liste für weitere Verarbeitung
            processing_file = download_folder / "duplikate_liste.txt"
            export_for_processing(duplicates, processing_file)
            
            print(f"\n💡 Die Datei 'duplikate_liste.txt' kann von einem weiteren Skript")
            print(f"   eingelesen werden, um Duplikate automatisch zu verschieben.")


if __name__ == "__main__":
    main()
