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
from kivy.uix.scrollview import ScrollView
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

    def show_popup_order_courses(self):
        self.show_popup('Успех', 'Вы успешно записались на курсы')

    def show_popup_order_courses_and_groups(self):
        self.show_popup('Успех', 'Вы успешно зачислены в группу')

    def show_popup_error(self, error_message):
        self.show_popup('Ошибка', error_message)


notification_manager = NotificationManager()  # создаем экземпляр класса уведомлений


class Auth(GridLayout):
    def __init__(self, app, **kwargs):
        super(Auth, self).__init__(**kwargs)
        self.app = app

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
            label1 = Label(text='Введите Ваши данные (требуется для записи на курсы)', text_size=(400, None),
                           halign='center')
            login_layout.add_widget(label1)

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
        msg = result['detail']
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
        msg = result['detail']
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
        self.app.current_user_email = username
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        parent_layout.clear_widgets()
        UrlRequest(login_url, req_body=request_data, req_headers=headers,
                   on_success=self.on_login_success, on_failure=self.on_login_failure)

    def on_login_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка аутентификации(некорректные данные или пользователя не существует)'
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

        self.app.on_auth_success(None)
        self.app.change_button_name(None, 'Профиль')

        notification_manager.show_popup_success_login()

        token = App.get_running_app().token
        if token:
            profile_url = f'http://127.0.0.1:8000/people/check'
            headers = {'Authorization': f'Bearer {token}'}
            # Добавляем параметр on_redirect для обработки перенаправлений
            UrlRequest(profile_url, req_headers=headers,
                       on_success=self.on_check_success,
                       on_failure=self.on_check_failure)

    def on_check_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка связи с севером: {msg}'
        notification_manager.show_popup_error(message)
        # print('Ошибка аутентификации:', request.resp_status, result)

    def on_check_success(self, request, result):

        if result['courses_and_groups_check']['check_group'] is True:
            self.app.on_group_success(None)

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

        self.app.hide_button_on_logout(None)  # убираем кнпоки при выходе

        notification_manager.show_popup_success_logout()
        # Обновление вкладки аутентификации

    def on_logout_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка при выходе из системы: {msg}'
        notification_manager.show_popup_error(message)

    def check_token(self, parent_layout, left_layout):
        token_check = App.get_running_app().token_check
        left_layout.clear_widgets()

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
        msg = result['detail']
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
        msg = result['detail']
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
    def __init__(self, app, **kwargs):
        super(Courses, self).__init__(**kwargs)
        self.app = app

    def check_token(self, parent_layout, left_layout):
        parent_layout.clear_widgets()
        left_layout.clear_widgets()

        token_check = App.get_running_app().token_check

        if token_check and token_check['access_token'] != 'your_token' and (datetime.now() < token_check['expiry']):
            self.check_courses(parent_layout, left_layout)
        else:
            App.get_running_app().token = None
            App.get_running_app().token_check = None

            message = 'Для просмотра курсов войдите в систему. Если не зарегистрированы- зарегистрируйтесь!'
            notification_manager.show_popup_error(message)

    def check_courses(self, parent_layout, left_layout):

        token = App.get_running_app().token

        courses_url = 'http://127.0.0.1:8000/courses'
        headers = {'Authorization': f'Bearer {token}'}
        # Добавляем параметр on_redirect для обработки перенаправлений
        UrlRequest(courses_url, req_headers=headers,
                   on_success=lambda req, res: self.on_courses_success(req, res, parent_layout, left_layout),
                   on_redirect=lambda req, res: self.on_redirect(req, res, parent_layout, left_layout))

    def on_redirect(self, request, result, parent_layout, left_layout):
        # # Логируем все заголовки ответа
        # print('Заголовки ответа:', request.resp_headers)
        # Пытаемся получить URL для перенаправления с учетом регистра
        redirect_url = request.resp_headers.get('location')  # Используйте 'location' в нижнем регистре
        # print('URL для перенаправления:', redirect_url)

        if redirect_url:
            token = App.get_running_app().token
            headers = {'Authorization': f'Bearer {token}'}
            UrlRequest(redirect_url, req_headers=headers,
                       on_success=lambda req, res: self.on_courses_success(req, res, parent_layout, left_layout),
                       on_failure=self.on_courses_failure)
        else:
            print('Ошибка: Заголовок Location отсутствует в ответе.')

    def on_courses_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка: {msg}'
        notification_manager.show_popup_error(message)

    def on_courses_success(self, request, result, parent_layout, left_layout):
        parent_layout.clear_widgets()
        left_layout.clear_widgets()
        courses_name_layout = BoxLayout(orientation='vertical')

        for course in result:
            temp_text = course['name']
            temp_id = course['id']
            courses_name = Button(text=temp_text)
            courses_name.bind(
                on_press=partial(self.course_description, temp_id=temp_id, result=result, parent_layout=parent_layout))
            courses_name_layout.add_widget(courses_name)

        left_layout.add_widget(courses_name_layout)

    def course_description(self, instance, temp_id, result, parent_layout):
        parent_layout.clear_widgets()
        courses_description_layout = BoxLayout(orientation='vertical')
        for i in range(len(result)):
            if temp_id == result[i]['id']:
                name = 'Название курсов:' + result[i]['name']
                description = result[i]['description']
                price = result[i]['price']
                price = 'Ориентировочная цена за курсы:' + str(price) + '.00 белорусских рублей'
                true_id = result[i]['id']

        label_name = Label(text=name, text_size=(400, None),
                           halign='center')
        label_description = Label(text=description, text_size=(400, None),
                                  halign='center')
        label_price = Label(text=price, text_size=(400, None),
                            halign='center')
        courses_description_layout.add_widget(label_name)
        courses_description_layout.add_widget(Widget())
        courses_description_layout.add_widget(label_description)
        courses_description_layout.add_widget(Widget())
        courses_description_layout.add_widget(label_price)

        courses_order = Button(text='Записаться на курсы')
        courses_order.bind(
            on_press=partial(self.course_order, true_id=true_id, result=result, parent_layout=parent_layout))
        courses_description_layout.add_widget(courses_order)

        parent_layout.add_widget(courses_description_layout)

    def course_order(self, instance, true_id, result, parent_layout):

        token = App.get_running_app().token
        if token:
            profile_url = f'http://127.0.0.1:8000/peoplecoursesassociation/{true_id}'
            headers = {'Authorization': f'Bearer {token}'}
            courses_id = true_id
            request_data = json.dumps({
                'courses_id': courses_id
            })
            # Добавляем параметр on_redirect для обработки перенаправлений
            UrlRequest(profile_url, method='POST', req_headers=headers, req_body=request_data,
                       on_success=lambda req, res: self.on_course_order_success_and_add_groups(req, res, courses_id),
                       on_failure=self.on_course_order_failure)

    def on_course_order_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка записи на курсы: {msg}'
        notification_manager.show_popup_error(message)

    def on_course_order_success_and_add_groups(self, request, result, courses_id):

        notification_manager.show_popup_order_courses()
        token = App.get_running_app().token
        if token:
            url = f'http://127.0.0.1:8000/peoplegroupesassociation/'
            headers = {'Authorization': f'Bearer {token}'}

            request_data = json.dumps({
                'courses_id': courses_id
            })
            # Добавляем параметр on_redirect для обработки перенаправлений
            UrlRequest(url, method='POST', req_headers=headers, req_body=request_data,
                       on_success=self.on_course_order_success_all,
                       on_failure=self.on_course_order_failure_all)

    def on_course_order_failure_all(self, request, result):
        msg = result['detail']
        message = f'Ошибка записи в группу: {msg}'
        notification_manager.show_popup_error(message)

    def on_course_order_success_all(self, request, result):
        self.app.on_group_success(None)
        notification_manager.show_popup_order_courses_and_groups()


