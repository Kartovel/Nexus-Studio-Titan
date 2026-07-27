# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from core.constants import THEME
from core.utils import open_folder

class ImageCliToolsMixin:
    """Модуль для работы с внешними CLI-утилитами оптимизации изображений"""

    def _get_tool_path(self, tool_name):
        """
        Ищет утилиту с учетом упаковки через PyInstaller (--add-binary).
        """
        if hasattr(sys, '_MEIPASS'):
            tool_path = os.path.join(sys._MEIPASS, "tools", tool_name)
        else:
            tool_path = os.path.join(os.path.abspath("."), "tools", tool_name)
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


class ImageTasksMixin:
    """Задачи: Изображения"""

    def task_remove_bg(self):
        files = filedialog.askopenfilenames(filetypes=[("Image", "*.jpg *.png *.jpeg *.webp")])
        if not files: return
        out_d = self.get_out_dir("AI_No_Background")
        
        def _rmbg(f):
            try:
                from rembg import remove 
                with open(f, 'rb') as i_file:
                    input_data = i_file.read()
                output_data = remove(input_data)
                out_name = os.path.splitext(os.path.basename(f))[0] + "_nobg.png"
                with open(os.path.join(out_d, out_name), 'wb') as o_file:
                    o_file.write(output_data)
            except ImportError:
                self.log_error("Для удаления фона нужна библиотека! Введи в консоли: pip install rembg")
            except Exception as e:
                self.log_error(f"Ошибка ИИ удаления фона {os.path.basename(f)}: {e}")

        s, t = self.run_parallel(_rmbg, files, "Удаление фона (AI)")
        self.log_info(f"Фон удален: {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_gif_to_png(self):
        files = filedialog.askopenfilenames(filetypes=[("GIF Image", "*.gif")])
        if not files: return
        out_d = self.get_out_dir("GIF_Frames")
        
        def _extract(f):
            name = os.path.splitext(os.path.basename(f))[0]
            target_dir = os.path.join(out_d, name)
            os.makedirs(target_dir, exist_ok=True)
            try:
                with Image.open(f) as img:
                    for i, frame in enumerate(ImageSequence.Iterator(img)):
                        frame = frame.convert("RGBA")
                        frame.save(os.path.join(target_dir, f"frame_{i:04d}.png"), "PNG")
            except Exception as e:
                self.log_error(f"Ошибка извлечения GIF {f}: {e}")

        s, t = self.run_parallel(_extract, files, "Раскадровка GIF")
        self.log_info(f"GIF разобраны на PNG: {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_pixel_art(self):
        files = filedialog.askopenfilenames(filetypes=[("Image", "*.jpg *.png *.jpeg *.webp")])
        if not files: return
        out_d = self.get_out_dir("PixelArt")
        
        val = self.pixel_size.get()
        size = 64
        if "32" in val: size = 32
        elif "128" in val: size = 128
        
        def _pixelate(f):
            try:
                with Image.open(f) as img:
                    is_png = img.format == 'PNG' or f.lower().endswith('.png')
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGBA' if is_png else 'RGB')
                        
                    w, h = img.size
                    ratio = h / w
                    new_w, new_h = size, int(size * ratio)
                    
                    small_img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                    result_img = small_img.resize((w, h), Image.Resampling.NEAREST)
                    
                    if "Ретро" in val:
                        result_img = result_img.quantize(colors=32).convert('RGB' if not is_png else 'RGBA')

                    out_path = os.path.join(out_d, os.path.basename(f))
                    if is_png:
                        result_img.save(out_path, "PNG")
                    else:
                        result_img.convert('RGB').save(out_path, "JPEG", quality=90)
            except Exception as e:
                pass 

        s, t = self.run_parallel(_pixelate, files, "PixelArt Generator")
        self.log_info(f"Стилизовано под пиксель-арт: {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_image_resize(self):
        files = filedialog.askopenfilenames(filetypes=[("Image", "*.jpg *.png *.jpeg *.webp")])
        if not files: return
        out_d = self.get_out_dir("Resized")
        mode = self.resize_mode.get()
        
        def _res(f):
            try:
                with Image.open(f) as img:
                    w, h = img.size
                    new_s = (w, h)
                    val = mode.lower().replace(" ", "")
                    
                    if "%" in val:
                        match = re.search(r'(\d+(?:\.\d+)?)%', val)
                        if match:
                            pct = float(match.group(1)) / 100.0
                            new_s = (max(1, int(w * pct)), max(1, int(h * pct)))
                            
                    elif "ширина:" in val or "width:" in val:
                        match = re.search(r'(\d+)', val)
                        if match:
                            target_w = int(match.group(1))
                            ratio = target_w / float(w)
                            new_s = (max(1, target_w), max(1, int(h * ratio)))
                            
                    elif "x" in val or "х" in val: 
                        val = val.replace("х", "x")
                        parts = val.split("x")
                        if len(parts) >= 2:
                            match_w = re.search(r'(\d+)', parts[0])
                            match_h = re.search(r'(\d+)', parts[1])
                            if match_w and match_h:
                                new_s = (max(1, int(match_w.group(1))), max(1, int(match_h.group(1))))

                    if new_s != (w, h):
                        save_ext = os.path.splitext(f)[1].lower()
                        if save_ext in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        img.resize(new_s, Image.Resampling.LANCZOS).save(os.path.join(out_d, os.path.basename(f)))
                    else:
                        img.save(os.path.join(out_d, os.path.basename(f)))
            except Exception as e:
                self.log_error(f"Ошибка ресайза {f}: {e}")

        s, t = self.run_parallel(_res, files, "Ресайз")
        self.log_info(f"Размер изменен: {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_generate_ico(self):
        files = filedialog.askopenfilenames(filetypes=[("Image", "*.jpg *.png *.jpeg")])
        if not files: return
        out_d = self.get_out_dir("Icons")
        def _ico(f):
            name = os.path.splitext(os.path.basename(f))[0]
            with Image.open(f) as img:
                img.save(os.path.join(out_d, f"{name}.ico"), format="ICO", sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
        s, t = self.run_parallel(_ico, files, "ICO Gen")
        self.log_info(f"Иконки созданы: {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_convert_images(self):
        files = filedialog.askopenfilenames()
        if not files: return
        fmt = self.img_fmt.get().lower(); out_d = self.get_out_dir(f"Conv_{fmt.upper()}"); q = int(self.img_q.get())
        def _c(data):
            in_p, out_p = data
            with Image.open(in_p) as img:
                if img.mode != "RGB" and fmt in ('jpeg', 'jpg'): img = img.convert("RGB")
                img.save(out_p, format=fmt.upper() if fmt != 'jpg' else 'JPEG', quality=q)
        
        tasks = [(f, os.path.join(out_d, f"{os.path.splitext(os.path.basename(f))[0]}.{fmt}")) for f in files]
        s, t = self.run_parallel(_c, tasks, "Конвертация")
        self.log_info(f"Конвертировано {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_watermark(self):
        files = filedialog.askopenfilenames()
        if not files: return
        txt = self.wm_text.get(); out_d = self.get_out_dir("Watermark"); pos = self.wm_pos.get()
        if not txt: return self.log_error("Укажите текст!")
        
        def _wm(fp):
            with Image.open(fp).convert("RGBA") as base:
                txt_img = Image.new("RGBA", base.size, (255,255,255,0))
                draw = ImageDraw.Draw(txt_img)
                f_size = max(20, int(base.width / 20))
                try: font = ImageFont.truetype("arial.ttf", f_size)
                except: font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), txt, font=font)
                tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
                y = base.height - th - 20 if "Низ" in pos else (base.height - th) // 2
                x = base.width - tw - 20 if "Право" in pos else (base.width - tw) // 2
                draw.text((x+2, y+2), txt, font=font, fill=(0,0,0,180))
                draw.text((x, y), txt, font=font, fill=(255,255,255,200))
                name = os.path.splitext(os.path.basename(fp))[0]
                Image.alpha_composite(base, txt_img).convert("RGB").save(os.path.join(out_d, f"{name}.jpg"), "JPEG")
        
        s, t = self.run_parallel(_wm, files, "Watermark")
        self.log_info(f"Защищено {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_compress_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Img", "*.jpg *.jpeg *.png *.webp")])
        if not files: return
        out_d = self.get_out_dir("Optimized_PRO")
        mode = self.opt_mode.get()
        
        engine = getattr(self, 'opt_engine', None)
        engine_val = engine.get() if engine else "PIL (Встроенный)"

        # Получаем выбранный формат
        fmt_ui = getattr(self, 'opt_out_fmt', None)
        out_fmt_val = fmt_ui.get() if fmt_ui else "Формат: Оригинал"
        
        def _cmp(f):
            try:
                name = os.path.splitext(os.path.basename(f))[0]
                with Image.open(f) as img:
                    is_png = img.format == 'PNG' or f.lower().endswith('.png')
                    
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGBA' if is_png else 'RGB')
                        
                    clean = Image.new(img.mode, img.size)
                    clean.putdata(list(img.getdata()))

                    # Определяем целевой формат
                    target_fmt = "ORIGINAL"
                    if "WEBP" in out_fmt_val: target_fmt = "WEBP"
                    elif "JPEG" in out_fmt_val: target_fmt = "JPEG"
                    elif "PNG" in out_fmt_val: target_fmt = "PNG"
                    
                    if "Квантизация" in mode:
                        if clean.mode != 'RGB': clean = clean.convert('RGB')
                        quantized = clean.convert('P', palette=Image.ADAPTIVE, colors=256, dither=Image.FLOYDSTEINBERG)
                        
                        if target_fmt == "WEBP":
                            quantized.convert("RGBA").save(os.path.join(out_d, f"{name}.webp"), "WEBP", quality=100, method=6)
                        else:
                            quantized.save(os.path.join(out_d, f"{name}.png"), "PNG", optimize=True)
                        return
                    
                    if "Guetzli" in engine_val:
                        if target_fmt not in ["ORIGINAL", "JPEG"]:
                            self.log_error(f"Guetzli жмет только в JPEG. Игнорируем формат {target_fmt} для {name}.")
                        clean = clean.convert('RGB')
                        temp_png = os.path.join(out_d, f"temp_guetzli_{name}.png")
                        clean.save(temp_png, "PNG")
                        out_jpg = os.path.join(out_d, f"{name}_guetzli.jpg")
                        try:
                            tool_path = self._get_tool_path("guetzli.exe")
                            import subprocess
                            cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
                            subprocess.run([tool_path, "--quality", "85", temp_png, out_jpg], check=True, creationflags=cflags)
                        except FileNotFoundError:
                            self.log_error(f"Guetzli не найден для {name}! Скачайте guetzli.exe.")
                        except Exception as e:
                            self.log_error(f"Сбой Guetzli для {name}: {e}")
                        finally:
                            if os.path.exists(temp_png): os.remove(temp_png)
                        return

                    if "MozJPEG" in engine_val:
                        if target_fmt not in ["ORIGINAL", "JPEG"]:
                            self.log_error(f"MozJPEG жмет только в JPEG. Игнорируем формат {target_fmt} для {name}.")
                        clean = clean.convert('RGB')
                        temp_bmp = os.path.join(out_d, f"temp_moz_{name}.bmp")
                        clean.save(temp_bmp, "BMP")
                        out_jpg = os.path.join(out_d, f"{name}_moz.jpg")
                        try:
                            tool_path = self._get_tool_path("cjpeg-static.exe")
                            import subprocess
                            cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
                            subprocess.run([tool_path, "-outfile", out_jpg, "-optimize", "-quality", "85", "-sample", "2x2", temp_bmp], check=True, creationflags=cflags)
                        except FileNotFoundError:
                            self.log_error(f"MozJPEG (cjpeg-static.exe) не найден для {name}!")
                        except Exception as e:
                            self.log_error(f"Сбой MozJPEG для {name}: {e}")
                        finally:
                            if os.path.exists(temp_bmp): os.remove(temp_bmp)
                        return

                    # Стандартный PIL (Встроенный)
                    q = 80
                    if "Мягкая" in mode: q = 95
                    elif "Агрессивная" in mode: q = 45
                    
                    final_ext = os.path.splitext(f)[1].lower()
                    save_fmt = None
                    
                    # Логика назначения форматов
                    if target_fmt == "WEBP":
                        final_ext = ".webp"
                        save_fmt = "WEBP"
                    elif target_fmt == "JPEG":
                        final_ext = ".jpg"
                        save_fmt = "JPEG"
                    elif target_fmt == "PNG":
                        final_ext = ".png"
                        save_fmt = "PNG"
                    else: # ORIGINAL (Автомат)
                        if is_png or clean.mode in ('RGBA', 'LA', 'P'):
                            save_fmt = "PNG"
                            final_ext = ".png" if not final_ext.endswith('.png') else final_ext
                        else:
                            save_fmt = "JPEG"
                            final_ext = ".jpg" if not final_ext.endswith(('.jpg', '.jpeg')) else final_ext

                    out_path = os.path.join(out_d, f"{name}{final_ext}")
                    
                    # Сохранение с учетом формата
                    if save_fmt == "PNG":
                        clean.save(out_path, "PNG", optimize=True)
                    elif save_fmt == "WEBP":
                        if clean.mode not in ('RGB', 'RGBA'): clean = clean.convert('RGBA')
                        clean.save(out_path, "WEBP", quality=q, method=6) # method=6 дает макс. сжатие WEBP
                    else: # JPEG
                        # Для JPEG обязательно убираем альфа-канал, иначе будет краш
                        if clean.mode not in ('RGB', 'L'): clean = clean.convert('RGB')
                        clean.save(out_path, "JPEG", quality=q, optimize=True, subsampling=1)
            except Exception as e:
                self.log_error(f"Системная ошибка файла {f}: {e}")

        s, t = self.run_parallel(_cmp, files, "Оптимизация PRO")
        self.log_info(f"Оптимизировано {s}/{t}")
        if s > 0: open_folder(out_d)

    def task_monochrome(self):
        files = filedialog.askopenfilenames(filetypes=[("Image", "*.jpg *.png *.jpeg *.webp")])
        if not files: return
        
        # Создаем папку для готовых Ч/Б изображений
        out_d = self.get_out_dir("Monochrome")
        
        def _mono(f):
            try:
                with Image.open(f) as img:
                    # Конвертируем в режим L (оттенки серого)
                    mono_img = img.convert('L')
                    
                    name = os.path.basename(f)
                    out_path = os.path.join(out_d, name)
                    ext = os.path.splitext(name)[1].lower()
                    
                    # Сохраняем с сохранением исходного формата
                    if ext in ['.jpg', '.jpeg']:
                        mono_img.save(out_path, "JPEG", quality=95)
                    elif ext == '.png':
                        mono_img.save(out_path, "PNG")
                    elif ext == '.webp':
                        mono_img.save(out_path, "WEBP", quality=95)
                    else:
                        mono_img.save(out_path)
            except Exception as e:
                self.log_error(f"Ошибка перевода в Ч/Б {f}: {e}")

        s, t = self.run_parallel(_mono, files, "Ч/Б Фильтр")
        self.log_info(f"Переведено в монохром: {s}/{t}")
        if s > 0: open_folder(out_d)