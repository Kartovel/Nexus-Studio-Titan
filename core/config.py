# -*- coding: utf-8 -*-
import json
import os
from core.constants import DEFAULT_CONFIG

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    for k, v in loaded.items():
                        if k in self.config: self.config[k] = v
            except Exception as e:
                print(f"Ошибка загрузки конфига: {e}")

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")

    def get(self, key, default=None): return self.config.get(key, default)
    def set(self, key, value): self.config[key] = value; self.save()