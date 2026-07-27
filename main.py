import os
import json
import threading
import sys
import subprocess
import asyncio
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

async def send_code_async(phone, api_id, api_hash):
    from telethon import TelegramClient
    client = TelegramClient('/storage/emulated/0/temp_session', api_id, api_hash)
    await client.connect()
    try:
        result = await client.send_code_request(phone)
        await client.disconnect()
        return True, str(result.phone_code_hash)
    except Exception as e:
        await client.disconnect()
        return False, str(e)

async def verify_code_async(phone, code, code_hash, password, api_id, api_hash):
    from telethon import TelegramClient, errors
    client = TelegramClient('/storage/emulated/0/userbot_session', api_id, api_hash)
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
        await client.disconnect()
        return True, "OK"
    except errors.SessionPasswordNeededError:
        if password:
            try:
                await client.sign_in(password=password)
                await client.disconnect()
                return True, "OK"
            except Exception as e:
                await client.disconnect()
                return False, f"Неверный пароль: {e}"
        await client.disconnect()
        return True, "PASSWORD"
    except errors.PhoneCodeInvalidError:
        await client.disconnect()
        return False, "Неверный код"
    except errors.PhoneCodeExpiredError:
        await client.disconnect()
        return False, "Код истёк, запросите новый"
    except Exception as e:
        await client.disconnect()
        return False, str(e)

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        layout.add_widget(Label(text="[b]USERBOT[/b]", font_size=sp(40), markup=True, color=WHITE))
        layout.add_widget(Label(text="Многофункциональный бот\nдля Telegram", font_size=sp(16), color=GRAY))
        layout.add_widget(Label(text="Загрузка...", font_size=sp(14), color=YELLOW))
        self.add_widget(layout)
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.check_and_go(), 1)
    
    def check_and_go(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                config = json.load(f)
            if config.get("logged_in"):
                self.manager.current = 'running'
                return
        self.manager.current = 'welcome'

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
console.mistral.ai (можно пропустить)
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
        start_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'api'))
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
[u]Как получить API ID и API Hash:[/u]
1. my.telegram.org
2. Войдите под своим номером
3. API Development
4. Создайте приложение (любое название)
5. Скопируйте api_id и api_hash

[u]Как получить Mistral ключ:[/u]
1. console.mistral.ai
2. Зарегистрируйтесь
3. API Keys -> Create key

[u]Команды бота:[/u]
.txt текст - анимированная печать
.voice текст - голосовое сообщение
.timer N текст - исчезающее сообщение
.mock - ИзДeВкА над текстом (reply)
.ai вопрос - Mistral AI
.draw описание - рисует картинку
.trans - перевод сообщения (reply)
.qr ссылка - генератор QR-кода
.save - сохранить в Избранное (reply)
.mute N - мут на N минут (reply)
.unmute - снять мут (reply)
.warn N - лимит сообщений (reply)
.unwarn - снять лимит (reply)
.panic - очистить историю
.del N - удалить чат через N сек
.help - меню в чате
.setup - сменить Mistral ключ

