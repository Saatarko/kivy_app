import json
from urllib.parse import urlencode
from datetime import datetime, timedelta
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelStrip
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from functools import partial


class NotificationManager:
    def __init__(self):
        pass

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical')
        label = Label(text=message, text_size=(400, None), halign='center')
        content.add_widget(label)
        closed_button = Button(text='Закрыть', size_hint_x=0.5, pos_hint={'center_x': 0.5})

        popup = Popup(title=title,
                      content=content,
                      size_hint=(None, None), size=(400, 400))
        closed_button.bind(on_press=popup.dismiss)  # Привязываем метод dismiss к popup
        content.add_widget(closed_button)

        popup.open()

    def show_popup_success_login(self):
        self.show_popup('Успех', 'Вы успешно вошли в систему')

    def show_popup_error(self, error_message):
        self.show_popup('Ошибка', error_message)


notification_manager = NotificationManager()  # создаем экземпляр класса уведомлений


class Auth(GridLayout):
    def __init__(self, **kwargs):
        super(Auth, self).__init__(**kwargs)

    def create_logout_layout(self, parent_layout):
        login_layout = BoxLayout(orientation='vertical')
        login_layout.clear_widgets()  # Очищаем родительский layout
        login_layout.add_widget(Label(text='Вы уже вошли в систему'))
        logout_button = Button(text='Выход', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        logout_button.bind(on_press=self.logout)
        login_layout.add_widget(logout_button)

        logout_button_closed = Button(text='Закрыть', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        logout_button_closed.bind(on_press=partial(self.closed, parent_layout=parent_layout))
        login_layout.add_widget(logout_button_closed)

        parent_layout.clear_widgets()
        parent_layout.add_widget(login_layout)


    def closed(self, instance, parent_layout):

        parent_layout.clear_widgets()


    def create_login_layout(self, parent_layout):
        # Создаем отдельный GridLayout для формы логина
        login_layout = BoxLayout(orientation='vertical')
        login_layout.add_widget(Widget())
        # Добавляем виджеты в login_layout
        login_layout.add_widget(Label(text='Введите логин(email) и пароль для входа', size_hint_x=0.5,
                                      pos_hint={'center_x': 0.5}))
        login_layout.add_widget(Label(text='Логин(email)', size_hint_x=0.5, pos_hint={'center_x': 0.5}))
        self.username_input = TextInput(size_hint_x=0.5, multiline=False, pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.username_input)
        login_layout.add_widget(Label(text='Пароль', size_hint_x=0.5, pos_hint={'center_x': 0.5}))
        self.password_input = TextInput(size_hint_x=0.5, password=True, multiline=False, pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.password_input)
        login_button = Button(text='Войти', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        login_button.bind(on_press=partial(self.login, parent_layout=parent_layout))
        login_layout.add_widget(login_button)
        login_layout.add_widget(Widget())
        login_layout.add_widget(Label(text='Или зарегистрируйтесь', size_hint_x=0.5,
                                      pos_hint={'center_x': 0.5}))
        login_layout.add_widget(Widget())
        login_layout.add_widget(Label(text='Введите логин(email)', size_hint_x=0.5, pos_hint={'center_x': 0.5}))
        self.reg_username_input = TextInput(size_hint_x=0.5, multiline=False, pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.reg_username_input)
        login_layout.add_widget(Label(text='Пароль', size_hint_x=0.5, pos_hint={'center_x': 0.5}))
        self.reg_password_input = TextInput(size_hint_x=0.5, password=True, multiline=False, pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.reg_password_input)
        login_layout.add_widget(Label(text='Подтверждение пароля', size_hint_x=0.5, pos_hint={'center_x': 0.5}))
        self.reg_password_input2 = TextInput(size_hint_x=0.5, password=True, multiline=False,
                                             pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.reg_password_input2)
        reg_button = Button(text='Регистрация', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        reg_button.bind(on_press=partial(self.registration, parent_layout=parent_layout))
        login_layout.add_widget(reg_button)
        login_layout.add_widget(Widget())

        # Очищаем родительский layout и добавляем в него login_layout
        parent_layout.clear_widgets()
        parent_layout.add_widget(login_layout)

    def login(self, instance, parent_layout):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        login_url = 'http://127.0.0.1:8000/api/v1/auth/login'
        request_data = urlencode({
            'username': username,
            'password': password
        })
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        parent_layout.clear_widgets()
        UrlRequest(login_url, req_body=request_data, req_headers=headers,
                   on_success=self.on_login_success, on_failure=self.on_login_failure)

    def on_login_failure(self, request, result):
        message =  'Ошибка аутентификации: или некорректные данные или пользователя не существует'
        notification_manager.show_popup_error(message)
        # print('Ошибка аутентификации:', request.resp_status, result)

    def on_login_success(self, request, result):
        # Сохранение токена аутентификации и переход к экрану курсов
        App.get_running_app().token = result['access_token']

        # Создание отдельного словаря для отслеживания времени истечения токена в приложении
        App.get_running_app().token_check = {
            'access_token': result['access_token'],
            'expiry': datetime.now() + timedelta(minutes=55)  # Устанавливаем время истечения на 55 минут
        }

        notification_manager.show_popup_success_login()

    def logout(self, instance):
        # Получаем текущий токен
        token = App.get_running_app().token
        if token:
            logout_url = 'http://127.0.0.1:8000/api/v1/auth/logout'
            headers = {'Authorization': f'Bearer {token}', 'accept': 'application/json'}

            # Используем POST-запрос для выхода из системы
            UrlRequest(logout_url, method='POST', req_headers=headers, on_success=self.on_logout_success,
                       on_failure=self.on_logout_failure)

    def on_logout_success(self, request, result):
        # Сброс токена после успешного выхода из системы
        App.get_running_app().token = None
        App.get_running_app().token_check = None
        # Обновление вкладки аутентификации

        # self.check_token()

    def on_logout_failure(self, request, result):
        print('Ошибка при выходе из системы:', request.resp_status, result)

    def check_token(self, parent_layout):
        token_check = App.get_running_app().token_check

        if token_check and token_check['access_token'] != 'your_token' and (datetime.now() < token_check['expiry']):
            self.create_logout_layout(parent_layout)  # Добавляем layout для logout непосредственно
        else:
            App.get_running_app().token = None
            App.get_running_app().token_check = None
            self.create_login_layout(parent_layout)  # Добавляем layout для login непосредственно

    def registration(self, parent_layout):
        pass


class MyApp(App):
    token = None
    token_check = None  # Добавляем атрибут для отслеживания времени истечения токена

    def build(self):
        base_gridlayout = GridLayout(rows=2, spacing=3)

        nav_gridlayout_onbase = GridLayout(cols=5, spacing=3, size_hint_y=0.10)

        main_button = Button(text='Главная')
        main_button.bind(on_press=self.show_main)
        nav_gridlayout_onbase.add_widget(main_button)

        nav_gridlayout_onbase.add_widget(Button(text='Курсы'))

        nav_gridlayout_onbase.add_widget(Button(text='Группа'))
        nav_gridlayout_onbase.add_widget(Widget())

        self.auth_instance = Auth()
        auth_button = Button(text='Auth')
        auth_button.bind(on_press=self.show_auth)
        nav_gridlayout_onbase.add_widget(auth_button)

        mainpage_onbase = GridLayout(cols=2, spacing=3, size_hint_y=0.90)

        left_nav_mainpage_onbase = GridLayout(rows=50, spacing=3, size_hint_x=0.20)
        left_nav_mainpage_onbase.add_widget(Button(text='Hi 1'))
        left_nav_mainpage_onbase.add_widget(Button(text='Hi 2'))
        central_mainpage_onbase = GridLayout(rows=1)

        self.central_mainpage_onbase = central_mainpage_onbase

        mainpage_onbase.add_widget(left_nav_mainpage_onbase)
        mainpage_onbase.add_widget(central_mainpage_onbase)

        base_gridlayout.add_widget(nav_gridlayout_onbase)
        base_gridlayout.add_widget(mainpage_onbase)

        return base_gridlayout

    def show_auth(self, instance):
        self.central_mainpage_onbase.clear_widgets()  # Очистить предыдущие виджеты
        self.auth_instance.check_token(self.central_mainpage_onbase)

    def show_main(self, instance):
        self.central_mainpage_onbase.clear_widgets()


def on_start(self):
    # Инициализация токена и времени его истечения
    self.token = {'access_token': 'your_token', 'token_type': 'your_type'}
    # Инициализация словаря для проверки токена
    self.token_check = {'access_token': 'your_token', 'token_type': 'your_type',
                        'expiry': datetime.now() + timedelta(seconds=3600)}


if __name__ == '__main__':
    MyApp().run()
