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

Window.fullscreen = 'auto'

CONFIG_PATH = "/storage/emulated/0/userbot_config.json"

GREEN = get_color_from_hex('#2ECC71')
BLUE = get_color_from_hex('#3498DB')
GRAY = get_color_from_hex('#7F8C8D')
WHITE = get_color_from_hex('#FFFFFF')
DARK = get_color_from_hex('#1a1a2e')
RED = get_color_from_hex('#E74C3C')
YELLOW = get_color_from_hex('#F39C12')

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        layout.add_widget(Label(text="[b]USERBOT[/b]", font_size=sp(40), markup=True, color=WHITE))
        layout.add_widget(Label(text="Многофункциональный бот\nдля Telegram", font_size=sp(16), color=GRAY, halign='center'))
        layout.add_widget(Label(text="Загрузка...", font_size=sp(14), color=YELLOW))
        layout.add_widget(Label(size_hint=(1, 0.3)))
        self.add_widget(layout)
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.check_and_go(), 1)
    
    def check_and_go(self):
        if os.path.exists(CONFIG_PATH):
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'running'), 1)
        else:
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'welcome'), 1)

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        layout.add_widget(Label(text="[b]USERBOT[/b]", font_size=sp(28), size_hint=(1, 0.1), markup=True, color=WHITE))
        
        scroll = ScrollView(size_hint=(1, 0.55))
        info = Label(
            text="""
Что умеет бот:

- Анимированная печать
- Голосовые сообщения
- Нейросеть Mistral AI
- Генерация картинок
- Переводчик
- Исчезающие сообщения
- QR-коды
- Модерация чатов

Нужен Mistral ключ:
console.mistral.ai
(Можно пропустить)
""",
            font_size=sp(13), size_hint=(1, None), halign='left', valign='top', color=GRAY
        )
        info.bind(texture_size=info.setter('size'))
        scroll.add_widget(info)
        layout.add_widget(scroll)
        
        btn_box = BoxLayout(size_hint=(1, 0.12), spacing=dp(10))
        
        help_btn = Button(text="ПОМОЩЬ", background_color=GRAY, font_size=sp(14), color=WHITE)
        help_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'help_screen'))
        btn_box.add_widget(help_btn)
        
        start_btn = Button(text="НАЧАТЬ", background_color=GREEN, font_size=sp(14), color=WHITE)
        start_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'phone'))
        btn_box.add_widget(start_btn)
        
        layout.add_widget(btn_box)
        self.add_widget(layout)

class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        layout.add_widget(Label(text="[b]СПРАВКА[/b]", font_size=sp(22), size_hint=(1, 0.08), markup=True, color=WHITE))
        
        scroll = ScrollView(size_hint=(1, 0.8))
        help_text = Label(
            text="""
Текст и голос:
.txt текст - анимированная печать
.voice текст - голосовое сообщение
.timer N текст - исчезающее сообщение
.mock - ИзДeВкА над текстом (reply)

Нейросети:
.ai вопрос - Mistral AI
.draw описание - рисует картинку

Инструменты:
.trans - перевод сообщения (reply)
.qr ссылка - генератор QR-кода
.save - сохранить в Избранное (reply)

Модерация:
.mute N - мут на N минут (reply)
.unmute - снять мут (reply)
.warn N - лимит сообщений (reply)
.unwarn - снять лимит (reply)

Очистка:
.panic - очистить историю
.del N - удалить чат через N сек

.help - это меню в чате
.setup - сменить Mistral ключ

Получить Mistral ключ:
1. console.mistral.ai
2. Зарегистрироваться
3. API Keys -> Create key
4. Скопировать ключ

Важно:
- Отключите облачный пароль Telegram
- EXE может ругаться антивирусом
  (это ложное срабатывание)
- Код открыт на GitHub
""",
            font_size=sp(12), size_hint=(1, None), halign='left', valign='top', color=GRAY
        )
        help_text.bind(texture_size=help_text.setter('size'))
        scroll.add_widget(help_text)
        layout.add_widget(scroll)
        
        btn = Button(text="НАЗАД", size_hint=(1, 0.08), background_color=BLUE, font_size=sp(14), color=WHITE)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'welcome'))
        layout.add_widget(btn)
        self.add_widget(layout)

class PhoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Номер телефона[/b]", font_size=sp(22), size_hint=(1, 0.08), markup=True, color=WHITE))
        layout.add_widget(Label(text="Выберите код страны и введите номер", font_size=sp(12), size_hint=(1, 0.05), color=GRAY))
        
        from kivy.uix.spinner import Spinner
        self.spinner = Spinner(
            text='+7 (Россия)',
            values=['+7 (Россия)', '+1 (США)', '+44 (Великобритания)', '+49 (Германия)', '+380 (Украина)',
                    '+375 (Беларусь)', '+998 (Узбекистан)', '+90 (Турция)', '+33 (Франция)',
                    '+39 (Италия)', '+34 (Испания)', '+86 (Китай)', '+81 (Япония)'],
            size_hint=(1, 0.08), font_size=sp(14)
        )
        layout.add_widget(self.spinner)
        
        self.phone_input = TextInput(hint_text="Номер (без кода)", font_size=sp(18), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.phone_input)
        self.status_label = Label(text="", font_size=sp(12), size_hint=(1, 0.04), color=RED)
        layout.add_widget(self.status_label)
        
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        back_btn = Button(text="НАЗАД", background_color=GRAY, font_size=sp(14), color=WHITE)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'welcome'))
        btn_box.add_widget(back_btn)
        
        next_btn = Button(text="ДАЛЕЕ", background_color=BLUE, font_size=sp(14), color=WHITE)
        next_btn.bind(on_press=self.save_phone)
        btn_box.add_widget(next_btn)
        layout.add_widget(btn_box)
        
        layout.add_widget(Label(size_hint=(1, 0.45)))
        self.add_widget(layout)
    
    def save_phone(self, instance):
        code = self.spinner.text.split(" ")[0]
        number = self.phone_input.text.strip()
        if number and len(number) > 3:
            phone = code + number
            App.get_running_app().phone = phone
            self.status_label.text = "Отправляю код..."
            threading.Thread(target=self.send_code, args=(phone,), daemon=True).start()
        else:
            self.status_label.text = "Введите корректный номер"
    
    def send_code(self, phone):
        try:
            from telethon import TelegramClient
            client = TelegramClient('/storage/emulated/0/temp_session', 2040, "b18441a1ff607e10a989891a5462e627")
            client.connect()
            client.send_code_request(phone)
            client.disconnect()
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'code'), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', f"Ошибка: {e}"), 0)

class CodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Код из Telegram[/b]", font_size=sp(22), size_hint=(1, 0.08), markup=True, color=WHITE))
        layout.add_widget(Label(text="На ваш номер отправлен код", font_size=sp(12), size_hint=(1, 0.05), color=GRAY))
        self.code_input = TextInput(hint_text="Введите код", font_size=sp(24), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.code_input)
        
        self.password_input = TextInput(hint_text="Облачный пароль (если есть)", font_size=sp(16), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.password_input)
        
        self.status_label = Label(text="", font_size=sp(12), size_hint=(1, 0.04), color=RED)
        layout.add_widget(self.status_label)
        
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        back_btn = Button(text="НАЗАД", background_color=GRAY, font_size=sp(14), color=WHITE)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'phone'))
        btn_box.add_widget(back_btn)
        
        next_btn = Button(text="ПОДТВЕРДИТЬ", background_color=BLUE, font_size=sp(14), color=WHITE)
        next_btn.bind(on_press=self.save_code)
        btn_box.add_widget(next_btn)
        layout.add_widget(btn_box)
        
        layout.add_widget(Label(size_hint=(1, 0.45)))
        self.add_widget(layout)
    
    def save_code(self, instance):
        code = self.code_input.text.strip()
        password = self.password_input.text.strip()
        if code:
            app = App.get_running_app()
            app.code = code
            app.password = password
            self.manager.current = 'mistral'
        else:
            self.status_label.text = "Введите код"

class MistralScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Mistral AI ключ[/b]", font_size=sp(22), size_hint=(1, 0.08), markup=True, color=WHITE))
        layout.add_widget(Label(text="console.mistral.ai -> API Keys\nМожно пропустить", font_size=sp(12), size_hint=(1, 0.1), color=GRAY))
        self.key_input = TextInput(hint_text="Вставьте ключ", font_size=sp(14), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.key_input)
        
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        back_btn = Button(text="НАЗАД", background_color=GRAY, font_size=sp(14), color=WHITE)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'code'))
        btn_box.add_widget(back_btn)
        
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
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'running'), 0.5)

class RunningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]БОТ ЗАПУЩЕН![/b]", font_size=sp(26), size_hint=(1, 0.15), markup=True, color=GREEN))
        self.status_label = Label(text="Подготовка...", font_size=sp(14), size_hint=(1, 0.25), color=GRAY)
        layout.add_widget(self.status_label)
        layout.add_widget(Label(text=".help - список команд\n.setup - сменить ключ", font_size=sp(12), size_hint=(1, 0.3), color=GRAY))
        layout.add_widget(Label(size_hint=(1, 0.2)))
        self.add_widget(layout)
    
    def on_enter(self):
        app = App.get_running_app()
        config = {"phone": app.phone, "code": app.code, "password": app.password, "mistral_key": app.mistral_key}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
        self.status_label.text = "Запускаю бота..."
        threading.Thread(target=self.start_bot, daemon=True).start()
    
    def start_bot(self):
        app = App.get_running_app()
        if app.mistral_key:
            try:
                import mistralai
            except ImportError:
                subprocess.run([sys.executable or "python3", "-m", "pip", "install", "mistralai"], capture_output=True)
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "userbot_core.py")
        subprocess.Popen([sys.executable or "python3", script])

class UserbotApp(App):
    phone = ""
    code = ""
    password = ""
    mistral_key = ""
    
    def build(self):
        self.title = "UserBot"
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(HelpScreen(name='help_screen'))
        sm.add_widget(PhoneScreen(name='phone'))
        sm.add_widget(CodeScreen(name='code'))
        sm.add_widget(MistralScreen(name='mistral'))
        sm.add_widget(RunningScreen(name='running'))
        return sm

if __name__ == "__main__":
    UserbotApp().run()
