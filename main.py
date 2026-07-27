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
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex

# Адаптивный полноэкранный режим
Window.fullscreen = 'auto'

CONFIG_PATH = "/storage/emulated/0/userbot_config.json"

# Цвета
GREEN = get_color_from_hex('#2ECC71')
BLUE = get_color_from_hex('#3498DB')
GRAY = get_color_from_hex('#7F8C8D')
WHITE = get_color_from_hex('#FFFFFF')
DARK = get_color_from_hex('#2C3E50')

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]USERBOT[/b]", font_size=sp(28), size_hint=(1, 0.12), markup=True, color=DARK))
        
        scroll = ScrollView(size_hint=(1, 0.58))
        info = Label(
            text="""
[u]Что умеет бот:[/u]

- Анимированная печать
- Голосовые сообщения
- Нейросеть Mistral AI
- Генерация картинок
- Переводчик
- Исчезающие сообщения
- QR-коды
- Издевка над текстом
- Модерация чатов

[u]Нужен Mistral ключ:[/u]
console.mistral.ai
(Можно пропустить)
""",
            font_size=sp(13), size_hint=(1, None), halign='left', valign='top', markup=True, color=DARK
        )
        info.bind(texture_size=info.setter('size'))
        scroll.add_widget(info)
        layout.add_widget(scroll)
        
        btn = Button(text="НАЧАТЬ НАСТРОЙКУ", size_hint=(1, 0.12), background_color=GREEN, font_size=sp(16), color=WHITE)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'phone'))
        layout.add_widget(btn)
        layout.add_widget(Label(size_hint=(1, 0.05)))
        self.add_widget(layout)

class PhoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Ваш номер телефона[/b]", font_size=sp(22), size_hint=(1, 0.1), markup=True, color=DARK))
        layout.add_widget(Label(text="Выберите код страны и введите номер", font_size=sp(12), size_hint=(1, 0.06), color=GRAY))
        
        # Выбор кода страны
        self.country_codes = {
            "+7": "Россия",
            "+1": "США",
            "+44": "Великобритания",
            "+49": "Германия",
            "+380": "Украина",
            "+375": "Беларусь",
            "+7 (KZ)": "Казахстан",
            "+998": "Узбекистан",
            "+90": "Турция",
            "+33": "Франция",
            "+39": "Италия",
            "+34": "Испания",
            "+86": "Китай",
            "+81": "Япония",
        }
        
        from kivy.uix.spinner import Spinner
        self.spinner = Spinner(
            text='+7 (Россия)',
            values=[f"{code} ({name})" for code, name in self.country_codes.items()],
            size_hint=(1, 0.08),
            font_size=sp(14)
        )
        layout.add_widget(self.spinner)
        
        self.phone_input = TextInput(hint_text="Введите номер (без кода)", font_size=sp(18), size_hint=(1, 0.1), multiline=False)
        layout.add_widget(self.phone_input)
        
        self.status_label = Label(text="", font_size=sp(12), size_hint=(1, 0.05), color=get_color_from_hex('#E74C3C'))
        layout.add_widget(self.status_label)
        
        btn = Button(text="ДАЛЕЕ", size_hint=(1, 0.1), background_color=BLUE, font_size=sp(16), color=WHITE)
        btn.bind(on_press=self.save_phone)
        layout.add_widget(btn)
        layout.add_widget(Label(size_hint=(1, 0.4)))
        self.add_widget(layout)
    
    def save_phone(self, instance):
        code = self.spinner.text.split(" ")[0]
        number = self.phone_input.text.strip()
        if number and len(number) > 3:
            phone = code + number
            App.get_running_app().phone = phone
            self.manager.current = 'code'
        else:
            self.status_label.text = "Введите корректный номер"

class CodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Код из Telegram[/b]", font_size=sp(22), size_hint=(1, 0.1), markup=True, color=DARK))
        layout.add_widget(Label(text="На ваш номер отправлен код подтверждения", font_size=sp(12), size_hint=(1, 0.06), color=GRAY))
        self.code_input = TextInput(hint_text="Введите код", font_size=sp(24), size_hint=(1, 0.1), multiline=False)
        layout.add_widget(self.code_input)
        self.status_label = Label(text="", font_size=sp(12), size_hint=(1, 0.05), color=get_color_from_hex('#E74C3C'))
        layout.add_widget(self.status_label)
        btn = Button(text="ПОДТВЕРДИТЬ", size_hint=(1, 0.1), background_color=BLUE, font_size=sp(16), color=WHITE)
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
            self.status_label.text = "Введите код"

class MistralScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Mistral AI ключ[/b]", font_size=sp(22), size_hint=(1, 0.1), markup=True, color=DARK))
        layout.add_widget(Label(text="console.mistral.ai -> API Keys\nМожно пропустить", font_size=sp(12), size_hint=(1, 0.1), color=GRAY))
        self.key_input = TextInput(hint_text="Вставьте ключ или пропустите", font_size=sp(14), size_hint=(1, 0.1), multiline=False)
        layout.add_widget(self.key_input)
        self.status_label = Label(text="", font_size=sp(12), size_hint=(1, 0.05))
        layout.add_widget(self.status_label)
        
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        skip_btn = Button(text="ПРОПУСТИТЬ", background_color=GRAY, font_size=sp(14), color=WHITE)
        skip_btn.bind(on_press=self.skip)
        btn_box.add_widget(skip_btn)
        save_btn = Button(text="СОХРАНИТЬ", background_color=GREEN, font_size=sp(14), color=WHITE)
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
        self.status_label.text = "Ключ сохранен"
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'running'), 0.5)

class RunningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]БОТ ЗАПУЩЕН![/b]", font_size=sp(26), size_hint=(1, 0.15), markup=True, color=GREEN))
        self.status_label = Label(text="Подготовка...", font_size=sp(14), size_hint=(1, 0.25), color=DARK)
        layout.add_widget(self.status_label)
        layout.add_widget(Label(text=".help - список команд\n.setup - сменить ключ", font_size=sp(12), size_hint=(1, 0.3), color=GRAY))
        layout.add_widget(Label(text="GitHub: /your_repo", font_size=sp(10), size_hint=(1, 0.15), color=get_color_from_hex('#BDC3C7')))
        self.add_widget(layout)
    
    def on_enter(self):
        app = App.get_running_app()
        config = {"phone": app.phone, "code": app.code, "mistral_key": app.mistral_key}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
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
        self.title = "UserBot"
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(PhoneScreen(name='phone'))
        sm.add_widget(CodeScreen(name='code'))
        sm.add_widget(MistralScreen(name='mistral'))
        sm.add_widget(RunningScreen(name='running'))
        return sm

if __name__ == "__main__":
    UserbotApp().run()