[u]Важно:[/u]
- Отключите облачный пароль Telegram
- API ключи хранятся локально
- EXE может ругаться антивирусом
""",
            font_size=sp(12), size_hint=(1, None), halign='left', valign='top', color=GRAY, markup=True
        )
        help_text.bind(texture_size=help_text.setter('size'))
        scroll.add_widget(help_text)
        layout.add_widget(scroll)
        btn = Button(text="НАЗАД", size_hint=(1, 0.08), background_color=BLUE, font_size=sp(14), color=WHITE)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'welcome'))
        layout.add_widget(btn)
        self.add_widget(layout)

class ApiScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]API данные[/b]", font_size=sp(22), size_hint=(1, 0.08), markup=True, color=WHITE))
        layout.add_widget(Label(text="my.telegram.org -> API Development\nОставьте пустым для общих ключей", font_size=sp(11), size_hint=(1, 0.1), color=GRAY))
        
        self.api_id_input = TextInput(hint_text="API ID (число)", font_size=sp(16), size_hint=(1, 0.08), multiline=False, input_filter='int')
        layout.add_widget(self.api_id_input)
        
        self.api_hash_input = TextInput(hint_text="API Hash", font_size=sp(16), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.api_hash_input)
        
        self.status_label = Label(text="", font_size=sp(11), size_hint=(1, 0.04), color=GRAY)
        layout.add_widget(self.status_label)
        
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        back_btn = Button(text="НАЗАД", background_color=GRAY, font_size=sp(14), color=WHITE)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'welcome'))
        btn_box.add_widget(back_btn)
        
        skip_btn = Button(text="ПРОПУСТИТЬ", background_color=GRAY, font_size=sp(14), color=WHITE)
        skip_btn.bind(on_press=self.skip)
        btn_box.add_widget(skip_btn)
        
        save_btn = Button(text="ДАЛЕЕ", background_color=BLUE, font_size=sp(14), color=WHITE)
        save_btn.bind(on_press=self.save_api)
        btn_box.add_widget(save_btn)
        layout.add_widget(btn_box)
        layout.add_widget(Label(size_hint=(1, 0.45)))
        self.add_widget(layout)
    
    def skip(self, instance):
        self.manager.current = 'phone'
    
    def save_api(self, instance):
        api_id = self.api_id_input.text.strip()
        api_hash = self.api_hash_input.text.strip()
        app = App.get_running_app()
        if api_id and api_hash:
            try:
                app.api_id = int(api_id)
                app.api_hash = api_hash
                self.status_label.text = "Свои ключи сохранены"
            except:
                self.status_label.text = "Ошибка: API ID должен быть числом"
                return
        else:
            self.status_label.text = "Используются общие ключи"
        self.manager.current = 'phone'

class PhoneScreen(Screen):
    code_hash = ""
    
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
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'api'))
        btn_box.add_widget(back_btn)
        
        self.next_btn = Button(text="ОТПРАВИТЬ КОД", background_color=BLUE, font_size=sp(14), color=WHITE)
        self.next_btn.bind(on_press=self.send_code)
        btn_box.add_widget(self.next_btn)
        layout.add_widget(btn_box)
        
        layout.add_widget(Label(size_hint=(1, 0.45)))
        self.add_widget(layout)
    
    def send_code(self, instance):
        code = self.spinner.text.split(" ")[0]
        number = self.phone_input.text.strip()
        if not number or len(number) < 4:
            self.status_label.text = "Введите корректный номер"
            return
        
        phone = code + number
        app = App.get_running_app()
        app.phone = phone
        
        self.next_btn.disabled = True
        self.next_btn.text = "Отправляю..."
        self.status_label.text = "Отправляю код..."
        
        def on_result(success, result):
            if success:
                self.code_hash = result
                Clock.schedule_once(lambda dt: self.go_to_code(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_error(result), 0)
        
        def do_send():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            app = App.get_running_app()
            ok, data = loop.run_until_complete(send_code_async(phone, app.api_id, app.api_hash))
            loop.close()
            on_result(ok, data)
        
        threading.Thread(target=do_send, daemon=True).start()
    
    def go_to_code(self):
        self.next_btn.disabled = False
        self.next_btn.text = "ОТПРАВИТЬ КОД"
        self.status_label.text = "Код отправлен!"
        self.manager.current = 'code'
    
    def show_error(self, error):
        self.next_btn.disabled = False
        self.next_btn.text = "ОТПРАВИТЬ КОД"
        self.status_label.text = f"Ошибка: {error}"

class CodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        layout.add_widget(Label(text="[b]Код подтверждения[/b]", font_size=sp(22), size_hint=(1, 0.08), markup=True, color=WHITE))
        layout.add_widget(Label(text="Введите код из Telegram", font_size=sp(12), size_hint=(1, 0.05), color=GRAY))
        self.code_input = TextInput(hint_text="12345", font_size=sp(24), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.code_input)
        
        self.password_input = TextInput(hint_text="Облачный пароль (если есть)", font_size=sp(16), size_hint=(1, 0.08), multiline=False)
        layout.add_widget(self.password_input)
        
        self.status_label = Label(text="", font_size=sp(12), size_hint=(1, 0.04), color=RED)
        layout.add_widget(self.status_label)
        
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        back_btn = Button(text="НАЗАД", background_color=GRAY, font_size=sp(14), color=WHITE)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'phone'))
        btn_box.add_widget(back_btn)
        
        self.verify_btn = Button(text="ПОДТВЕРДИТЬ", background_color=BLUE, font_size=sp(14), color=WHITE)
        self.verify_btn.bind(on_press=self.verify_code)
        btn_box.add_widget(self.verify_btn)
        layout.add_widget(btn_box)
        
        layout.add_widget(Label(size_hint=(1, 0.45)))
        self.add_widget(layout)
    
    def verify_code(self, instance):
        code = self.code_input.text.strip()
        password = self.password_input.text.strip()
        
        if not code:
            self.status_label.text = "Введите код"
            return
        
        app = App.get_running_app()
        phone = app.phone
        phone_screen = self.manager.get_screen('phone')
        code_hash = phone_screen.code_hash
        
        self.verify_btn.disabled = True
        self.verify_btn.text = "Проверяю..."
        self.status_label.text = "Проверяю код..."
        
        def on_result(success, result):
            if success:
                if result == "PASSWORD":
                    Clock.schedule_once(lambda dt: self.need_password(), 0)
                else:
                    app.code = code
                    app.password = password
                    app.code_hash = code_hash
                    Clock.schedule_once(lambda dt: self.go_mistral(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_error(result), 0)
        
        def do_verify():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            app = App.get_running_app()
            ok, data = loop.run_until_complete(verify_code_async(phone, code, code_hash, password, app.api_id, app.api_hash))
            loop.close()
            on_result(ok, data)
        
        threading.Thread(target=do_verify, daemon=True).start()
    
    def need_password(self):
        self.verify_btn.disabled = False
        self.verify_btn.text = "ПОДТВЕРДИТЬ"
        self.status_label.text = "Введите облачный пароль"
    
    def go_mistral(self):
        self.verify_btn.disabled = False
        self.verify_btn.text = "ПОДТВЕРДИТЬ"
        self.manager.current = 'mistral'
    
    def show_error(self, error):
        self.verify_btn.disabled = False
        self.verify_btn.text = "ПОДТВЕРДИТЬ"
        self.status_label.text = f"Ошибка: {error}"

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
        self.manager.current = 'running'

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
        config = {
            "api_id": app.api_id,
            "api_hash": app.api_hash,
            "phone": app.phone,
            "code": app.code,
            "password": app.password,
            "code_hash": app.code_hash,
            "mistral_key": app.mistral_key,
            "logged_in": True
        }
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
    code_hash = ""
    mistral_key = ""
    api_id = 2040
    api_hash = "b18441a1ff607e10a989891a5462e627"
    
    def build(self):
        self.title = "UserBot"
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(HelpScreen(name='help_screen'))
        sm.add_widget(ApiScreen(name='api'))
        sm.add_widget(PhoneScreen(name='phone'))
        sm.add_widget(CodeScreen(name='code'))
        sm.add_widget(MistralScreen(name='mistral'))
        sm.add_widget(RunningScreen(name='running'))
        return sm

if __name__ == "__main__":
    UserbotApp().run()
