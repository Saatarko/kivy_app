import json
from urllib.parse import urlencode

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')  # Создаем BoxLayout с вертикальной ориентацией
        layout.add_widget(Label(text='Username'))
        self.username_input = TextInput(multiline=False)
        layout.add_widget(self.username_input)
        layout.add_widget(Label(text='Password'))
        self.password_input = TextInput(password=True, multiline=False)
        layout.add_widget(self.password_input)
        self.login_button = Button(text='Login')
        self.login_button.bind(on_press=self.login)
        layout.add_widget(self.login_button)
        self.add_widget(layout)  # Добавляем BoxLayout в качестве дочернего элемента к Screen

    def on_login_failure(self, request, result):
        print('Ошибка аутентификации:', request.resp_status, result)

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

    def on_login_success(self, request, result):
        # Сохранение токена аутентификации и переход к экрану курсов
        App.get_running_app().token = result['access_token']
        # Получаем экземпляр CoursesScreen и вызываем update_courses
        courses_screen = self.manager.get_screen('courses')
        courses_screen.update_courses()
        # Переход к экрану курсов
        self.parent.current = 'courses'


class CoursesScreen(Screen):
    def __init__(self, **kwargs):
        super(CoursesScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.courses_label = Label(text='Courses will be listed here')
        layout.add_widget(self.courses_label)
        self.add_widget(layout)  # Добавляем BoxLayout в качестве дочернего элемента к Screen

    def update_courses(self):
        try:
            token = App.get_running_app().token
            courses_url = 'http://127.0.0.1:8000/courses'
            headers = {'Authorization': f'Bearer {token}'}
            # Добавляем параметр on_redirect для обработки перенаправлений
            UrlRequest(courses_url, req_headers=headers, on_success=self.on_courses_success,
                       on_redirect=self.on_redirect)
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


class MyApp(App):
    token = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CoursesScreen(name='courses'))
        return sm


if __name__ == '__main__':
    MyApp().run()
