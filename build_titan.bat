@echo off
chcp 65001 >nul
pushd "%~dp0"

echo ========================================================
echo        Сборка Nexus Studio Titan (Модульная версия)
echo ========================================================
echo.
echo Рабочая директория: %cd%
echo.

echo Проверка наличия CLI-утилит...
set "MISSING=0"

if exist "tools\dither.exe" ( echo [ОК] dither.exe найден! ) else ( echo [ОШИБКА] tools\dither.exe не найден! & set "MISSING=1" )
if exist "tools\floyd-steinberg.exe" ( echo [ОК] floyd-steinberg.exe найден! ) else ( echo [ОШИБКА] tools\floyd-steinberg.exe не найден! & set "MISSING=1" )
if exist "tools\guetzli.exe" ( echo [ОК] guetzli.exe найден! ) else ( echo [ОШИБКА] @echo off
chcp 65001 >nul
pushd "%~dp0"

echo ========================================================
echo        Сборка Nexus Studio Titan (Для установщика)
echo ========================================================
echo.
echo Рабочая директория: %cd%
echo.

echo Проверка наличия CLI-утилит...
set "MISSING=0"

if exist "tools\dither.exe" ( echo [ОК] dither.exe найден! ) else ( echo [ОШИБКА] tools\dither.exe не найден! & set "MISSING=1" )
if exist "tools\floyd-steinberg.exe" ( echo [ОК] floyd-steinberg.exe найден! ) else ( echo [ОШИБКА] tools\floyd-steinberg.exe не найден! & set "MISSING=1" )
if exist "tools\guetzli.exe" ( echo [ОК] guetzli.exe найден! ) else ( echo [ОШИБКА] tools\guetzli.exe не найден! & set "MISSING=1" )
if exist "tools\sstrip.exe" ( echo [ОК] sstrip.exe найден! ) else ( echo [ОШИБКА] tools\sstrip.exe не найден! & set "MISSING=1" )
if exist "tools\cjpeg-static.exe" ( echo [ОК] cjpeg-static.exe найден! ) else ( echo [ОШИБКА] tools\cjpeg-static.exe не найден! & set "MISSING=1" )
if exist "tools\jpegtran-static.exe" ( echo [ОК] jpegtran-static.exe найден! ) else ( echo [ОШИБКА] tools\jpegtran-static.exe не найден! & set "MISSING=1" )
if exist "tools\djpeg-static.exe" ( echo [ОК] djpeg-static.exe найден! ) else ( echo [ОШИБКА] tools\djpeg-static.exe не найден! & set "MISSING=1" )

if "%MISSING%"=="1" (
echo.
echo ВНИМАНИЕ: Не все .exe файлы найдены в папке tools!
echo Пожалуйста, проверьте наличие файлов и повторите попытку.
pause
exit /b
)

echo.
echo [1/3] Установка необходимых библиотек...
python -m pip install pyinstaller customtkinter pillow moviepy==1.0.3 imageio-ffmpeg

echo.
echo [2/3] Поиск и подготовка FFmpeg...
for /f "delims=" %%i in ('python -c "from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())"') do set "FFMPEG_PATH=%%i"

echo.
echo [3/3] Запуск сборки проекта (режим папки --onedir)...
:: ВАЖНО: Заменен --onefile на --onedir. Это создаст папку dist\NexusStudio_Titan
:: со всеми необходимыми файлами внутри для Inno Setup.
python -m PyInstaller --noconsole --onedir --windowed --name="NexusStudio_Titan" ^
--icon="assets\icon_plus.ico" ^
--collect-all customtkinter ^
--collect-all moviepy ^
--copy-metadata imageio ^
--copy-metadata tqdm ^
--add-binary "%FFMPEG_PATH%;." ^
--add-data "tools\dither.exe;tools" ^
--add-data "tools\floyd-steinberg.exe;tools" ^
--add-data "tools\guetzli.exe;tools" ^
--add-data "tools\sstrip.exe;tools" ^
--add-data "tools\cjpeg-static.exe;tools" ^
--add-data "tools\jpegtran-static.exe;tools" ^
--add-data "tools\djpeg-static.exe;tools" ^
"main.py"

echo.
echo [4/4] Очистка временных файлов...
rmdir /s /q build 2>nul
del /q *.spec 2>nul

echo ========================================================
echo Сборка программы завершена!
echo Теперь откройте setup.iss в Inno Setup и нажмите Compile.
echo ========================================================
pausetools\guetzli.exe не найден! & set "MISSING=1" )
if exist "tools\sstrip.exe" ( echo [ОК] sstrip.exe найден! ) else ( echo [ОШИБКА] tools\sstrip.exe не найден! & set "MISSING=1" )
if exist "tools\cjpeg-static.exe" ( echo [ОК] cjpeg-static.exe найден! ) else ( echo [ОШИБКА] tools\cjpeg-static.exe не найден! & set "MISSING=1" )
if exist "tools\jpegtran-static.exe" ( echo [ОК] jpegtran-static.exe найден! ) else ( echo [ОШИБКА] tools\jpegtran-static.exe не найден! & set "MISSING=1" )
if exist "tools\djpeg-static.exe" ( echo [ОК] djpeg-static.exe найден! ) else ( echo [ОШИБКА] tools\djpeg-static.exe не найден! & set "MISSING=1" )

