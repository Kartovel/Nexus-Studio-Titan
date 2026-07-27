# -*- coding: utf-8 -*-
import os
import shutil
import re
import time
from tkinter import filedialog, messagebox
from core.constants import THEME
from core.utils import open_folder, get_file_hash

class SystemUtilsTasksMixin:
    """Задачи: Файлы и Утилиты"""

    def task_sort_files(self):
        folder = filedialog.askdirectory(title="Свалка файлов для сортировки")
        if not folder: return
        out_d = self.get_out_dir("Sorted_Files")
        
        ext_map = {
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            "Video": ['.mp4', '.avi', '.mkv', '.mov', '.webm'],
            "Audio": ['.mp3', '.wav', '.ogg', '.flac'],
            "Documents": ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.csv'],
            "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz'],
            "Executables": ['.exe', '.msi', '.apk', '.bat', '.sh'],
            "Code": ['.py', '.js', '.html', '.css', '.cpp', '.json', '.lua']
        }
        
        s = 0
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        for i, f in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            ext = os.path.splitext(f)[1].lower()
            target_cat = "Others"
            for cat, exts in ext_map.items():
                if ext in exts: target_cat = cat; break
            
            cat_dir = os.path.join(out_d, target_cat)
            os.makedirs(cat_dir, exist_ok=True)
            try: 
                shutil.copy2(os.path.join(folder, f), os.path.join(cat_dir, f)); s+=1
            except Exception as e: self.log_error(f"Сбой сортировки {f}: {e}")
            
        self.log_info(f"Рассортировано {s} файлов."); open_folder(out_d)

    def task_clean_empty_dirs(self):
        folder = filedialog.askdirectory()
        if not folder: return
        s = 0
        for root, dirs, files in os.walk(folder, topdown=False):
            if self.cancel_flag: break
            for d in dirs:
                dir_p = os.path.join(root, d)
                try: 
                    if not os.listdir(dir_p): os.rmdir(dir_p); s += 1
                except Exception: pass
        self.log_info(f"Удалено пустых папок: {s}")

    def task_bulk_rename(self):
        folder = filedialog.askdirectory()
        if not folder: return
        fnd = self.rn_find.get(); repl = self.rn_repl.get(); out_d = self.get_out_dir("Renamed")
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        s = 0
        for i, f in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            name, ext = os.path.splitext(f)
            if fnd:
                try: name = re.sub(fnd, repl, name)
                except: name = name.replace(fnd, repl)
            try: 
                shutil.copy2(os.path.join(folder, f), os.path.join(out_d, f"{name}{ext}")); s += 1
            except Exception as e: self.log_error(f"Сбой переименования {f}: {e}")
            
        self.log_info(f"Переименовано: {s}"); open_folder(out_d)

    def task_find_duplicates(self):
        folder = filedialog.askdirectory()
        if not folder: return
        out_d = self.get_out_dir("Duplicates")
        del_mode = self.config.get("delete_mode") == "Permadelete"
        
        if del_mode and not messagebox.askyesno("ВНИМАНИЕ", "Файлы будут УДАЛЕНЫ БЕЗВОЗВРАТНО. Продолжить?"): return

        hashes = {}; dups = []; files = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs]
        for i, fp in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files), f"Хеширование {i+1}/{len(files)}...")
            try:
                # Использование новой memory-safe функции
                h = get_file_hash(fp)
                if h in hashes: dups.append(fp)
                else: hashes[h] = fp
            except Exception as e: self.log_error(f"Ошибка чтения {fp}: {e}")
            
        self.log_info(f"Дубликатов: {len(dups)}")
        for i, dup in enumerate(dups):
            if self.cancel_flag: break
            self.set_progress(i/len(dups), "Очистка...")
            try:
                if del_mode: os.remove(dup)
                else: shutil.move(dup, os.path.join(out_d, f"dup_{int(time.time())}_{os.path.basename(dup)}"))
            except Exception as e: self.log_error(f"Не удалось удалить {dup}: {e}")
            
        if not del_mode and dups: open_folder(out_d)

    def task_file_shredder(self):
        files = filedialog.askopenfilenames()
        if not files: return
        if not messagebox.askyesno("КРИТИЧЕСКИ", "Файлы будут ПЕРЕЗАПИСАНЫ нулями и удалены навсегда. Вы уверены?"): return
        s = 0
        chunk_size = 1024 * 1024 # 1 Мегабайт
        
        for i, fp in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files), f"Уничтожение {i+1}/{len(files)}...")
            try:
                file_size = os.path.getsize(fp)
                # Безопасная блочная перезапись вместо помещения файла целиком в ОЗУ
                with open(fp, 'r+b') as f:
                    written = 0
                    while written < file_size:
                        write_size = min(chunk_size, file_size - written)
                        f.write(os.urandom(write_size))
                        written += write_size
                os.remove(fp)
                s += 1
            except Exception as e: self.log_error(f"Ошибка шрединга {fp}: {e}")
            
        self.log_info(f"Уничтожено файлов: {s}", THEME["danger"])