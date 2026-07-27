# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import hashlib

def open_folder(path):
    if not os.path.exists(path): return
    try:
        if os.name == 'nt': os.startfile(path)
        elif sys.platform == 'darwin': subprocess.Popen(['open', path])
        else: subprocess.Popen(['xdg-open', path])
    except Exception as e:
        print(f"Ошибка открытия папки: {e}")

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()

# Memory-Safe генерация хеша (для файлов любого размера)
def get_file_hash(filepath, chunk_size=65536):
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()