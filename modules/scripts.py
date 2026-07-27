# -*- coding: utf-8 -*-
import os
import base64
import json
import time
import string
import secrets
from tkinter import filedialog
from core.constants import THEME
from core.utils import open_folder

class ScriptTasksMixin:
    """Задачи: Текст и Скрипты"""

    def task_base64(self):
        files = filedialog.askopenfilenames(filetypes=[("Text", "*.txt *.json *.lua *.cfg")])
        if not files: return
        out_d = self.get_out_dir("Base64_Result")
        mode = self.b64_mode.get()
        
        s = 0
        for i, fp in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            try:
                with open(fp, 'rb') as f: data = f.read()
                out_p = os.path.join(out_d, f"{os.path.basename(fp)}.b64.txt")
                if "Зашифровать" in mode: res = base64.b64encode(data)
                else: res = base64.b64decode(data); out_p = out_p.replace('.b64.txt', '.dec.txt')
                with open(out_p, 'wb') as f: f.write(res)
                s += 1
            except Exception as e: self.log_error(f"Base64 сбой {fp}: {e}")
            
        self.log_info(f"Base64 операция завершена: {s} файлов."); open_folder(out_d)

    def task_pass_gen(self):
        out_d = self.get_out_dir()
        out_p = os.path.join(out_d, f"Passwords_{int(time.time())}.txt")
        try:
            count = int(self.pass_count.get()); length = int(self.pass_len.get())
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            with open(out_p, 'w') as f:
                for i in range(count):
                    # Использование криптографически безопасного модуля secrets вместо random
                    f.write(''.join(secrets.choice(chars) for _ in range(length)) + '\n')
            self.log_info(f"Сгенерировано {count} SECURE паролей."); open_folder(out_d)
        except Exception as e: self.log_error(f"Ошибка генерации: {e}")

    def task_fix_encoding(self):
        folder = filedialog.askdirectory()
        if not folder: return
        out_d = self.get_out_dir("Text_UTF8"); enc = self.enc_val.get(); exts = tuple(self.enc_exts.get().split())
        files = [f for f in os.listdir(folder) if f.lower().endswith(exts)]
        s = 0
        for i, f in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            try:
                with open(os.path.join(folder, f), 'r', encoding=enc, errors='ignore') as f_in: c = f_in.read()
                with open(os.path.join(out_d, f), 'w', encoding='utf-8') as f_out: f_out.write(c)
                s += 1
            except Exception as e: self.log_error(f"Сбой кодировки {f}: {e}")
        self.log_info(f"Кодировка исправлена: {s}"); open_folder(out_d)

    def task_format_json(self):
        folder = filedialog.askdirectory()
        if not folder: return
        out_d = self.get_out_dir("JSON_Fmt"); mini = "Минификация" in self.json_mode.get()
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        s = 0
        for i, f in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            try:
                with open(os.path.join(folder, f), 'r', encoding='utf-8') as jf: data = json.load(jf)
                with open(os.path.join(out_d, f), 'w', encoding='utf-8') as jf:
                    json.dump(data, jf, separators=(',', ':') if mini else None, indent=None if mini else 4)
                s+=1
            except Exception as e: self.log_error(f"Сбой JSON {f}: {e}")
        self.log_info(f"JSON готов: {s}"); open_folder(out_d)