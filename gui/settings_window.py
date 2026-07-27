# -*- coding: utf-8 -*-
import os
import customtkinter as ctk
from tkinter import filedialog
from core.constants import THEME

class SettingsMixin:
    """Примесь для логики окна настроек"""

    def open_settings(self):
        top = ctk.CTkToplevel(self)
        top.title("Системные Настройки (Автосохранение)")
        top.geometry("650x580")
        top.transient(self)
        top.grab_set()
        
        tabs = ctk.CTkTabview(top)
        tabs.pack(fill="both", expand=True, padx=15, pady=15)
        
        tab_ui = tabs.add("🎨 Внешний вид")
        tab_sys = tabs.add("⚙️ Система")
        tab_render = tabs.add("🎥 Рендер & GPU") 
        tab_adv = tabs.add("🔧 Дополнительно")
        
        def save_cfg(*args):
            self.config.set("theme_mode", self.s_theme.get())
            self.config.set("accent_color", self.s_accent.get())
            self.config.set("ui_scaling", self.s_scale.get())
            self.config.set("window_alpha", float(self.s_alpha.get()))
            self.config.set("ui_animations", self.s_anim.get())
            
            self.config.set("output_dir", self.s_out.get())
            self.config.set("max_workers", int(self.s_work.get()))
            self.config.set("auto_open", self.s_auto_op.get())
            self.config.set("always_on_top", self.s_top.get())
            self.config.set("delete_mode", self.s_del.get())
            
            self.config.set("processing_mode", self.s_proc.get())
            self.config.set("gpu_preset", self.s_preset.get())
            self.config.set("auto_threads", self.s_athreads.get())
            self.config.set("hwaccel_decode", self.s_hwaccel.get())
            self.config.set("ffmpeg_log", self.s_fflog.get())
            
            self.config.set("save_logs", self.s_logs.get())
            self.config.set("play_sounds", self.s_snd.get())
            self.config.set("clear_cache_exit", self.s_cache.get())
            self.config.set("dev_mode", self.s_dev.get())
            self.config.set("auto_update", self.s_upd.get())
            
            THEME["accent"] = self.s_accent.get()
            self._apply_core_settings()
        
        # TAB 1
        self.s_theme = ctk.StringVar(value=self.config.get("theme_mode"))
        ctk.CTkLabel(tab_ui, text="1. Тема интерфейса:").pack(anchor="w", pady=(5,0))
        ctk.CTkOptionMenu(tab_ui, variable=self.s_theme, values=["Dark", "Light", "System"], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_accent = ctk.StringVar(value=self.config.get("accent_color"))
        ctk.CTkLabel(tab_ui, text="2. Акцентный цвет:").pack(anchor="w")
        ctk.CTkOptionMenu(tab_ui, variable=self.s_accent, values=["#7289DA", "#43B581", "#F04747", "#FAA61A", "#E67E22", "#9B59B6", "#00B0F4"], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_scale = ctk.StringVar(value=self.config.get("ui_scaling"))
        ctk.CTkLabel(tab_ui, text="3. Масштабирование (Требует перезапуск):").pack(anchor="w")
        ctk.CTkOptionMenu(tab_ui, variable=self.s_scale, values=["80%", "90%", "100%", "110%", "120%"], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_alpha = ctk.DoubleVar(value=self.config.get("window_alpha"))
        ctk.CTkLabel(tab_ui, text="4. Прозрачность окна (Alpha):").pack(anchor="w")
        ctk.CTkSlider(tab_ui, variable=self.s_alpha, from_=0.5, to=1.0, command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_anim = ctk.BooleanVar(value=self.config.get("ui_animations"))
        ctk.CTkSwitch(tab_ui, text="5. Анимации интерфейса", variable=self.s_anim, command=save_cfg).pack(anchor="w", pady=10)

        # TAB 2
        self.s_out = ctk.StringVar(value=self.config.get("output_dir"))
        ctk.CTkLabel(tab_sys, text="1. Папка вывода (Output):").pack(anchor="w", pady=(5,0))
        out_fr = ctk.CTkFrame(tab_sys, fg_color="transparent")
        out_fr.pack(fill="x", pady=(0, 10))
        e_out = ctk.CTkEntry(out_fr, textvariable=self.s_out); e_out.pack(side="left", fill="x", expand=True)
        e_out.bind("<KeyRelease>", save_cfg)
        def _pick_dir():
            d = filedialog.askdirectory(); 
            if d: self.s_out.set(d); save_cfg()
        ctk.CTkButton(out_fr, text="📁", width=40, command=_pick_dir).pack(side="right", padx=(5,0))
        
        self.s_work = ctk.StringVar(value=str(self.config.get("max_workers", 2)))
        ctk.CTkLabel(tab_sys, text="2. Ручной лимит потоков (если авто выключено):").pack(anchor="w")
        ctk.CTkOptionMenu(tab_sys, variable=self.s_work, values=[str(i) for i in range(1, os.cpu_count() + 2)], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_del = ctk.StringVar(value=self.config.get("delete_mode"))
        ctk.CTkLabel(tab_sys, text="3. Режим удаления дубликатов:").pack(anchor="w")
        ctk.CTkOptionMenu(tab_sys, variable=self.s_del, values=["Trash", "Permadelete"], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_auto_op = ctk.BooleanVar(value=self.config.get("auto_open"))
        ctk.CTkSwitch(tab_sys, text="4. Авто-открытие папки вывода", variable=self.s_auto_op, command=save_cfg).pack(anchor="w", pady=5)
        
        self.s_top = ctk.BooleanVar(value=self.config.get("always_on_top"))
        ctk.CTkSwitch(tab_sys, text="5. Поверх других окон", variable=self.s_top, command=save_cfg).pack(anchor="w", pady=5)

        # TAB 3 
        self.s_proc = ctk.StringVar(value=self.config.get("processing_mode", "CPU"))
        ctk.CTkLabel(tab_render, text="1. Режим обработки (Видеокарта/Процессор):").pack(anchor="w", pady=(5,0))
        ctk.CTkOptionMenu(tab_render, variable=self.s_proc, values=["CPU", "GPU (NVIDIA)", "GPU (AMD)", "GPU (Intel)"], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_preset = ctk.StringVar(value=self.config.get("gpu_preset", "P4 (Баланс VRAM)"))
        ctk.CTkLabel(tab_render, text="2. Лимит памяти / Пресет (для NVENC):").pack(anchor="w")
        ctk.CTkOptionMenu(tab_render, variable=self.s_preset, values=["P1 (Макс. Скорость)", "P4 (Баланс VRAM)", "P7 (Макс. Качество)"], command=save_cfg).pack(fill="x", pady=(0, 10))
        
        self.s_athreads = ctk.BooleanVar(value=self.config.get("auto_threads", True))
        ctk.CTkSwitch(tab_render, text="3. Умные потоки CPU (Оставляет 2 ядра для UI)", variable=self.s_athreads, command=save_cfg).pack(anchor="w", pady=10)
        
        self.s_hwaccel = ctk.BooleanVar(value=self.config.get("hwaccel_decode", True))
        ctk.CTkSwitch(tab_render, text="4. Аппаратное декодирование (HWAccel)", variable=self.s_hwaccel, command=save_cfg).pack(anchor="w", pady=10)
        
        self.s_fflog = ctk.BooleanVar(value=self.config.get("ffmpeg_log", False))
        ctk.CTkSwitch(tab_render, text="5. Выводить логи FFmpeg в терминал", variable=self.s_fflog, command=save_cfg).pack(anchor="w", pady=10)

        # TAB 4
        self.s_logs = ctk.BooleanVar(value=self.config.get("save_logs"))
        ctk.CTkSwitch(tab_adv, text="1. Сохранять логи в nexus_log.txt", variable=self.s_logs, command=save_cfg).pack(anchor="w", pady=(15, 10))
        
        self.s_snd = ctk.BooleanVar(value=self.config.get("play_sounds"))
        ctk.CTkSwitch(tab_adv, text="2. Звуковые уведомления", variable=self.s_snd, command=save_cfg).pack(anchor="w", pady=10)
        
        self.s_cache = ctk.BooleanVar(value=self.config.get("clear_cache_exit"))
        ctk.CTkSwitch(tab_adv, text="3. Очищать кэш при выходе", variable=self.s_cache, command=save_cfg).pack(anchor="w", pady=10)
        
        self.s_dev = ctk.BooleanVar(value=self.config.get("dev_mode"))
        ctk.CTkSwitch(tab_adv, text="4. Режим разработчика (Дебаг)", variable=self.s_dev, command=save_cfg).pack(anchor="w", pady=10)

        self.s_upd = ctk.BooleanVar(value=self.config.get("auto_update"))
        ctk.CTkSwitch(tab_adv, text="5. Авто-проверка обновлений", variable=self.s_upd, command=save_cfg).pack(anchor="w", pady=10)

        ctk.CTkLabel(top, text="* Настройки сохраняются автоматически при изменении.", text_color=THEME["text_muted"], font=ctk.CTkFont(size=11)).pack(pady=(0, 10))