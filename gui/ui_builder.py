# -*- coding: utf-8 -*-
import customtkinter as ctk
from gui.components import ModernCard
from core.constants import THEME
from core.utils import open_folder

class UIBuilderMixin:
    """Обособленный строитель интерфейса, подключаемый как примесь к основному окну"""

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=THEME["sidebar"], border_width=1, border_color="#1F1F28")
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        logo_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_container.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")
        ctk.CTkLabel(logo_container, text="NEXUS", font=ctk.CTkFont(size=32, weight="bold", family="Impact"), text_color=THEME["accent"]).pack(side="left")
        ctk.CTkLabel(logo_container, text="TITAN", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=5, pady=(8,0))
        ctk.CTkLabel(logo_container, text="v6.3", font=ctk.CTkFont(size=12), text_color=THEME["warning"]).pack(side="left", pady=(12,0))

        prof_frame = ctk.CTkFrame(self.sidebar, fg_color="#1B1B24", corner_radius=10)
        prof_frame.grid(row=1, column=0, padx=15, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(prof_frame, text="⚡ Системный статус:", font=ctk.CTkFont(size=11), text_color=THEME["text_muted"]).pack(anchor="w", padx=15, pady=(10, 0))
        
        mode_text = self.config.get("processing_mode")
        status_color = THEME["info"] if "GPU" in mode_text else THEME["success"]
        ctk.CTkLabel(prof_frame, text=f"Готов ({mode_text})", font=ctk.CTkFont(size=14, weight="bold"), text_color=status_color).pack(anchor="w", padx=15, pady=(0, 10))

        self.nav_btns = {}
        nav_items = [
            ("home", "📊 Главная панель"),
            ("modding", "👾 Моддинг & Source"), 
            ("audio", "🎵 Видео & Аудио"),
            ("images", "🖼️ Изображения"),
            ("scripts", "📄 Текст & Скрипты"),
            ("utils", "🛠️ Файлы & Утилиты")
        ]
        
        for i, (key, text) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", 
                                text_color=THEME["text_muted"], hover_color=THEME["card_bg"],
                                anchor="w", font=ctk.CTkFont(size=15, weight="bold"), height=45,
                                command=lambda k=key: self.select_frame(k))
            btn.grid(row=i, column=0, padx=15, pady=3, sticky="ew")
            self.nav_btns[key] = btn

        ctk.CTkButton(self.sidebar, text="⚙️ Настройки Системы", fg_color=THEME["card_bg"], hover_color="#2A2A35",
                      text_color=THEME["text_main"], font=ctk.CTkFont(weight="bold"), height=50,
                      command=self.open_settings).grid(row=11, column=0, padx=15, pady=20, sticky="ew")

    def _build_main_area(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        self.frames["home"] = self._create_home_frame()
        self.frames["modding"] = self._create_modding_frame()
        self.frames["audio"] = self._create_audio_frame()
        self.frames["images"] = self._create_images_frame()
        self.frames["scripts"] = self._create_scripts_frame()
        self.frames["utils"] = self._create_utils_frame()

    def _build_footer(self):
        self.footer = ctk.CTkFrame(self, height=220, corner_radius=0, fg_color=THEME["sidebar"], border_width=1, border_color="#1F1F28")
        self.footer.grid(row=1, column=1, sticky="nsew")
        
        status_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        status_frame.pack(fill="x", padx=25, pady=(15, 5))
        
        self.status_lbl = ctk.CTkLabel(status_frame, text="Ожидание задач...", font=ctk.CTkFont(weight="bold", size=14))
        self.status_lbl.pack(side="left")
        
        self.cancel_btn = ctk.CTkButton(status_frame, text="⏹ Отменить процесс", fg_color=THEME["danger"], width=130, height=28, state="disabled", command=self._cancel_task)
        self.cancel_btn.pack(side="right", padx=(10, 0))
        
        self.progress_pct = ctk.CTkLabel(status_frame, text="0%", font=ctk.CTkFont(weight="bold", size=16), text_color=THEME["accent"])
        self.progress_pct.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self.footer, mode="determinate", height=12, progress_color=THEME["accent"])
        self.progress_bar.pack(fill="x", padx=25, pady=(0, 10))
        self.progress_bar.set(0)

        self.log_box = ctk.CTkTextbox(self.footer, height=120, state="disabled", 
                                      fg_color="#0A0A0E", text_color="#00FF00", font=("Consolas", 13), border_width=1, border_color="#1F1F28")
        self.log_box.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    def select_frame(self, name):
        for key, btn in self.nav_btns.items():
            btn.configure(fg_color="transparent", text_color=THEME["text_muted"])
        if name in self.nav_btns:
            self.nav_btns[name].configure(fg_color=THEME["accent"], text_color=THEME["text_main"])
            
        if self.current_frame: self.current_frame.grid_forget()
        self.current_frame = self.frames[name]
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _create_home_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Nexus Titan v6.3", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=(40, 5), anchor="w", padx=30)
        ctk.CTkLabel(frame, text="Добро пожаловать в рабочую среду.", text_color=THEME["text_muted"], font=ctk.CTkFont(size=16)).pack(anchor="w", padx=30, pady=(0, 30))
        
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=25)
        info_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        def create_stat(parent, col, num, text, color):
            f = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], corner_radius=15, border_width=1, border_color="#2E2E3A")
            f.grid(row=0, column=col, padx=8, sticky="nsew")
            ctk.CTkLabel(f, text=num, font=ctk.CTkFont(size=42, weight="bold"), text_color=color).pack(pady=(25, 0))
            ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME["text_muted"]).pack(pady=(0, 25))

        create_stat(info_frame, 0, "27+", "Мощных Утилит", THEME["accent"])
        create_stat(info_frame, 1, f"x{self.get_active_workers()}", "Потоков Активно", THEME["warning"])
        create_stat(info_frame, 2, "PRO", "Smart Engine", THEME["success"])
        create_stat(info_frame, 3, "V6.3", "Refactored Edition", THEME["info"])
        
        act_frame = ctk.CTkFrame(frame, fg_color="transparent")
        act_frame.pack(fill="x", padx=25, pady=40)
        
        ctk.CTkButton(act_frame, text="📁 Открыть Рабочую Папку (Output)", height=60, fg_color=THEME["accent"], 
                      font=ctk.CTkFont(size=16, weight="bold"), command=lambda: open_folder(self.get_out_dir())).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(act_frame, text="🗑️ Очистить Output", height=60, fg_color=THEME["danger"], 
                      font=ctk.CTkFont(size=16, weight="bold"), command=self.clear_results).pack(side="right", expand=True, fill="x", padx=(10, 0))
        
        return frame

    def _create_modding_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Моддинг (Source Engine)", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(25, 15), anchor="w", padx=30)

        card1 = ModernCard(frame, "Аудио Оптимизатор (Source)", "🔊", "Сжатие звуков строго под стандарты движка (Garry's Mod, CS:S).")
        row1 = ctk.CTkFrame(card1.content, fg_color="transparent"); row1.pack(fill="x")
        self.gmod_hz = ctk.CTkOptionMenu(row1, values=["44100", "22050", "11025"], width=100); self.gmod_hz.pack(side="left", padx=5)
        self.gmod_ch = ctk.CTkOptionMenu(row1, values=["Моно", "Стерео"], width=100); self.gmod_ch.pack(side="left", padx=5)
        ctk.CTkButton(row1, text="Оптимизировать WAV", command=lambda: self.start_task(self.task_gmod_wav), fg_color=THEME["success"]).pack(side="right")

        card2 = ModernCard(frame, "DDS Конвертер (Текстуры)", "👾", "Массовое извлечение игровых .dds текстур в PNG формат.")
        ctk.CTkButton(card2.content, text="Выбрать DDS и извлечь", command=lambda: self.start_task(self.task_dds_to_png), fg_color="#8E44AD").pack(fill="x")

        card3 = ModernCard(frame, "Умный фикс кодировки (Lua/TXT)", "     🛠️", "Лечит скрипты от кракозябр, переводит в UTF-8 (Unix переносы).")
        ctk.CTkButton(card3.content, text="Вылечить скрипты в папке", command=lambda: self.start_task(self.task_gmod_lua_fix), fg_color=THEME["warning"], text_color="#000").pack(fill="x")

        card4 = ModernCard(frame, "Генератор Материалов (.VMT)", "🧱", "Создает базовые .vmt файлы для текстур Source Engine.", accent_color=THEME["info"])
        row4 = ctk.CTkFrame(card4.content, fg_color="transparent"); row4.pack(fill="x")
        ctk.CTkLabel(row4, text="Шейдер:").pack(side="left")
        self.vmt_shader = ctk.CTkOptionMenu(row4, values=["LightmappedGeneric", "VertexLitGeneric", "UnlitGeneric"]); self.vmt_shader.pack(side="left", padx=10)
        ctk.CTkLabel(row4, text="Базовый путь:").pack(side="left")
        self.vmt_path = ctk.CTkEntry(row4, width=150, placeholder_text="models/myprops/"); self.vmt_path.pack(side="left", padx=5)
        ctk.CTkButton(row4, text="Генерировать для папки", command=lambda: self.start_task(self.task_vmt_gen), fg_color=THEME["info"], text_color="#000").pack(side="right")

        return frame

    def _create_audio_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Видео & Аудио", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(25, 15), anchor="w", padx=30)

        card_opt = ModernCard(frame, "Аудио Оптимизатор PRO", "     🎛️", "Экстремальное сжатие аудио: VBR, Opus, Low-Pass фильтры.", accent_color="#3498DB")
        row_opt = ctk.CTkFrame(card_opt.content, fg_color="transparent"); row_opt.pack(fill="x")
        self.opt_aud_fmt = ctk.CTkOptionMenu(row_opt, values=["Opus (Игры)", "MP3 (VBR)", "OGG (VBR)"], width=130)
        self.opt_aud_fmt.pack(side="left", padx=5)
        self.opt_aud_type = ctk.CTkOptionMenu(row_opt, values=["Голос / Диалоги", "Эмбиент / Шумы"], width=150)
        self.opt_aud_type.pack(side="left", padx=5)
        ctk.CTkButton(row_opt, text="Оптимизировать", command=lambda: self.start_task(self.task_optimize_audio), fg_color="#3498DB").pack(side="right")

        card_ai_aud = ModernCard(frame, "ИИ Распознавание Речи (Whisper)", "🤖", "Транскрибация аудио и видео в текстовый файл с помощью нейросети.", accent_color="#9B59B6")
        ctk.CTkButton(card_ai_aud.content, text="Распознать текст", command=lambda: self.start_task(self.task_transcribe_audio), fg_color="#9B59B6").pack(fill="x")

        card1 = ModernCard(frame, "Умный конвертер Video -> GIF", "     🎞️", "Рендер через FFmpeg палитры для лучшего качества (Поддерживает HWAccel).")
        row1 = ctk.CTkFrame(card1.content, fg_color="transparent"); row1.pack(fill="x")
        self.gif_fps = ctk.CTkOptionMenu(row1, values=["15", "24", "30", "10"], width=70); self.gif_fps.pack(side="left", padx=5)
        self.gif_res = ctk.CTkOptionMenu(row1, values=["480p", "720p", "1080p", "Оригинал"], width=90); self.gif_res.pack(side="left", padx=5)
        ctk.CTkButton(row1, text="Создать GIF", command=lambda: self.start_task(self.task_video_to_gif), fg_color=THEME["accent"]).pack(side="right")

        card2 = ModernCard(frame, "Извлечение Аудио", "🎵", "Достает звук из папки с видео.")
        row2 = ctk.CTkFrame(card2.content, fg_color="transparent"); row2.pack(fill="x")
        self.aud_fmt = ctk.CTkOptionMenu(row2, values=["MP3", "WAV", "OGG"], width=90); self.aud_fmt.pack(side="left", padx=5)
        self.aud_bit = ctk.CTkOptionMenu(row2, values=["192k", "320k", "128k"], width=90); self.aud_bit.pack(side="left", padx=5)
        ctk.CTkButton(row2, text="Извлечь из папки", command=lambda: self.start_task(self.task_batch_extract_audio), fg_color=THEME["warning"], text_color="#000").pack(side="right")

        card3 = ModernCard(frame, "Нормализатор Аудио", "🔊", "Массово выравнивает громкость аудиофайлов.")
        ctk.CTkButton(card3.content, text="Нормализовать папку", command=lambda: self.start_task(self.task_normalize_audio), fg_color=THEME["info"], text_color="#000").pack(fill="x")

        card4 = ModernCard(frame, "Изменение скорости Видео/Аудио", "⏩", "Динамический GPU/CPU рендер для ускорения или замедления медиа.", accent_color="#E67E22")
        row4 = ctk.CTkFrame(card4.content, fg_color="transparent"); row4.pack(fill="x")
        ctk.CTkLabel(row4, text="Множитель:").pack(side="left")
        self.speed_factor = ctk.CTkOptionMenu(row4, values=["0.5x (Замедлить)", "1.5x (Быстро)", "2.0x (Очень быстро)"], width=150)
        self.speed_factor.pack(side="left", padx=10)
        ctk.CTkButton(row4, text="Применить", command=lambda: self.start_task(self.task_media_speed), fg_color="#E67E22").pack(side="right")

        return frame

    def _create_images_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Изображения", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(25, 15), anchor="w", padx=30)

        card_ai = ModernCard(frame, "ИИ Удаление Фона", "✨", "Нейросетевое удаление фона с изображений (требуется библиотека rembg).", accent_color="#2ECC71")
        ctk.CTkButton(card_ai.content, text="Удалить фон", command=lambda: self.start_task(self.task_remove_bg), fg_color="#2ECC71", text_color="#000").pack(fill="x")

        card_gif = ModernCard(frame, "Раскадровщик GIF", "     🎞️", "Извлекает все кадры из GIF и сохраняет их как отдельные PNG.", accent_color="#E74C3C")
        ctk.CTkButton(card_gif.content, text="Разобрать GIF", command=lambda: self.start_task(self.task_gif_to_png), fg_color="#E74C3C").pack(fill="x")

        card_pixel = ModernCard(frame, "PixelArt Конвертер (Bonus)", "     🕹️", "Превращает любые фото и картинки в стильный ретро пиксель-арт (8-bit).", accent_color="#9B59B6")
        row_pixel = ctk.CTkFrame(card_pixel.content, fg_color="transparent"); row_pixel.pack(fill="x")
        self.pixel_size = ctk.CTkOptionMenu(row_pixel, values=["Хардкор (32x32 Ретро)", "Средний (64x64)", "Легкий (128x128)"], width=200)
        self.pixel_size.pack(side="left", padx=5)
        ctk.CTkButton(row_pixel, text="Создать PixelArt", command=lambda: self.start_task(self.task_pixel_art), fg_color="#9B59B6").pack(side="right")

        card_res = ModernCard(frame, "Умный Ресайз (Изменение размера)", "📏", "Массовое изменение размера (Выбери пресет или впиши свой руками, напр: '800x600' или '50%').", accent_color="#3498DB")
        row_res = ctk.CTkFrame(card_res.content, fg_color="transparent"); row_res.pack(fill="x")
        
        self.resize_mode = ctk.CTkComboBox(row_res, values=[
            "1024x1024", "512x512", "256x256", "128x128", "64x64", "32x32", "16x16", "8x8", 
            "50%", "25%", "Ширина: 1920", "Ширина: 1080"
        ])
        self.resize_mode.set("1024x1024") 
        self.resize_mode.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(row_res, text="Обработать", command=lambda: self.start_task(self.task_image_resize), fg_color="#3498DB").pack(side="right")

        card_mono = ModernCard(frame, "Ч/Б Фильтр (Монохром)", "🖤", "Перевод цветных изображений в черно-белые (Grayscale).", accent_color="#7F8C8D")
        ctk.CTkButton(card_mono.content, text="Сделать черно-белым", command=lambda: self.start_task(self.task_monochrome), fg_color="#7F8C8D").pack(fill="x")

        card1 = ModernCard(frame, "Ультимативный Конвертер", "     🖼️", "Перевод в любые форматы с настройкой качества.")
        row1 = ctk.CTkFrame(card1.content, fg_color="transparent"); row1.pack(fill="x")
        self.img_fmt = ctk.CTkOptionMenu(row1, values=["WEBP", "PNG", "JPEG", "BMP"], width=100); self.img_fmt.pack(side="left", padx=5)
        self.img_q = ctk.CTkSlider(row1, from_=10, to=100, width=150); self.img_q.set(85); self.img_q.pack(side="left", padx=10)
        ctk.CTkButton(row1, text="Конвертировать", command=lambda: self.start_task(self.task_convert_images), fg_color=THEME["accent"]).pack(side="right")

        card_ico = ModernCard(frame, "Генератор Иконок (.ICO)", "💠", "Создает многоразмерные ICO файлы из любых картинок.")
        ctk.CTkButton(card_ico.content, text="Сгенерировать ICO", command=lambda: self.start_task(self.task_generate_ico), fg_color="#9B59B6").pack(fill="x")

        card2 = ModernCard(frame, "Водяные Знаки PRO", "     ©️", "Массовое добавление текста.")
        row2 = ctk.CTkFrame(card2.content, fg_color="transparent"); row2.pack(fill="x")
        self.wm_text = ctk.CTkEntry(row2, width=150, placeholder_text="Текст..."); self.wm_text.pack(side="left", padx=5)
        self.wm_pos = ctk.CTkOptionMenu(row2, values=["Низ-Право", "Центр"], width=120); self.wm_pos.pack(side="left", padx=5)
        ctk.CTkButton(row2, text="Применить", command=lambda: self.start_task(self.task_watermark), fg_color="#E67E22").pack(side="right")

        card3 = ModernCard(frame, "Оптимизатор PRO (Сжатие + Очистка EXIF)", "     🗜️", "Продвинутый Strip, MozJPEG, Guetzli и Floyd-Steinberg дизеринг.")
        row3 = ctk.CTkFrame(card3.content, fg_color="transparent"); row3.pack(fill="x", pady=(5, 0))
        
        self.opt_engine = ctk.CTkOptionMenu(row3, values=["PIL (Встроенный, 4:2:0)", "MozJPEG (Web, Быстрый)", "Guetzli (Макс. качество)"], width=190)
        self.opt_engine.pack(side="left", padx=(0, 10))
        
        self.opt_mode = ctk.CTkComboBox(row3, values=[
            "Баланс (Web, Качество 80%)",
            "Мягкая (Чистый Strip, Q95)",
            "Агрессивная (Сжатие, Q45)",
            "Квантизация (PNG 256 цветов)"
        ], width=230)
        self.opt_mode.set("Баланс (Web, Качество 80%)")
        self.opt_mode.pack(side="left", fill="x", expand=True)
        
        # Добавляем новую строку для выбора формата (Вывод 1)
        row3_sub = ctk.CTkFrame(card3.content, fg_color="transparent")
        row3_sub.pack(fill="x", pady=(10, 0))
        
        self.opt_out_fmt = ctk.CTkOptionMenu(row3_sub, values=["Формат: Оригинал", "Формат: WEBP", "Формат: JPEG", "Формат: PNG"], width=190)
        self.opt_out_fmt.pack(side="left", padx=(0, 10))

        ctk.CTkButton(row3_sub, text="Оптимизировать", command=lambda: self.start_task(self.task_compress_images), fg_color=THEME["success"]).pack(side="right")

        return frame

    def _create_scripts_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Текст & Скрипты", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(25, 15), anchor="w", padx=30)

        card1 = ModernCard(frame, "Универсальный Фикс Кодировки", "🔤", "Преобразует файлы из выбранной кодировки в UTF-8.")
        row1 = ctk.CTkFrame(card1.content, fg_color="transparent"); row1.pack(fill="x")
        self.enc_val = ctk.CTkOptionMenu(row1, values=["windows-1251", "latin-1", "cp866"], width=130); self.enc_val.pack(side="left", padx=5)
        self.enc_exts = ctk.CTkEntry(row1, width=150, placeholder_text=".txt .cfg .ini"); self.enc_exts.insert(0, ".txt .cfg .ini"); self.enc_exts.pack(side="left", padx=5)
        ctk.CTkButton(row1, text="Исправить", command=lambda: self.start_task(self.task_fix_encoding), fg_color=THEME["success"]).pack(side="right")

        card_b64 = ModernCard(frame, "Base64 Шифратор / Декодер", "🔐", "Кодирует или декодирует текстовые файлы с помощью Base64.", accent_color="#1ABC9C")
        row_b = ctk.CTkFrame(card_b64.content, fg_color="transparent"); row_b.pack(fill="x")
        self.b64_mode = ctk.CTkOptionMenu(row_b, values=["Зашифровать (Encode)", "Расшифровать (Decode)"])
        self.b64_mode.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(row_b, text="Выполнить", command=lambda: self.start_task(self.task_base64), fg_color="#1ABC9C", text_color="#000").pack(side="right")

        card_pass = ModernCard(frame, "Генератор Паролей / Токенов", "🔑", "Массовая генерация секьюрных паролей в .txt файл.", accent_color="#E74C3C")
        row_p = ctk.CTkFrame(card_pass.content, fg_color="transparent"); row_p.pack(fill="x")
        ctk.CTkLabel(row_p, text="Кол-во:").pack(side="left")
        self.pass_count = ctk.CTkEntry(row_p, width=60); self.pass_count.insert(0, "100"); self.pass_count.pack(side="left", padx=5)
        ctk.CTkLabel(row_p, text="Длина:").pack(side="left")
        self.pass_len = ctk.CTkEntry(row_p, width=60); self.pass_len.insert(0, "16"); self.pass_len.pack(side="left", padx=5)
        ctk.CTkButton(row_p, text="Сгенерировать", command=lambda: self.start_task(self.task_pass_gen), fg_color="#E74C3C").pack(side="right")

        card3 = ModernCard(frame, "JSON Форматтер", "{} ", "Красивое форматирование или сжатие JSON файлов в папке.")
        row3 = ctk.CTkFrame(card3.content, fg_color="transparent"); row3.pack(fill="x")
        self.json_mode = ctk.CTkOptionMenu(row3, values=["Красиво (Indent 4)", "Минификация"]); self.json_mode.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(row3, text="Форматировать", command=lambda: self.start_task(self.task_format_json), fg_color="#F1C40F", text_color="#000").pack(side="right")

        return frame

    def _create_utils_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Файлы & Утилиты", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(25, 15), anchor="w", padx=30)

        card_sort = ModernCard(frame, "Умная Сортировка Файлов", "     🗂️", "Разбивает свалку файлов в папке по подпапкам (Изображения, Видео, Текст и т.д.).", accent_color="#2ECC71")
        ctk.CTkButton(card_sort.content, text="Выбрать папку и отсортировать", command=lambda: self.start_task(self.task_sort_files), fg_color="#2ECC71", text_color="#000").pack(fill="x")

        card_clean = ModernCard(frame, "Очистка Пустых Папок", "🧹", "Сканирует директорию и удаляет все пустые папки внутри неё.", accent_color="#95A5A6")
        ctk.CTkButton(card_clean.content, text="Очистить дерево папок", command=lambda: self.start_task(self.task_clean_empty_dirs), fg_color="#95A5A6", text_color="#000").pack(fill="x")

        card1 = ModernCard(frame, "Массовое Переименование", "📝", "Поддерживает поиск/замену и префиксы.")
        row1 = ctk.CTkFrame(card1.content, fg_color="transparent"); row1.pack(fill="x")
        self.rn_find = ctk.CTkEntry(row1, width=120, placeholder_text="Найти"); self.rn_find.pack(side="left", padx=2)
        self.rn_repl = ctk.CTkEntry(row1, width=120, placeholder_text="Заменить"); self.rn_repl.pack(side="left", padx=2)
        ctk.CTkButton(row1, text="Переименовать", command=lambda: self.start_task(self.task_bulk_rename), fg_color=THEME["warning"], text_color="#000").pack(side="right")

        card2 = ModernCard(frame, "Поиск дубликатов (Memory-Safe)", "👯", "Изолирует точные копии (Поддерживает огромные файлы).")
        ctk.CTkButton(card2.content, text="Найти дубликаты", command=lambda: self.start_task(self.task_find_duplicates), fg_color=THEME["danger"]).pack(fill="x")

        card4 = ModernCard(frame, "Secure File Shredder", "     🗑️", "Безвозвратное удаление файлов (блочная перезапись мусором перед удалением).")
        ctk.CTkButton(card4.content, text="Уничтожить файлы", command=lambda: self.start_task(self.task_file_shredder), fg_color="#C0392B").pack(fill="x")

        return frame