if "%MISSING%"=="1" (
echo.
echo ВНИМАНИЕ: Не все .exe файлы найдены в папке tools!
echo Пожалуйста, проверьте наличие файлов и повторите попытку.
pause
exit /b
)

echo.
echo [1/3] Установка необходимых библиотек...
python -m pip install pyinstaller customtkinter pillow moviepy==1.0.3 imageio-ffmpeg

echo.
echo [2/3] Поиск и подготовка FFmpeg...
for /f "delims=" %%i in ('python -c "from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())"') do set "FFMPEG_PATH=%%i"

echo.
echo [3/3] Запуск упаковки...
:: ВАЖНО: Изменен путь назначения с ;. на ;tools, чтобы внутри .exe сохранилась папка tools
python -m PyInstaller --noconsole --onefile --windowed --name="NexusStudio_Titan" ^
--collect-all customtkinter ^
--collect-all moviepy ^
--copy-metadata imageio ^
--copy-metadata tqdm ^
--add-binary "%FFMPEG_PATH%;." ^
--add-data "tools\dither.exe;tools" ^
--add-data "tools\floyd-steinberg.exe;tools" ^
--add-data "tools\guetzli.exe;tools" ^
--add-data "tools\sstrip.exe;tools" ^
--add-data "tools\cjpeg-static.exe;tools" ^
--add-data "tools\jpegtran-static.exe;tools" ^
--add-data "tools\djpeg-static.exe;tools" ^
"main.py"

echo.
echo [4/4] Очистка временных файлов...
rmdir /s /q build 2>nul
del /q *.spec 2>nul

echo ========================================================
echo Сборка успешно завершена! Ваш .EXE файл находится в папке dist
echo ========================================================
pause
```eof

```python:main.py
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
    Работает как для разработки (.py), так и для собранного приложения (.exe).
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Автоматически добавляем временную папку сборки в системный PATH приложения.
if hasattr(sys, '_MEIPASS'):
    # Добавляем корень распаковки в PATH
    os.environ["PATH"] += os.pathsep + sys._MEIPASS
    # Добавляем папку tools в PATH (чтобы subprocess.run("dither.exe") работал без путей)
    os.environ["PATH"] += os.pathsep + os.path.join(sys._MEIPASS, "tools")
    
    # ФИКС ДЛЯ АВТОНОМНОСТИ MOVIEPY И FFMPEG:
    # Ищем запакованный exe файл ffmpeg и жестко указываем MoviePy его использовать,
    # иначе на другом ПК он попытается скачать его из интернета и выдаст ошибку.
    ffmpeg_executables = glob.glob(os.path.join(sys._MEIPASS, "*ffmpeg*.exe"))
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
```eof

### Что тебе нужно проверить в остальном коде (очень важно!):

Чтобы программа была на 100% автономной, тебе нужно убедиться, что **везде в твоем коде (внутри папки `gui`, обработчиков и т.д.)**, когда ты открываешь картинку, иконку темы или вызываешь `.exe` утилиту, ты используешь функцию `get_resource_path()`.

**Пример НЕПРАВИЛЬНОГО кода в твоих модулях:**
```python
# Это сломается на другом ПК!
subprocess.run(["tools/dither.exe", "image.png"])
image = customtkinter.CTkImage(Image.open("assets/icon.png"))