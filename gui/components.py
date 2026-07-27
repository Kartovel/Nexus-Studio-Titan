# -*- coding: utf-8 -*-
import customtkinter as ctk
from core.constants import THEME

class ModernCard(ctk.CTkFrame):
    """Премиальная карточка для утилит с улучшенным дизайном"""
    def __init__(self, master, title, icon, description, accent_color=None, **kwargs):
        # Добавляем более явный бордер, чтобы создать эффект "карточки"
        super().__init__(master, fg_color=THEME["card_bg"], corner_radius=15, 
                         border_width=2, border_color="#2b3240", **kwargs)
        self.pack(fill="x", padx=30, pady=15) # Увеличили отступы для "воздуха"
        
        # Заголовок с иконкой
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        
        icon_color = accent_color if accent_color else THEME["accent"]
        
        # Контейнер для иконки с "подложкой"
        icon_bg = ctk.CTkFrame(header, fg_color="#1e2330", corner_radius=10, width=50, height=50)
        icon_bg.pack(side="left", padx=(0, 15))
        icon_bg.pack_propagate(False)
        
        icon_lbl = ctk.CTkLabel(icon_bg, text=icon, font=ctk.CTkFont(size=28), text_color=icon_color)
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Текстовая часть заголовка
        title_lbl = ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=THEME["text_main"])
        title_lbl.pack(side="left")
        
        # Описание стало чуть крупнее и читабельнее
        desc_lbl = ctk.CTkLabel(self, text=description, font=ctk.CTkFont(size=13), 
                                text_color=THEME["text_muted"], justify="left", wraplength=750)
        desc_lbl.pack(fill="x", padx=25, pady=(5, 20), anchor="w")
        
        # Контейнер для элементов управления (кнопки, инпуты)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="x", padx=25, pady=(0, 20))