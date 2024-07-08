import json
from urllib.parse import urlencode
from datetime import datetime, timedelta
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelStrip


class AuthTab(TabbedPanelItem):
    def __init__(self, **kwargs):
        super(AuthTab, self).__init__(**kwargs)
        self.text = 'Auth'
        self.check_token()

    # def on_touch_down(self, touch):
    #     if self.collide_point(*touch.pos):
    #         # Получаем родительский объект TabbedPanel
    #         tabbed_panel = self.parent
    #         while not isinstance(tabbed_panel, TabbedPanel):
    #             tabbed_panel = tabbed_panel.parent
    #         # Проверяем, что вкладка стала активной
    #         if tabbed_panel.current_tab != self:
    #             tabbed_panel.switch_to(self)
    #             if tabbed_panel.current_tab.text == 'Курсы':
    #                 self.update_courses()
    #             elif tabbed_panel.current_tab.text == 'Auth':
    #                 self.check_token()
    #     return super(AuthTab, self).on_touch_down(touch)

    def check_token(self):
        token_check = App.get_running_app().token_check

        if token_check and token_check['access_token'] !='your_token' and (datetime.now() < token_check['expiry']):
            self.create_logout_layout()
        else:
            # Удаление и токена, и словаря для проверки при истечении времени
            App.get_running_app().token = None
            App.get_running_app().token_check = None
            self.create_login_layout()

    def create_logout_layout(self):
        def update_layout(dt):
            self.clear_widgets()
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(Label(text='Вы уже вошли в систему'))
            logout_button = Button(text='Logout')
            logout_button.bind(on_press=self.logout)
            layout.add_widget(logout_button)
            self.add_widget(layout)

        Clock.schedule_once(update_layout)


    def create_login_layout(self):

        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Username'))
        self.username_input = TextInput(multiline=False)
        layout.add_widget(self.username_input)
        layout.add_widget(Label(text='Password'))
        self.password_input = TextInput(password=True, multiline=False)
        layout.add_widget(self.password_input)
        login_button = Button(text='Login')
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)
        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        login_url = 'http://127.0.0.1:8000/api/v1/auth/login'
        request_data = urlencode({
            'username': username,
            'password': password
        })
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        UrlRequest(login_url, req_body=request_data, req_headers=headers,
                   on_success=self.on_login_success, on_failure=self.on_login_failure)

    def on_login_failure(self, request, result):
        print('Ошибка аутентификации:', request.resp_status, result)

    def on_login_success(self, request, result):
        # Сохранение токена аутентификации и переход к экрану курсов
        App.get_running_app().token = result['access_token']

        # Создание отдельного словаря для отслеживания времени истечения токена в приложении
        App.get_running_app().token_check = {
            'access_token': result['access_token'],
            'expiry': datetime.now() + timedelta(minutes=55)  # Устанавливаем время истечения на 55 минут
        }
        # Получаем доступ к родительскому TabbedPanel через свойство parent
        tp = self.parent
        while not isinstance(tp, TabbedPanel):
            tp = tp.parent

        # Переключаемся на вкладку курсов и вызываем метод update_courses
        for tab in tp.tab_list:
            if isinstance(tab, CoursesTab):
                tp.switch_to(tab)
                tab.update_courses()  # Вызываем метод update_courses
                break

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
        self.create_login_layout()
        # self.check_token()

    def on_logout_failure(self, request, result):
        print('Ошибка при выходе из системы:', request.resp_status, result)
        self.create_login_layout()


class CoursesTab(TabbedPanelItem):
    def __init__(self, **kwargs):
        super(CoursesTab, self).__init__(**kwargs)
        self.text = 'Курсы'
        layout = BoxLayout(orientation='vertical')
        self.courses_label = Label(text='Зарегистрируйтесь и войдите для отображения доступных курсов')
        layout.add_widget(self.courses_label)
        self.add_widget(layout)

    def update_courses(self):
        try:
            token = App.get_running_app().token
            if token:
                courses_url = 'http://127.0.0.1:8000/courses'
                headers = {'Authorization': f'Bearer {token}'}
                # Добавляем параметр on_redirect для обработки перенаправлений
                UrlRequest(courses_url, req_headers=headers, on_success=self.on_courses_success,
                           on_redirect=self.on_redirect)
            else:
                self.courses_label.text = 'Зарегистрируйтесь и войдите для отображения доступных курсов'
        except Exception as e:
            print(f'Ошибка при обновлении курсов: {e}')

    def on_redirect(self, request, result):
        # Логируем все заголовки ответа
        print('Заголовки ответа:', request.resp_headers)

        # Пытаемся получить URL для перенаправления с учетом регистра
        redirect_url = request.resp_headers.get('location')  # Используйте 'location' в нижнем регистре
        print('URL для перенаправления:', redirect_url)

        if redirect_url:
            token = App.get_running_app().token
            headers = {'Authorization': f'Bearer {token}'}
            UrlRequest(redirect_url, req_headers=headers, on_success=self.on_courses_success)
        else:
            print('Ошибка: Заголовок Location отсутствует в ответе.')

    def on_courses_success(self, request, result):
        # Обновление списка курсов
        # courses_list = '\n'.join([course['name'] for course in result])
        # self.courses_label.text = courses_list

        courses_list = '\n'.join(
            [f"Название: {course['name']}, Описание: {course['description']}, Цена: {course['price']} руб." for course
             in result])
        self.courses_label.text = courses_list

class MyTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super(MyTabbedPanel, self).__init__(**kwargs)
        self.initial_switch_done = False
        Clock.schedule_once(self.finish_initialization)   # стопорим выполнение до полной инициализации всегоп риложения
        self.bind(current_tab=self.on_tab_switch)

    def finish_initialization(self, dt):
        self.initial_switch_done = True
        # Явно вызываем on_tab_switch для первой вкладки
        self.on_tab_switch(self, self.current_tab)

    def switch_to(self, header):
        if not self.initial_switch_done:
            return
        super(MyTabbedPanel, self).switch_to(header)

    def on_tab_switch(self, instance_of_tabbed_panel, instance_of_tab, *args):
        if not self.initial_switch_done:
            return
        # Проверяем, является ли текущая вкладка вкладкой AuthTab
        if isinstance(instance_of_tab, AuthTab):
            instance_of_tab.check_token()
        # Проверяем, является ли текущая вкладка вкладкой CoursesTab
        elif isinstance(instance_of_tab, CoursesTab):
            instance_of_tab.update_courses()


class MyApp(App):
    token = None
    token_check = None  # Добавляем атрибут для отслеживания времени истечения токена

    # def build(self):
    #     tp = TabbedPanel(do_default_tab=False)  # Убираем закладку по умолчанию
    #     tp.add_widget(AuthTab())
    #     tp.add_widget(CoursesTab())
    #     return tp

    def build(self):
        self.tp = MyTabbedPanel(do_default_tab=False)
        self.auth_tab = AuthTab()
        self.courses_tab = CoursesTab()
        self.tp.add_widget(self.auth_tab)
        self.tp.add_widget(self.courses_tab)
        return self.tp

    def on_start(self):
        # Инициализация токена и времени его истечения
        self.token = {'access_token': 'your_token', 'token_type': 'your_type'}
        # Инициализация словаря для проверки токена
        self.token_check = {'access_token': 'your_token', 'token_type': 'your_type', 'expiry': datetime.now() + timedelta(seconds=3600)}

if __name__ == '__main__':
    MyApp().run()