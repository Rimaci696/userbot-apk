import os
import json
import threading
import sys
import subprocess
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

Window.size = (400, 700)

CONFIG_PATH = "/storage/emulated/0/userbot_config.json"

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="🚀 USERBOT", font_size=36, size_hint=(1, 0.15), bold=True))
        
        scroll = ScrollView(size_hint=(1, 0.55))
        info = Label(
            text="""
Добро пожаловать в UserBot!

Что умеет бот:
📝 Анимированная печать
🎤 Голосовые сообщения
🤖 Нейросеть Mistral AI
🎨 Генерация картинок
🌐 Переводчик
⏳ Исчезающие сообщения
📱 QR-коды
😈 ИзДeВкА над текстом
🛡 Модерация чатов

━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Нужен Mistral ключ:
1. console.mistral.ai
2. Зарегистрироваться
3. API Keys → Create key
(Можно пропустить)
━━━━━━━━━━━━━━━━━━━━━━━━
""",
            font_size=13, size_hint=(1, None), halign='left', valign='top'
        )
        info.bind(texture_size=info.setter('size'))
        scroll.add_widget(info)
        layout.add_widget(scroll)
        
        btn = Button(text="▶ НАЧАТЬ НАСТРОЙКУ", size_hint=(1, 0.15), background_color=(0.2, 0.7, 0.3, 1), font_size=18)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'phone'))
        layout.add_widget(btn)
        self.add_widget(layout)

class PhoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="📱 Ваш номер телефона", font_size=22, size_hint=(1, 0.15), bold=True))
        layout.add_widget(Label(text="Формат: +79123456789", font_size=13, size_hint=(1, 0.08)))
        self.phone_input = TextInput(text="+7", font_size=20, size_hint=(1, 0.12), multiline=False)
        layout.add_widget(self.phone_input)
        self.status_label = Label(text="", font_size=13, size_hint=(1, 0.08))
        layout.add_widget(self.status_label)
        btn = Button(text="▶ ДАЛЕЕ", size_hint=(1, 0.12), background_color=(0.2, 0.5, 0.9, 1), font_size=18)
        btn.bind(on_press=self.save_phone)
        layout.add_widget(btn)
        layout.add_widget(Label(size_hint=(1, 0.5)))
        self.add_widget(layout)
    
    def save_phone(self, instance):
        phone = self.phone_input.text.strip()
        if phone and len(phone) > 5:
            App.get_running_app().phone = phone
            self.manager.current = 'code'
        else:
            self.status_label.text = "❌ Введите корректный номер"

class CodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="🔐 Код из Telegram", font_size=22, size_hint=(1, 0.15), bold=True))
        layout.add_widget(Label(text="Вам придёт сообщение с кодом", font_size=13, size_hint=(1, 0.08)))
        self.code_input = TextInput(hint_text="12345", font_size=24, size_hint=(1, 0.12), multiline=False)
        layout.add_widget(self.code_input)
        self.status_label = Label(text="", font_size=13, size_hint=(1, 0.08))
        layout.add_widget(self.status_label)
        btn = Button(text="▶ ПОДТВЕРДИТЬ", size_hint=(1, 0.12), background_color=(0.2, 0.5, 0.9, 1), font_size=18)
        btn.bind(on_press=self.save_code)
        layout.add_widget(btn)
        layout.add_widget(Label(size_hint=(1, 0.5)))
        self.add_widget(layout)
    
    def save_code(self, instance):
        code = self.code_input.text.strip()
        if code:
            App.get_running_app().code = code
            self.manager.current = 'mistral'
        else:
            self.status_label.text = "❌ Введите код"

class MistralScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="🤖 Mistral AI ключ", font_size=22, size_hint=(1, 0.15), bold=True))
        layout.add_widget(Label(text="console.mistral.ai → API Keys\nМожно пропустить", font_size=13, size_hint=(1, 0.12)))
        self.key_input = TextInput(hint_text="Вставьте ключ или пропустите", font_size=16, size_hint=(1, 0.12), multiline=False)
        layout.add_widget(self.key_input)
        self.status_label = Label(text="", font_size=13, size_hint=(1, 0.08))
        layout.add_widget(self.status_label)
        btn_box = BoxLayout(size_hint=(1, 0.12), spacing=10)
        skip_btn = Button(text="ПРОПУСТИТЬ", background_color=(0.5, 0.5, 0.5, 1), font_size=16)
        skip_btn.bind(on_press=self.skip)
        btn_box.add_widget(skip_btn)
        save_btn = Button(text="▶ СОХРАНИТЬ", background_color=(0.2, 0.7, 0.3, 1), font_size=16)
        save_btn.bind(on_press=self.save_key)
        btn_box.add_widget(save_btn)
        layout.add_widget(btn_box)
        layout.add_widget(Label(size_hint=(1, 0.45)))
        self.add_widget(layout)
    
    def skip(self, instance):
        App.get_running_app().mistral_key = ""
        self.manager.current = 'running'
    
    def save_key(self, instance):
        App.get_running_app().mistral_key = self.key_input.text.strip()
        self.status_label.text = "✅ Ключ сохранён"
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'running'), 0.5)

class RunningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="✅ БОТ ЗАПУЩЕН!", font_size=28, size_hint=(1, 0.2), bold=True, color=(0.2, 0.8, 0.3, 1)))
        self.status_label = Label(text="Подготовка...", font_size=15, size_hint=(1, 0.3))
        layout.add_widget(self.status_label)
        layout.add_widget(Label(text=".help — список команд\n.setup — сменить ключ", font_size=13, size_hint=(1, 0.3)))
        layout.add_widget(Label(text="GitHub: /your_repo", font_size=11, size_hint=(1, 0.2), color=(0.5, 0.5, 0.5, 1)))
        self.add_widget(layout)
    
    def on_enter(self):
        app = App.get_running_app()
        config = {"phone": app.phone, "code": app.code, "mistral_key": app.mistral_key}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
        
        # Устанавливаем mistralai если есть ключ
        if app.mistral_key:
            self.status_label.text = "Устанавливаю ИИ (1 раз)..."
            threading.Thread(target=self.install_mistral, daemon=True).start()
        else:
            self.status_label.text = "Запускаю бота..."
            threading.Thread(target=self.run_bot, daemon=True).start()
    
    def install_mistral(self):
        try:
            import mistralai
            self.status_label.text = "ИИ уже установлен\nЗапускаю бота..."
        except ImportError:
            subprocess.run([sys.executable or "python3", "-m", "pip", "install", "mistralai"], capture_output=True)
            self.status_label.text = "ИИ установлен!\nЗапускаю бота..."
        self.run_bot()
    
    def run_bot(self):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "userbot_core.py")
        subprocess.run([sys.executable or "python3", script])

class UserbotApp(App):
    phone = ""
    code = ""
    mistral_key = ""
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(PhoneScreen(name='phone'))
        sm.add_widget(CodeScreen(name='code'))
        sm.add_widget(MistralScreen(name='mistral'))
        sm.add_widget(RunningScreen(name='running'))
        return sm

if __name__ == "__main__":
    UserbotApp().run()