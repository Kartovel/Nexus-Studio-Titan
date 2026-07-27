# -*- coding: utf-8 -*-
import os
from tkinter import filedialog
from PIL import Image
from core.utils import open_folder
from core.constants import THEME
from moviepy.editor import AudioFileClip

class ModdingTasksMixin:
    """Задачи: Моддинг и Source Engine"""

    def task_vmt_gen(self):
        folder = filedialog.askdirectory(title="Папка с текстурами (.vtf)")
        if not folder: return
        shader = self.vmt_shader.get()
        base_p = self.vmt_path.get().strip()
        if base_p and not base_p.endswith('/'): base_p += '/'
        
        out_d = self.get_out_dir("VMT_Generated")
        files = [f for f in os.listdir(folder) if f.lower().endswith('.vtf')]
        if not files: return self.log_error("Не найдено .vtf файлов в папке.")
        
        s = 0
        for i, f in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            name = os.path.splitext(f)[0]
            content = f'"{shader}"\n{{\n\t"$basetexture" "{base_p}{name}"\n\t"$surfaceprop" "default"\n}}'
            try:
                with open(os.path.join(out_d, f"{name}.vmt"), 'w', encoding='utf-8') as out_f:
                    out_f.write(content)
                s += 1
            except Exception as e: self.log_error(f"Ошибка записи VMT {name}: {e}")
            
        self.log_info(f"Сгенерировано VMT: {s}/{len(files)}")
        if s > 0 and self.config.get("auto_open"): open_folder(out_d)

    def task_gmod_wav(self):
        files = filedialog.askopenfilenames(filetypes=[("WAV Audio", "*.wav")])
        if not files: return
        out_d = self.get_out_dir("GMod_Audio")
        fps = int(self.gmod_hz.get()); ch = 1 if self.gmod_ch.get() == "Моно" else 2

        def _w(f):
            clip = None
            try:
                clip = AudioFileClip(f)
                clip.write_audiofile(os.path.join(out_d, os.path.basename(f)), fps=fps, nbytes=2, codec='pcm_s16le', ffmpeg_params=["-ac", str(ch)], logger=None)
            finally:
                if clip: clip.close() # Предотвращение утечки памяти

        s, t = self.run_parallel(_w, files, "Source WAV"); self.log_info(f"WAV готово: {s}/{t}")
        if s > 0 and self.config.get("auto_open"): open_folder(out_d)

    def task_dds_to_png(self):
        files = filedialog.askopenfilenames(filetypes=[("DDS", "*.dds")])
        if not files: return
        out_d = self.get_out_dir("DDS_to_PNG")
        def _dds(f):
            with Image.open(f) as img: img.save(os.path.join(out_d, f"{os.path.splitext(os.path.basename(f))[0]}.png"), "PNG")
        s, t = self.run_parallel(_dds, files, "DDS Extract"); self.log_info(f"DDS извлечено: {s}/{t}")
        if s > 0 and self.config.get("auto_open"): open_folder(out_d)

    def task_gmod_lua_fix(self):
        folder = filedialog.askdirectory()
        if not folder: return
        out_d = self.get_out_dir("Lua_Fixed")
        files = [os.path.join(r, f) for r, d, fs in os.walk(folder) for f in fs if f.lower().endswith(('.lua', '.txt'))]
        
        s = 0
        for i, fp in enumerate(files):
            if self.cancel_flag: break
            self.set_progress(i/len(files))
            content = None
            for enc in ['utf-8', 'windows-1251', 'cp866', 'latin-1']:
                try:
                    with open(fp, 'r', encoding=enc) as f_in: content = f_in.read(); break
                except Exception: continue
                
            if content is not None:
                out_p = os.path.join(out_d, os.path.relpath(fp, folder))
                os.makedirs(os.path.dirname(out_p), exist_ok=True)
                try:
                    with open(out_p, 'w', encoding='utf-8', newline='\n') as f_out: f_out.write(content); s += 1
                except Exception as e: self.log_error(f"Ошибка сохранения: {e}")
                
        self.log_info(f"Скрипты вылечены: {s}"); open_folder(out_d)