class Groups(GridLayout):
    def __init__(self, app, **kwargs):
        super(Groups, self).__init__(**kwargs)
        self.app = app
        self.update_event = None

    def check_token(self, parent_layout, left_layout):
        parent_layout.clear_widgets()
        left_layout.clear_widgets()

        token_check = App.get_running_app().token_check

        if token_check and token_check['access_token'] != 'your_token' and (datetime.now() < token_check['expiry']):
            self.check_groups(parent_layout, left_layout)
        else:
            App.get_running_app().token = None
            App.get_running_app().token_check = None

    def check_groups(self, parent_layout, left_layout):

        token = App.get_running_app().token

        url = 'http://127.0.0.1:8000/peoplegroupesassociation/check'
        headers = {'Authorization': f'Bearer {token}'}
        # Добавляем параметр on_redirect для обработки перенаправлений
        UrlRequest(url, req_headers=headers,
                   on_success=lambda req, res: self.on_groups_success(req, res, parent_layout, left_layout),
                   on_redirect=lambda req, res: self.on_groups_redirect(req, res, parent_layout, left_layout))

    def on_groups_redirect(self, request, result, parent_layout, left_layout):

        redirect_url = request.resp_headers.get('location')  # Используйте 'location' в нижнем регистре
        # print('URL для перенаправления:', redirect_url)

        if redirect_url:
            token = App.get_running_app().token
            headers = {'Authorization': f'Bearer {token}'}
            UrlRequest(redirect_url, req_headers=headers,
                       on_success=lambda req, res: self.on_groups_success(req, res, parent_layout, left_layout),
                       on_failure=self.on_groups_failure)
        else:
            print('Ошибка: Заголовок Location отсутствует в ответе.')

    def on_groups_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка при загрузке данных по группам: {msg}'
        notification_manager.show_popup_error(message)

    def on_groups_success(self, request, result, parent_layout, left_layout):
        parent_layout.clear_widgets()
        left_layout.clear_widgets()
        groups_name_layout = BoxLayout(orientation='vertical')
        groups_name_layout.add_widget(Label(text='Вы учитесь в:'))

        for group in result:
            temp_text = group['name']
            temp_id = group['id']
            groups_button = Button(text=temp_text)
            groups_button.bind(
                on_press=partial(self.groupe_in, temp_id=temp_id, result=result, left_layout=left_layout,
                                 parent_layout=parent_layout))
            groups_name_layout.add_widget(groups_button)
            groups_name_layout.add_widget(Widget())

        groups_name_layout.add_widget(Widget())
        left_layout.add_widget(groups_name_layout)

    def groupe_in(self, instance, temp_id, result, left_layout, parent_layout):
        left_layout.clear_widgets()
        for group in result:
            if group['id'] == temp_id:
                name = group['name']
                break
        groups_name_layout = BoxLayout(orientation='vertical')

        label1 = Label(text=name, text_size=(60, None),
                       halign='center')

        temp_groupe_val = result
        temp_id_val = temp_id

        groups_name_layout.add_widget(label1)

        chat_button = Button(text='Чат')
        chat_button.bind(
            on_press=partial(self.open_chat, temp_id_val=temp_id_val, temp_groupe_val=temp_groupe_val,
                             left_layout=left_layout,
                             parent_layout=parent_layout))
        groups_name_layout.add_widget(Widget())
        groups_name_layout.add_widget(chat_button)

        lection_button = Button(text='Лекции')
        lection_button.bind(
            on_press=partial(self.open_lection, temp_id_val=temp_id_val, temp_groupe_val=temp_groupe_val,
                             left_layout=left_layout,
                             parent_layout=parent_layout))
        groups_name_layout.add_widget(Widget())
        groups_name_layout.add_widget(lection_button)

        back_button = Button(text='Назад')
        back_button.bind(
            on_press=self.app.show_groups)
        groups_name_layout.add_widget(Widget())
        groups_name_layout.add_widget(back_button)

        left_layout.add_widget(groups_name_layout)

    def start_chat_updates(self, instance, temp_id, temp_id_val, temp_groupe_val, chat_text_layout, parent_layout):
        def update_chat(*args):
            self.open_chat_full(instance, temp_id, temp_id_val, temp_groupe_val, chat_text_layout, parent_layout)

        # Останавливаем предыдущую задачу, если она была
        if self.update_event:
            Clock.unschedule(self.update_event)

        # Запускаем новую задачу
        self.update_event = Clock.schedule_interval(update_chat, 4)

    def stop_chat_update(self, go_back=False, temp_id=None, result=None, left_layout=None, parent_layout=None):
        if self.update_event:
            Clock.unschedule(self.update_event)
            self.update_event = None

        # Если требуется вернуться в предыдущее меню
        if go_back:
            self.groupe_in(instance=None, temp_id=temp_id, result=result, left_layout=left_layout,
                           parent_layout=parent_layout)

    def open_chat(self, instance, temp_id_val, temp_groupe_val, left_layout, parent_layout):
        left_layout.clear_widgets()

        chat_layout = BoxLayout(orientation='vertical')
        chat_layout.add_widget(Widget())

        back_button2 = Button(text='Назад')
        back_button2.bind(on_press=lambda x: self.stop_chat_update(go_back=True, temp_id=temp_id_val,
                                                                   result=temp_groupe_val, left_layout=left_layout,
                                                                   parent_layout=parent_layout))
        chat_layout.add_widget(back_button2)
        left_layout.add_widget(chat_layout)

        chat_main_layout = GridLayout(rows=2, spacing=3)

        chat_text_layout = BoxLayout(orientation='vertical', size_hint_y=0.70)
        chat_input_layout = BoxLayout(orientation='vertical', size_hint_y=0.30)


        self.message_input = TextInput(multiline=True)
        chat_input_layout.add_widget(self.message_input)
        message_button = Button(text='Отправить сообщение')
        message_button.bind(on_press=partial(self.add_message, temp_id_val=temp_id_val, temp_groupe_val=temp_groupe_val,
                                             left_layout=left_layout, parent_layout=parent_layout))
        chat_input_layout.add_widget(message_button)

        chat_main_layout.add_widget(chat_text_layout)
        chat_main_layout.add_widget(chat_input_layout)

        parent_layout.add_widget(chat_main_layout)

        # Запускаем обновления чата
        self.start_chat_updates(instance, temp_id_val, temp_id_val, temp_groupe_val, chat_text_layout, parent_layout)

    def open_chat_full(self, instance, temp_id, temp_id_val, temp_groupe_val, chat_text_layout,
                       parent_layout):

        token = App.get_running_app().token
        pk = temp_id_val
        url = f'http://127.0.0.1:8000/chat/{pk}'
        headers = {'Authorization': f'Bearer {token}'}

        UrlRequest(url, req_headers=headers,
                   on_success=lambda req, res: self.on_open_chat_success(req, res, temp_id_val, temp_groupe_val,
                                                                         chat_text_layout, parent_layout),
                   on_failure=lambda req, res: self.on_open_chat_failure(req, res, temp_id_val, temp_groupe_val,
                                                                         chat_text_layout, parent_layout))

    def on_open_chat_failure(self, request, result, temp_id_val, temp_groupe_val, chat_text_layout, parent_layout):
        # Пустой result для случая, когда нет сообщений
        self.on_open_chat_success(request=request, result=None, temp_id_val=temp_id_val,
                                  temp_groupe_val=temp_groupe_val, chat_text_layout=chat_text_layout,
                                  parent_layout=parent_layout)

    def on_open_chat_success(self, request, result, temp_id_val, temp_groupe_val, chat_text_layout, parent_layout):
        # parent_layout.clear_widgets()

        chat_text_layout.clear_widgets()

        chat_layout = BoxLayout(orientation='vertical')
        chat_screen_layout = ScrollView(size_hint_y=0.8)

        messages_container = BoxLayout(orientation='vertical', size_hint_y=None)
        messages_container.bind(minimum_height=messages_container.setter('height'))

        if result:
            for chat in result:
                temp_content = chat['content']
                temp_user_id = chat['user']['email']
                temp_timestamp = chat['timestamp']

                prefix = 'Сообщение от ' + str(temp_user_id) + ' в ' + temp_timestamp

                # Определяем, слева или справа будет сообщение
                if temp_user_id == self.app.current_user_email:
                    halign = 'left'
                else:
                    halign = 'right'

                label_prefix = Label(
                    text=prefix,
                    size_hint_y=None,
                    height=20,  # Высота уменьшена для меньшего шрифта
                    font_size=10,  # Меньший размер шрифта для prefix
                    color=(1, 1, 0, 1),
                    halign=halign,
                    valign='top'
                )
                label_prefix.bind(size=label_prefix.setter('text_size'))

                label_message = Label(
                    text=temp_content,
                    size_hint_y=None,
                    height=30,
                    font_size=16,
                    halign=halign,
                    valign='middle'
                )
                label_message.bind(size=label_message.setter('text_size'))

                # Создаем вертикальный BoxLayout для выравнивания
                message_box = BoxLayout(orientation='vertical', size_hint_y=None, height=50, padding=5)
                message_box.add_widget(label_prefix)
                message_box.add_widget(label_message)

                # Создаем горизонтальный BoxLayout для выравнивания слева или справа
                alignment_box = BoxLayout(size_hint_y=None, height=50, padding=5)
                if halign == 'left':
                    alignment_box.add_widget(message_box)
                    alignment_box.add_widget(Widget())
                else:
                    alignment_box.add_widget(Widget())
                    alignment_box.add_widget(message_box)

                messages_container.add_widget(alignment_box)
        else:
            # Добавляем сообщение о том, что чат пуст
            empty_label = Label(
                text="Чат пока пуст. Будьте первым, кто отправит сообщение!",
                size_hint_y=None,
                height=30,
                font_size=16,
                halign='center',
                valign='middle'
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            messages_container.add_widget(empty_label)

        chat_screen_layout.add_widget(messages_container)
        chat_layout.add_widget(chat_screen_layout)
        chat_text_layout.add_widget(chat_layout)
        self.scroll_to_bottom(chat_screen_layout)

    def scroll_to_bottom(self, scroll_view):
        scroll_view.scroll_y = 0


    def add_message(self, instance, temp_id_val, temp_groupe_val, left_layout, parent_layout):

        temp_message = self.message_input.text.strip()
        self.message_input.text = ''
        token = App.get_running_app().token

        url = 'http://127.0.0.1:8000/chat/'
        headers = {'Authorization': f'Bearer {token}'}

        request_data = json.dumps({
            'content': temp_message,
            'groups_id': temp_id_val,

        })

        UrlRequest(url, method='POST', req_headers=headers, req_body=request_data)


    def open_lection(self, instance, temp_id_val, temp_groupe_val, left_layout, parent_layout):

        left_layout.clear_widgets()
        token = App.get_running_app().token

        url = 'http://127.0.0.1:8000/lessons/list'
        headers = {'Authorization': f'Bearer {token}'}

        request_data = json.dumps({
            'id': temp_id_val
        })

        UrlRequest(url, method='POST', req_headers=headers, req_body=request_data,
                   on_success=lambda req, res: self.on_open_lection_success(req, res, temp_groupe_val, temp_id_val,
                                                                            left_layout, parent_layout),
                   on_failure=self.on_open_lection_failure)

    def on_open_lection_failure(self, request, result):
        msg = result['detail']
        message = f'Ошибка при загрузке данных по лекциям: {msg}'
        notification_manager.show_popup_error(message)

    def on_open_lection_success(self, request, result, temp_groupe_val, temp_id_val, left_layout, parent_layout):
        parent_layout.clear_widgets()
        left_layout.clear_widgets()
        groups_name_layout = BoxLayout(orientation='vertical')
        groups_name_layout.add_widget(Label(text='Лекции'))

        for lesson in result:
            temp_text = lesson['title']
            temp_id = lesson['id']
            lesson_button = Button(text=temp_text)
            lesson_button.bind(
                on_press=partial(self.lesson_description, temp_id=temp_id, result=result, left_layout=left_layout,
                                 parent_layout=parent_layout))
            groups_name_layout.add_widget(lesson_button)
            groups_name_layout.add_widget(Widget())

        back_button2 = Button(text='Назад')
        temp_id = temp_id_val
        back_button2.bind(
            on_press=partial(self.groupe_in, temp_id=temp_id, result=temp_groupe_val, left_layout=left_layout,
                             parent_layout=parent_layout))
        groups_name_layout.add_widget(Widget())
        groups_name_layout.add_widget(back_button2)

        left_layout.add_widget(groups_name_layout)

    def lesson_description(self, instance, temp_id, result, left_layout, parent_layout):

        parent_layout.clear_widgets()
        courses_description_layout = BoxLayout(orientation='vertical')
        for i in range(len(result)):
            if temp_id == result[i]['id']:
                name = 'Лекция:' + result[i]['title']
                description = result[i]['document_path']
                true_id = result[i]['id']
                break

        label_name = Label(text=name, text_size=(400, None),
                           halign='center')
        label_description = Label(text=description, text_size=(400, None),
                                  halign='center')

        courses_description_layout.add_widget(label_name)
        courses_description_layout.add_widget(Widget())
        courses_description_layout.add_widget(label_description)
        courses_description_layout.add_widget(Widget())

        parent_layout.add_widget(courses_description_layout)


class MyApp(App):
    token = None
    token_check = None  # Добавляем атрибут для отслеживания времени истечения токена

    data = {'first_name': '',  # данные для профиля по умолчанию
            'last_name': '',
            'age': 0,
            }

    current_user_email = 'user1@example.com'  # Email текущего пользователя

    def build(self):
        self.base_gridlayout = GridLayout(rows=2, spacing=3)

        self.nav_gridlayout_onbase = GridLayout(cols=5, spacing=3, size_hint_y=0.10)

        self.main_button = Button(text='Главная')
        self.main_button.bind(on_press=self.show_main)
        self.nav_gridlayout_onbase.add_widget(self.main_button)

        self.courses_instance = Courses(app=self)
        self.courses_button = Button(text='Курсы')
        self.courses_button.bind(on_press=self.show_courses)
        self.nav_gridlayout_onbase.add_widget(self.courses_button)
        self.courses_button.opacity = 0
        self.courses_button.disabled = True

        self.group_instance = Groups(app=self)
        self.group_button = Button(text='Группа')
        self.group_button.bind(on_press=self.show_groups)
        self.nav_gridlayout_onbase.add_widget(self.group_button)
        self.group_button.opacity = 0
        self.group_button.disabled = True

        self.nav_gridlayout_onbase.add_widget(Widget())
        # Создаем экземпляр Auth, передавая ссылку на текущий экземпляр MyApp
        self.auth_instance = Auth(app=self)

        self.auth_button = Button(text='Вход/Регист')
        self.auth_button.bind(on_press=self.show_auth)
        self.nav_gridlayout_onbase.add_widget(self.auth_button)

        self.mainpage_onbase = GridLayout(cols=2, spacing=3, size_hint_y=0.90)

        left_nav_mainpage_onbase = GridLayout(rows=1, spacing=3, size_hint_x=0.20)

        central_mainpage_onbase = GridLayout(rows=1)

        self.central_mainpage_onbase = central_mainpage_onbase
        self.left_nav_mainpage_onbase = left_nav_mainpage_onbase

        self.mainpage_onbase.add_widget(left_nav_mainpage_onbase)
        self.mainpage_onbase.add_widget(central_mainpage_onbase)

        self.base_gridlayout.add_widget(self.nav_gridlayout_onbase)
        self.base_gridlayout.add_widget(self.mainpage_onbase)

        return self.base_gridlayout

    def show_auth(self, instance):
        self.central_mainpage_onbase.clear_widgets()  # Очистить предыдущие виджеты
        self.auth_instance.check_token(self.central_mainpage_onbase, self.left_nav_mainpage_onbase)
        if self.group_instance:
            self.group_instance.stop_chat_update()  # Остановка обновлений

    def show_main(self, instance):
        self.central_mainpage_onbase.clear_widgets()
        self.left_nav_mainpage_onbase.clear_widgets()

    def show_courses(self, instance):
        self.central_mainpage_onbase.clear_widgets()  # Очистить предыдущие виджеты
        self.left_nav_mainpage_onbase.clear_widgets()
        self.courses_instance.check_token(self.central_mainpage_onbase, self.left_nav_mainpage_onbase)
        if self.group_instance:
            self.group_instance.stop_chat_update()  # Остановка обновлений

    def show_groups(self, instance):
        self.left_nav_mainpage_onbase.clear_widgets()
        self.central_mainpage_onbase.clear_widgets()  # Очистить предыдущие виджеты
        self.group_instance.check_token(self.central_mainpage_onbase, self.left_nav_mainpage_onbase)
        if self.group_instance:
            self.group_instance.stop_chat_update()  # Остановка обновлений

    def on_auth_success(self, instance):
        # Вызывается после успешной авторизации
        self.courses_button.opacity = 1
        self.courses_button.disabled = False

    def on_group_success(self, instance):
        self.group_button.opacity = 1
        self.group_button.disabled = False

    def change_button_name(self, instance, name):
        self.auth_button.text = name

    def hide_button_on_logout(self, instance):
        self.auth_button.text = 'Вход/Регист'
        self.group_button.opacity = 0
        self.group_button.disabled = True
        self.group_button.opacity = 0
        self.group_button.disabled = True


def on_start(self):
    # Инициализация токена и времени его истечения
    self.token = {'access_token': 'your_token', 'token_type': 'your_type'}
    # Инициализация словаря для проверки токена
    self.token_check = {'access_token': 'your_token', 'token_type': 'your_type',
                        'expiry': datetime.now() + timedelta(seconds=3600)}

    # self.current_user_email = current_user_email


if __name__ == '__main__':
    MyApp().run()
