# -*- coding: utf-8 -*-
import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False): return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()

# =====================================================================
# ИСПРАВЛЕНИЕ ОШИБКИ ДОСТУПА (WinError 5)
# =====================================================================
# Находим папку "Документы" текущего пользователя
USER_DOCUMENTS = os.path.join(os.path.expanduser('~'), 'Documents')

# Создаем главную папку программы в Документах (чтобы не мусорить в корне)
APP_WORKSPACE_DIR = os.path.join(USER_DOCUMENTS, "NexusStudio")

# Теперь папка с результатами и файл настроек хранятся безопасно
DEFAULT_OUTPUT_DIR = os.path.join(APP_WORKSPACE_DIR, "Nexus_Output")
CONFIG_FILE = os.path.join(APP_WORKSPACE_DIR, "nexus_config_v6.json")

# Гарантируем, что папки существуют при старте программы
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
# =====================================================================

# Обновленная, более сочная и современная палитра (в стиле Discord/Cyberpunk)
THEME = {
    "bg_main": "#0b0c10",          # Глубокий темный фон
    "sidebar": "#1f2833",          # Чуть светлее для сайдбара
    "card_bg": "#151821",          # Фон карточек (с легким синим оттенком)
    "accent": "#66fcf1",           # Яркий неоновый циан
    "accent_hover": "#45a29e",     # Приглушенный циан для наведения
    "success": "#2ecc71",          # Яркий зеленый
    "danger": "#e74c3c",           # Сочный красный
    "warning": "#f39c12",          # Теплый оранжевый
    "info": "#3498db",             # Яркий синий
    "text_main": "#ffffff",        # Белый текст
    "text_muted": "#c5c6c7"        # Приятный серый текст
}

DEFAULT_CONFIG = {
    "theme_mode": "Dark",
    "accent_color": THEME["accent"],
    "ui_scaling": "100%",
    "window_alpha": 1.0,
    "ui_animations": True,
    "output_dir": DEFAULT_OUTPUT_DIR,
    "max_workers": max(1, (os.cpu_count() or 4) - 2),
    "auto_open": True,
    "always_on_top": False,
    "delete_mode": "Trash",
    "save_logs": False,
    "play_sounds": False,
    "clear_cache_exit": False,
    "dev_mode": False,
    "auto_update": True,
    "processing_mode": "CPU",
    "gpu_preset": "P4 (Баланс VRAM)", 
    "auto_threads": True,     
    "hwaccel_decode": True,   
    "ffmpeg_log": False
}