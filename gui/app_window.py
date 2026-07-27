# -*- coding: utf-8 -*-
import os
import queue
import threading
import time
import shutil
import concurrent.futures
from datetime import datetime
from tkinter import messagebox
import customtkinter as ctk

from core.constants import THEME, DEFAULT_OUTPUT_DIR, CONFIG_FILE, BASE_DIR
from core.config import ConfigManager

# Импорт Mixins (частей класса)
from gui.ui_builder import UIBuilderMixin
from gui.settings_window import SettingsMixin
from modules.modding import ModdingTasksMixin
from modules.audio_video import AudioVideoTasksMixin
from modules.images import ImageTasksMixin
from modules.scripts import ScriptTasksMixin
from modules.system_utils import SystemUtilsTasksMixin
from modules.image_cli_tools import ImageCliToolsMixin # ИСПРАВЛЕНИЕ: Добавлен импорт миксина CLI утилит

class NexusTitanApp(
    ctk.CTk, 
    UIBuilderMixin, 
    SettingsMixin, 
    ModdingTasksMixin, 
    AudioVideoTasksMixin, 
    ImageTasksMixin, 
    ScriptTasksMixin, 
    SystemUtilsTasksMixin,
    ImageCliToolsMixin # ИСПРАВЛЕНИЕ: Добавлен миксин в список наследования
):
    """Главный класс приложения, собирающий все модули воедино"""
    
    def __init__(self):
        super().__init__()
        
        self.config = ConfigManager(CONFIG_FILE)
        # Принудительно применяем обновленный акцент из констант, если он не переопределен пользователем
        THEME["accent"] = self.config.get("accent_color", THEME["accent"])
        self._apply_core_settings()
        
        self.title("Nexus Studio Titan ⚡ v6.3 AI Ultimate")
        self.geometry("1400x950") # Чуть шире для новых карточек
        self.minsize(1200, 800)
        
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        
        self.is_processing = False
        self.cancel_flag = False 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.frames = {}
        self.current_frame = None
        
        self._build_sidebar()
        self._build_main_area()
        self._build_footer()
        
        self._start_queue_listeners()
        
        self.select_frame("home")
        self.log_info("Nexus Titan v6.3 (AI Edition) инициализирован.", THEME["success"])

    def _apply_core_settings(self):
        ctk.set_appearance_mode(self.config.get("theme_mode"))
        scale_str = self.config.get("ui_scaling", "100%")
        scale_val = float(scale_str.replace("%", "")) / 100.0
        ctk.set_widget_scaling(scale_val)
        
        if self.config.get("always_on_top"): self.attributes('-topmost', True)
        else: self.attributes('-topmost', False)
        
        self.attributes('-alpha', self.config.get("window_alpha", 1.0))
        self.configure(fg_color=THEME["bg_main"])

    def get_out_dir(self, subfolder=""):
        base = self.config.get("output_dir")
        if not base: base = DEFAULT_OUTPUT_DIR
        path = os.path.join(base, subfolder) if subfolder else base
        os.makedirs(path, exist_ok=True)
        return path

    def get_active_workers(self):
        if self.config.get("auto_threads"):
            # Оптимизация Шаг 1: Оставляем 1 поток системе, остальные забираем
            return max(1, (os.cpu_count() or 4) - 1)
        return int(self.config.get("max_workers", 2))

    def _start_queue_listeners(self):
        try:
            while True:
                msg, color = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                tag = f"color_{color.replace('#', '')}" if color else None
                if tag: self.log_box.tag_config(tag, foreground=color)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_line = f"[{timestamp}] root@titan:~# {msg}\n"
                self.log_box.insert("end", log_line, tag if tag else "None")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
                
                if self.config.get("save_logs"):
                    try:
                        with open(os.path.join(BASE_DIR, "nexus_log.txt"), 'a', encoding='utf-8') as f:
                            f.write(log_line)
                    except Exception: pass
        except queue.Empty: pass

        try:
            while True:
                progress, text = self.progress_queue.get_nowait()
                self.progress_bar.set(progress)
                self.progress_pct.configure(text=f"{int(progress * 100)}%")
                if text: self.status_lbl.configure(text=text)
        except queue.Empty: pass

        self.after(50, self._start_queue_listeners)

    def log_info(self, msg, color=THEME["text_main"]): self.log_queue.put((msg, color))
    def log_error(self, msg): self.log_queue.put((f"ERROR: {msg}", THEME["danger"]))
    def set_progress(self, val, txt=None): self.progress_queue.put((val, txt))

    def _cancel_task(self):
        if self.is_processing:
            self.cancel_flag = True
            self.log_info("Сигнал прерывания отправлен. Остановка воркеров...", THEME["warning"])
            self.cancel_btn.configure(state="disabled")

    def start_task(self, task_func):
        if self.is_processing: return messagebox.showwarning("Ядро занято", "Дождитесь окончания текущей задачи.")
        self.is_processing = True; self.cancel_flag = False; self.cancel_btn.configure(state="normal")
        self.set_progress(0.0, "Инициализация...")
        
        def wrapper():
            st = time.time()
            try:
                task_func()
                if self.cancel_flag: self.log_info("Задача прервана.", THEME["warning"]); self.set_progress(0.0, "Прервано")
                else: self.log_info(f"Успешно. ({time.time() - st:.2f} сек)", THEME["success"]); self.set_progress(1.0, "Завершено!")
            except Exception as e:
                self.log_error(str(e)); self.set_progress(0.0, "Критический сбой")
            finally:
                self.is_processing = False; self.cancel_btn.configure(state="disabled")
        threading.Thread(target=wrapper, daemon=True).start()

    def clear_results(self):
        out_d = self.get_out_dir()
        if messagebox.askyesno("Очистка", "Полностью уничтожить содержимое папки Output?"):
            try: shutil.rmtree(out_d); os.makedirs(out_d); self.log_info("Output очищен.", THEME["warning"])
            except Exception as e: self.log_error(f"Сбой очистки: {e}")

    # --- ШАГ 1: ОПТИМИЗАЦИЯ СКОРОСТИ (Улучшенный run_parallel) ---
    def run_parallel(self, func, items, desc="Process"):
        """
        Многопоточный раннер. Теперь использует пулы эффективнее.
        Для сверхбыстрых задач (например, ренейм) лучше использовать os.walk, но для тяжелых (FFmpeg, PIL, AI) 
        ThreadPoolExecutor подходит отлично, так как снимает GIL (Global Interpreter Lock) на уровне C-расширений.
        """
        total = len(items)
        if total == 0: return 0, 0
        success = 0
        workers = min(total, self.get_active_workers())
        self.log_info(f"Инициализация пула: {workers} потоков.", THEME["info"])
        
        # Используем ThreadPoolExecutor для IO-bound и C-bound задач
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(func, item): item for item in items}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self.cancel_flag: 
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                self.set_progress((i + 1) / total, f"{desc} ({i+1}/{total})")
                try: 
                    future.result()
                    success += 1
                except Exception as e: 
                    self.log_error(f"Ошибка в потоке: {str(e)}")
        return success, total

    def render_video_with_fallback(self, clip, out_path, audio=True):
        mode = self.config.get("processing_mode", "CPU")
        preset_val = self.config.get("gpu_preset", "P4")
        threads = self.get_active_workers()
        preset_str = preset_val.split()[0].lower()
        
        codec_map = {
            "GPU (NVIDIA)": ("h264_nvenc", ["-preset", preset_str]),
            "GPU (AMD)": ("h264_amf", ["-quality", "balanced"]),
            "GPU (Intel)": ("h264_qsv", ["-preset", "medium"])
        }
        
        codec, ffmpeg_params = codec_map.get(mode, ("libx264", ["-preset", "fast"]))
        
        if codec != "libx264":
            self.log_info(f"Запуск аппаратного рендера [{codec}]...", THEME["info"])
            try:
                clip.write_videofile(out_path, codec=codec, ffmpeg_params=ffmpeg_params, threads=threads, logger=None, audio=audio)
                return True
            except Exception as e:
                err_msg = str(e).split('\n')[-1] if str(e) else "Unknown"
                self.log_error(f"Сбой GPU рендера ({codec}): {err_msg[:80]}")
                self.log_info("Выполняется прозрачный Fallback на процессор (CPU)...", THEME["warning"])
        
        self.log_info(f"Запуск CPU-рендера [libx264, потоков: {threads}]...", THEME["warning"])
        clip.write_videofile(out_path, codec="libx264", ffmpeg_params=["-preset", "fast"], threads=threads, logger=None, audio=audio)
        return True