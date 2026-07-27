# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from core.constants import THEME

class ImageCliToolsMixin:
    """Модуль для работы с внешними CLI-утилитами оптимизации изображений"""

    def _get_tool_path(self, tool_name):
        """
        Ищет утилиту с учетом упаковки через PyInstaller (--add-binary).
        """
        if hasattr(sys, '_MEIPASS'):
            # ИСПРАВЛЕНИЕ: Так как в обновленном build_titan.bat мы пакуем утилиты 
            # с флагом "--add-binary tools\*;tools", внутри архива они лежат в папке tools
            tool_path = os.path.join(sys._MEIPASS, "tools", tool_name)
        else:
            # Для режима разработки ищем в папке tools
            tool_path = os.path.join(os.path.abspath("."), "tools", tool_name)
            
            # На случай, если скрипт запущен из другой директории
            if not os.path.exists(tool_path):
                tool_path = os.path.join(os.path.abspath("."), tool_name)

        if not os.path.exists(tool_path):
            raise FileNotFoundError(f"Утилита {tool_name} не найдена по пути {tool_path}")
        
        return tool_path

    def _run_cli_tool(self, cmd, tool_name):
        """Базовый метод для запуска процессов без блокировки основного UI"""
        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode('utf-8', errors='ignore').strip()
            self.log_error(f"Сбой {tool_name}: {err_msg}")
            return False
        except Exception as e:
            self.log_error(f"Системная ошибка {tool_name}: {str(e)}")
            return False

    def optimize_guetzli(self, input_path, output_path, quality=90):
        tool = self._get_tool_path("guetzli.exe")
        cmd = [tool, "--quality", str(quality), input_path, output_path]
        return self._run_cli_tool(cmd, "Guetzli")

    def process_mozjpeg(self, input_path, output_path, quality=85):
        djpeg = self._get_tool_path("djpeg-static.exe")
        cjpeg = self._get_tool_path("cjpeg-static.exe")
        temp_bmp = input_path + ".bmp"
        
        if not self._run_cli_tool([djpeg, "-bmp", "-outfile", temp_bmp, input_path], "djpeg"):
            return False
            
        success = self._run_cli_tool([cjpeg, "-quality", str(quality), "-optimize", "-outfile", output_path, temp_bmp], "cjpeg")
        
        if os.path.exists(temp_bmp):
            os.remove(temp_bmp)
        return success

    def optimize_jpegtran(self, input_path, output_path):
        tool = self._get_tool_path("jpegtran-static.exe")
        cmd = [tool, "-optimize", "-copy", "none", "-outfile", output_path, input_path]
        return self._run_cli_tool(cmd, "JPEGTran")

    def apply_floyd_steinberg(self, input_path, output_path):
        tool = self._get_tool_path("floyd-steinberg.exe")
        cmd = [tool, input_path, output_path]
        return self._run_cli_tool(cmd, "Floyd-Steinberg")
        
    def run_sstrip(self, input_file):
        tool = self._get_tool_path("sstrip.exe")
        cmd = [tool, input_file]
        return self._run_cli_tool(cmd, "sstrip")