import json
from typing import Any
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

    def show_popup_success_reg(self):
        self.show_popup('Успех', 'Вы успешно зарегистрировались в системе')

    def show_popup_success_logout(self):
        self.show_popup('Успех', 'Вы успешно вышли из системы')

    def show_popup_update_people(self):
        self.show_popup('Успех', 'Вы успешно обновили данные профиля')

    def show_popup_create_people(self):
        self.show_popup('Успех', 'Вы успешно создали профиль')

    def show_popup_error(self, error_message):
        self.show_popup('Ошибка', error_message)


notification_manager = NotificationManager()  # создаем экземпляр класса уведомлений


class Auth(GridLayout):
    def __init__(self, **kwargs):
        super(Auth, self).__init__(**kwargs)

    def create_logout_layout(self, parent_layout, data):

        if data['first_name'] != '':
            first_name = data['first_name']
            last_name = data['last_name']
            age = data['age']
            pk = data['pk']
            save_button = Button(text='Обновить данные профиля', size_hint_x=0.5, pos_hint={'center_x': 0.5})
            save_button.bind(on_press=partial(self.update_people, parent_layout=parent_layout, pk=pk))
        else:
            first_name = ''
            last_name = ''
            age = 0
            save_button = Button(text='Сохранить данные профиля', size_hint_x=0.5, pos_hint={'center_x': 0.5})
            save_button.bind(on_press=partial(self.create_people, parent_layout=parent_layout))



        login_layout = BoxLayout(orientation='vertical')
        login_layout.clear_widgets()  # Очищаем родительский layout
        login_layout.add_widget(Label(text='Вы уже вошли в систему'))
        if data['first_name'] != '':
            login_layout.add_widget(Label(text='Данные пользователя'))
        else:
            login_layout.add_widget(Label(text='Введите Ваши данные (требуется для записи на курсы'),
                                    text_size=(200, None), halign='center')

        login_layout.add_widget(Widget())

        login_layout.add_widget(Label(text='Имя'))
        self.firstname_input = TextInput(text=f'{first_name}', size_hint_x=0.5, multiline=False,
                                         pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.firstname_input)

        login_layout.add_widget(Label(text='Фамилия'))
        self.lastname_input = TextInput(text=f'{last_name}', size_hint_x=0.5, multiline=False,
                                        pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.lastname_input)

        login_layout.add_widget(Label(text='Возраст'))
        self.age_input = TextInput(text=f'{age}', size_hint_x=0.5, multiline=False, pos_hint={'center_x': 0.5})
        login_layout.add_widget(self.age_input)
        login_layout.add_widget(Widget())

        login_layout.add_widget(save_button)

        logout_button = Button(text='Выход из системы', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        logout_button.bind(on_press=partial(self.logout, parent_layout=parent_layout))
        login_layout.add_widget(logout_button)

        logout_button_closed = Button(text='Закрыть окно профиля', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        logout_button_closed.bind(on_press=partial(self.closed, parent_layout=parent_layout))
        login_layout.add_widget(logout_button_closed)

        parent_layout.clear_widgets()
        parent_layout.add_widget(login_layout)

    def closed(self, instance, parent_layout):

        parent_layout.clear_widgets()

    def update_people(self, instance, parent_layout, pk):
        token = App.get_running_app().token
        if token:
            user_url = f'http://127.0.0.1:8000/people/update/{pk}'
            headers = {'Authorization': f'Bearer {token}', 'accept': 'application/json'}

            first_name = self.firstname_input.text.strip()
            last_name = self.lastname_input.text.strip()
            age = self.age_input.text.strip()
            request_data = json.dumps({
                'first_name': first_name,
                'last_name': last_name,
                'age': age,
            })

            parent_layout.clear_widgets()
            UrlRequest(user_url, method='PUT', req_body=request_data, req_headers=headers,
                       on_success=self.on_update_people_success, on_failure=self.on_update_people_failure)

    def on_update_people_success(self, request, result):
        # Сохранение токена аутентификации и переход к экрану курсов
        notification_manager.show_popup_update_people()

    def on_update_people_failure(self, request, result):
        msg = result['detail'][0]['msg']
        message = f'Ошибка обновления профиля: {msg}'
        notification_manager.show_popup_error(message)

    def create_people(self, instance, parent_layout):

        token = App.get_running_app().token
        if token:
            create_people_url = 'http://127.0.0.1:8000/people/'
            headers = {'Authorization': f'Bearer {token}', 'accept': 'application/json'}

            first_name = self.firstname_input.text.strip()
            last_name = self.lastname_input.text.strip()
            age = self.age_input.text.strip()

            request_data = json.dumps({
                'first_name': first_name,
                'last_name': last_name,
                'age': age,
            })

            parent_layout.clear_widgets()

            UrlRequest(create_people_url, method='POST', req_body=request_data, req_headers=headers,
                       on_success=self.on_create_people_success,
                       on_failure=self.create_people_failure)

    def on_create_people_success(self, request, result):
        # Сохранение токена аутентификации и переход к экрану курсов
        notification_manager.show_popup_create_people()

    def create_people_failure(self, request, result):
        msg = result['detail'][0]['msg']
        message = f'Ошибка создания профиля: {msg}'
        notification_manager.show_popup_error(message)




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
        msg = result['detail'][0]['msg']
        message = f'Ошибка аутентификации(некорректные данные или пользователя не существует): {msg}'
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

    def logout(self, instance, parent_layout):
        # Получаем текущий токен
        token = App.get_running_app().token
        if token:
            logout_url = 'http://127.0.0.1:8000/api/v1/auth/logout'
            headers = {'Authorization': f'Bearer {token}', 'accept': 'application/json'}

            parent_layout.clear_widgets()
            # Используем POST-запрос для выхода из системы
            UrlRequest(logout_url, method='POST', req_headers=headers, on_success=self.on_logout_success,
                       on_failure=self.on_logout_failure)

    def on_logout_success(self, request, result):
        # Сброс токена после успешного выхода из системы
        App.get_running_app().token = None
        App.get_running_app().token_check = None
        notification_manager.show_popup_success_logout()
        # Обновление вкладки аутентификации

    def on_logout_failure(self, request, result):
        msg = result['detail'][0]['msg']
        message = f'Ошибка при выходе из системы: {msg}'
        notification_manager.show_popup_error(message)

    def check_token(self, parent_layout):
        token_check = App.get_running_app().token_check

        if token_check and token_check['access_token'] != 'your_token' and (datetime.now() < token_check['expiry']):
            self.check_profile('out', lambda data: self.create_logout_layout(parent_layout, data))
        else:
            App.get_running_app().token = None
            App.get_running_app().token_check = None
            self.create_login_layout(parent_layout)  # Добавляем layout для login непосредственно

    # def check_token(self, parent_layout):
    #     token_check = App.get_running_app().token_check
    #
    #     if token_check and token_check['access_token'] != 'your_token' and (datetime.now() < token_check['expiry']):
    #         self.check_profile('out', lambda data: self.create_logout_layout(parent_layout, data))
    #     else:
    #         App.get_running_app().token = None
    #         App.get_running_app().token_check = None
    #         self.create_login_layout(parent_layout)  # Добавляем layout для login непосредственно

    def check_profile(self, type, callback=None):  # callback заставляет асинхронщиу дожидаться ответа по функции
        if isinstance(type, str):
            token = App.get_running_app().token
            if token:
                user_url = 'http://127.0.0.1:8000/api/v1/auth/me'
                headers = {'Authorization': f'Bearer {token}'}
                UrlRequest(user_url, req_headers=headers,
                           on_success=lambda req, res: self.on_check_profile_success(req, res, callback),
                           on_failure=self.on_check_profile_failure)
        else:
            return type

    def on_check_profile_failure(self, request, result):
        msg = result['detail'][0]['msg']
        message = f'Ошибка: {msg}'
        notification_manager.show_popup_error(message)

    def on_check_profile_success(self, request, result, callback=None):
        pk = result['id']
        token = App.get_running_app().token
        if token:
            profile_url = f'http://127.0.0.1:8000/people/{pk}'
            headers = {'Authorization': f'Bearer {token}'}
            # Добавляем параметр on_redirect для обработки перенаправлений
            UrlRequest(profile_url, req_headers=headers,
                       on_success=lambda req, res: self.on_people_success(req, pk, res, callback),
                       on_failure=lambda req, res: self.on_people_failure(req, pk, res, callback))
        else:
            if callback:
                callback(result)

    def on_people_success(self, request, pk, result, callback=None):
        data = {'first_name': result['first_name'],
                'last_name': result['last_name'],
                'age': result['age'],
                'pk': pk,
                }
        if callback:
            callback(data)

    def on_people_failure(self, request, pk, result, callback=None):
        data = {'first_name': '',
                'last_name': '',
                'age': '',
                'pk': pk,
                }
        if callback:
            callback(data)

    def registration(self, instance, parent_layout):
        email = self.reg_username_input.text.strip()
        password = self.reg_password_input.text.strip()
        password2 = self.reg_password_input2.text.strip()
        if password == password2:
            reg_url = 'http://127.0.0.1:8000/api/v1/auth/register'
            request_data = json.dumps({
                'email': email,
                'password': password,
                'is_active': True,
                'is_superuser': False,
                'is_verified': False
            })
            headers = {'Content-type': 'application/json'}
            parent_layout.clear_widgets()
            UrlRequest(reg_url, req_body=request_data, req_headers=headers,
                       on_success=lambda req, res: self.on_reg_success(req, res, password),
                       on_failure=self.on_reg_failure)
        else:
            message = 'Введенные пароли не одинаковые:'
            notification_manager.show_popup_error(message)

    def on_reg_failure(self, request, result):
        msg = result['detail'][0]['msg']
        message = f'Ошибка регистрации: {msg}'
        notification_manager.show_popup_error(message)

    def on_reg_success(self, request, result, password):
        login_url = 'http://127.0.0.1:8000/api/v1/auth/login'
        request_data = urlencode({
            'username': result['email'],
            'password': password
        })
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        UrlRequest(login_url, req_body=request_data, req_headers=headers,
                   on_success=self.on_login_success, on_failure=self.on_login_failure)
        notification_manager.show_popup_success_reg()

class Courses(GridLayout):
    def __init__(self, **kwargs):
        super(Courses, self).__init__(**kwargs)

    def check_token(self, parent_layout):
        token_check = App.get_running_app().token_check

        if token_check and token_check['access_token'] != 'your_token' and (datetime.now() < token_check['expiry']):
            pass
        else:
            App.get_running_app().token = None
            App.get_running_app().token_check = None
            pass



class MyApp(App):
    token = None
    token_check = None  # Добавляем атрибут для отслеживания времени истечения токена

    data = {'first_name': '',  # данные для профиля по умолчанию
            'last_name': '',
            'age': 0,
            }

    def build(self):
        base_gridlayout = GridLayout(rows=2, spacing=3)

        nav_gridlayout_onbase = GridLayout(cols=5, spacing=3, size_hint_y=0.10)

        main_button = Button(text='Главная')
        main_button.bind(on_press=self.show_main)
        nav_gridlayout_onbase.add_widget(main_button)


        self.courses_instance = Courses()
        courses_button = Button(text='Курсы')
        courses_button.bind(on_press=self.show_courses)
        nav_gridlayout_onbase.add_widget(courses_button)



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
        self.left_nav_mainpage_onbase = left_nav_mainpage_onbase

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

    def show_courses(self, instance):
        self.central_mainpage_onbase.clear_widgets()  # Очистить предыдущие виджеты
        self.courses_instance.check_token(self.central_mainpage_onbase)

def on_start(self):
    # Инициализация токена и времени его истечения
    self.token = {'access_token': 'your_token', 'token_type': 'your_type'}
    # Инициализация словаря для проверки токена
    self.token_check = {'access_token': 'your_token', 'token_type': 'your_type',
                        'expiry': datetime.now() + timedelta(seconds=3600)}


if __name__ == '__main__':
    MyApp().run()
