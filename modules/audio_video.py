# -*- coding: utf-8 -*-
import os
import subprocess
from tkinter import filedialog
from core.constants import THEME
from core.utils import open_folder, sanitize_filename
from moviepy.editor import AudioFileClip, VideoFileClip, afx
import moviepy.video.fx.all as vfx

class AudioVideoTasksMixin:
    """Задачи: Видео и Аудио"""

    # --- ЗАДАЧА 1: АУДИО ОПТИМИЗАТОР PRO ---
    def task_optimize_audio(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.wav *.mp3 *.ogg *.flac *.m4a")])
        if not files: return
        out_d = self.get_out_dir("Audio_Optimized")
        
        # Получаем значения из UI (добавлено в ui_builder.py)
        fmt = self.opt_aud_fmt.get() 
        aud_type = self.opt_aud_type.get() 
        
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ff = get_ffmpeg_exe()
        except ImportError:
            self.log_error("Критическая ошибка: FFmpeg не найден (установите imageio_ffmpeg).")
            return
            
        cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0

        def _optimize(f):
            name = os.path.splitext(os.path.basename(f))[0]
            
            # Психоакустическая модель среза частот (LPF)
            # Голос не требует ничего выше 16кГц, а эмбиент можно резать даже на 14кГц
            lpf = "16000" if "Голос" in aud_type else "14000"
            
            if "Opus" in fmt:
                ext = ".opus"
                br = "64k" if "Голос" in aud_type else "48k"
                args = ["-c:a", "libopus", "-b:a", br, "-vbr", "on", "-compression_level", "10", "-af", f"lowpass=f={lpf}"]
            elif "MP3" in fmt:
                ext = ".mp3"
                q = "4" if "Голос" in aud_type else "6"
                args = ["-c:a", "libmp3lame", "-q:a", q, "-joint_stereo", "1", "-af", f"lowpass=f={lpf}"]
            else: # OGG
                ext = ".ogg"
                q = "3" if "Голос" in aud_type else "1"
                args = ["-c:a", "libvorbis", "-q:a", q, "-af", f"lowpass=f={lpf}"]
            
            out_path = os.path.join(out_d, f"{name}_opt{ext}")
            cmd = [ff, "-y", "-i", f] + args + [out_path]
            
            try:
                subprocess.run(cmd, check=True, creationflags=cflags, capture_output=True)
            except subprocess.CalledProcessError as err:
                if self.config.get("ffmpeg_log"):
                    self.log_error(f"FFmpeg Ошибка ({name}): {err.stderr.decode('utf-8', 'ignore')}")
                raise err

        s, t = self.run_parallel(_optimize, files, "Аудио Оптимизация")
        self.log_info(f"Оптимизировано аудио: {s}/{t}")
        if s > 0 and self.config.get("auto_open"): open_folder(out_d)

    # --- ИИ ТРАНСКРИБАЦИЯ (Нейросеть Whisper) ---
    def task_transcribe_audio(self):
        files = filedialog.askopenfilenames(filetypes=[("Media", "*.mp3 *.wav *.mp4 *.mkv *.avi")])
        if not files: return
        out_d = self.get_out_dir("AI_Transcripts")
        
        def _transcribe(f):
            try:
                import whisper
                model = whisper.load_model("base") # Автоматически скачает легкую и быструю модель
                result = model.transcribe(f)
                out_name = os.path.splitext(os.path.basename(f))[0] + ".txt"
                with open(os.path.join(out_d, out_name), "w", encoding="utf-8") as txt:
                    txt.write(result["text"])
            except ImportError:
                self.log_error("Для распознавания текста нужен Whisper! Введи в консоли: pip install openai-whisper")
            except Exception as e:
                self.log_error(f"Ошибка ИИ транскрибации {os.path.basename(f)}: {e}")
                
        s, t = self.run_parallel(_transcribe, files, "Whisper AI Транскрибация")
        self.log_info(f"Текст распознан: {s}/{t}")
        if s > 0 and self.config.get("auto_open"): open_folder(out_d)

    def task_media_speed(self):
        f_path = filedialog.askopenfilename(filetypes=[("Media", "*.mp4 *.avi *.mkv *.mp3 *.wav *.ogg")])
        if not f_path: return
        out_d = self.get_out_dir("Speed_Mods")
        val = self.speed_factor.get()
        factor = 0.5 if "0.5" in val else 1.5 if "1.5" in val else 2.0
        
        is_audio = f_path.lower().endswith(('.mp3', '.wav', '.ogg'))
        name, ext = os.path.splitext(os.path.basename(f_path))
        out_p = os.path.join(out_d, f"{name}_{factor}x{ext}")
        
        self.set_progress(0.5, "Рендер медиа...")
        clip, new_clip = None, None
        try:
            if is_audio:
                clip = AudioFileClip(f_path)
                new_clip = clip.fx(vfx.speedx, factor)
                new_clip.write_audiofile(out_p, logger=None)
            else:
                clip = VideoFileClip(f_path)
                new_clip = clip.fx(vfx.speedx, factor)
                self.render_video_with_fallback(new_clip, out_p, audio=True)
                
            self.log_info("Скорость изменена!")
            if self.config.get("auto_open"): open_folder(out_d)
        except Exception as e: 
            self.log_error(str(e))
        finally:
            if new_clip: new_clip.close()
            if clip: clip.close()

    def task_video_to_gif(self):
        f_path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.webm")])
        if not f_path: return
        out_d = self.get_out_dir("Video2GIF")
        fps = int(self.gif_fps.get())
        res_map = {"1080p": 1080, "720p": 720, "480p": 480}
        target_h = res_map.get(self.gif_res.get(), None)
        out_path = os.path.join(out_d, f"{sanitize_filename(os.path.splitext(os.path.basename(f_path))[0])}.gif")
        
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ff = get_ffmpeg_exe()
            sc = f",scale=-2:{target_h}:flags=lanczos" if target_h else ""
            tmp = os.path.join(out_d, "pal.png")
            cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
            
            hw_args = []
            if self.config.get("hwaccel_decode") and "GPU" in self.config.get("processing_mode", ""):
                if "NVIDIA" in self.config.get("processing_mode"): hw_args = ["-hwaccel", "cuda"]
                elif "Intel" in self.config.get("processing_mode"): hw_args = ["-hwaccel", "qsv"]
            
            def run_cmd(args, desc):
                try: 
                    subprocess.run(args, check=True, creationflags=cflags, capture_output=True)
                    return True
                except subprocess.CalledProcessError as err:
                    if self.config.get("ffmpeg_log"): self.log_error(err.stderr.decode('utf-8', 'ignore'))
                    return False

            self.set_progress(0.3, "Генерация палитры...")
            cmd_pal = [ff, "-y"] + hw_args + ["-i", f_path, "-vf", f"fps={fps}{sc},palettegen", tmp]
            if not run_cmd(cmd_pal, "Palette"):
                self.log_info("Отключение HWAccel (Fallback)...", THEME["warning"])
                run_cmd([ff, "-y", "-i", f_path, "-vf", f"fps={fps}{sc},palettegen", tmp], "Palette CPU")

            self.set_progress(0.7, "Рендер GIF...")
            cmd_gif = [ff, "-y"] + hw_args + ["-i", f_path, "-i", tmp, "-filter_complex", f"fps={fps}{sc}[x];[x][1:v]paletteuse", out_path]
            if not run_cmd(cmd_gif, "Render"):
                run_cmd([ff, "-y", "-i", f_path, "-i", tmp, "-filter_complex", f"fps={fps}{sc}[x];[x][1:v]paletteuse", out_path], "Render CPU")

            if os.path.exists(tmp): os.remove(tmp)
            self.log_info("GIF создан!"); open_folder(out_d)
        except Exception as e: self.log_error(f"FFmpeg ошибка: {e}")

    def task_batch_extract_audio(self):
        folder = filedialog.askdirectory()
        if not folder: return
        out_d = self.get_out_dir("Audio_Extract"); fmt = self.aud_fmt.get().lower(); br = self.aud_bit.get()
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.mp4','.mkv','.avi'))]
        
        def _ex(vp):
            c = None
            try:
                c = VideoFileClip(vp)
                if c.audio: c.audio.write_audiofile(os.path.join(out_d, f"{os.path.splitext(os.path.basename(vp))[0]}.{fmt}"), bitrate=br, logger=None)
            finally:
                if c: c.close()
                
        s, t = self.run_parallel(_ex, files, f"Extract"); self.log_info(f"Извлечено: {s}/{t}"); open_folder(out_d)

    def task_normalize_audio(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav *.ogg")])
        if not files: return
        out_d = self.get_out_dir("Normalized")
        def _n(f):
            c, nc = None, None
            try:
                c = AudioFileClip(f); nc = c.fx(afx.audio_normalize)
                nc.write_audiofile(os.path.join(out_d, os.path.basename(f)), logger=None)
            finally:
                if c: c.close()
                if nc: nc.close()
                
        s, t = self.run_parallel(_n, files, "Нормализация"); self.log_info(f"Готово: {s}/{t}"); open_folder(out_d)