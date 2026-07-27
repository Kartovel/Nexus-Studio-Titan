# -*- coding: utf-8 -*-
"""
Nexus Studio Titan ⚡ (Version 6.2 AI Ultimate GPU Edition - Modular)
"""

import os
import sys
import glob
import PIL.Image

# =====================================================================
# ГЛОБАЛЬНЫЕ ФИКСЫ И ПУТИ К РЕСУРСАМ
# =====================================================================
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def get_resource_path(relative_path):
    """
    Получает абсолютный путь к ресурсам. 
    Отлично работает как для разработки (.py), так и для приложения, 
    установленного через Inno Setup в Program Files.
    """
    if getattr(sys, 'frozen', False):
        # sys.executable вернет путь к C:\Program Files\NexusStudio\NexusStudio_Titan.exe
        # а os.path.dirname получит папку C:\Program Files\NexusStudio
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Если запущена как обычный .py скрипт
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

# Автоматически добавляем корень программы и папку tools в системный PATH приложения.
if getattr(sys, 'frozen', False):
    app_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    
    # Добавляем корень программы в PATH
    os.environ["PATH"] += os.pathsep + app_dir
    # Добавляем папку tools в PATH (чтобы утилиты вызывались без путей)
    os.environ["PATH"] += os.pathsep + os.path.join(app_dir, "tools")
    
    # ФИКС ДЛЯ АВТОНОМНОСТИ MOVIEPY И FFMPEG:
    ffmpeg_executables = glob.glob(os.path.join(app_dir, "*ffmpeg*.exe"))
    if ffmpeg_executables:
        os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_executables[0]

from gui.app_window import NexusTitanApp

if __name__ == "__main__":
    # Фикс масштабирования для Windows (чтобы шрифты не мылились)
    if os.name == 'nt':
        try: 
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except: 
            pass
            
    app = NexusTitanApp()
    app.mainloop()