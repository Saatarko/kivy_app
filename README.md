# Этот проект - дипломная работа студента группы Py53-onl Хвороща Александр Владимировича.

# Ссылка на сайт:
-

# Описание:
Внешнее приложение на Kivy (вместо Frontend) -  IT школы с курсами, записями на курсы,зачислением в группы и групповым чатом на websocket. Сделано кеширование. Для работы с backend на Fastapi

# Backend:

Серверная часть - backend на Fastapi
https://github.com/Saatarko/-ourses-Fast_api-.git

# Технологии:

Языки программирования: Python v3.8
Дополнительно: Kivy

# Размещение:
-

# Для локальной загрузки требуется:
1.Загрузить сайт на ПК.
2. Установить виртуальное окружение с Python v3.8
3. Установить библиотеки. (в проекте использовался poetry)
   Для этого Вам нужно установить poetry - pip install poetry
   Затем для устновки всех библиотек  -   poetry install
4. Для запуска запустить main.py

Дополнительно. Приложение может быть собрано до запускаемой программы под windows или android. 
Файлы с настройками для сборки уже включены в проект.

## 1. Сборка приложения для Windows

### Установка необходимых инструментов

1. Установите Python (рекомендуется версия 3.7 или 3.8).
2. Установите `pip` и `virtualenv`:
    
    ```
    pip install virtualenv
    
    ```
    
3. Создайте виртуальное окружение и активируйте его:
    
    ```
    virtualenv venv
    source venv/Scripts/activate  # Для Windows PowerShell
    
    ```
    
4. Установите Kivy:
    
    ```
    pip install kivy
    
    ```
    
5. Установите `PyInstaller`:
    
    ```
    pip install pyinstaller
    
    ```
   

### Сборка приложения

1. Создайте файл вашего Kivy приложения `main.py`.
2. Запустите `PyInstaller`:
    
    ```
    pyinstaller --onefile --windowed main.py
    
    ```
    
3. После выполнения команды в папке `dist` появится исполняемый файл вашего приложения.

## 2. Сборка приложения для Android

Для сборки приложения Kivy для Android используется `Buildozer`.

### Установка необходимых инструментов

1. Установите `Buildozer` и зависимости (Linux или WSL на Windows рекомендуется):
    
    ```
     sudo apt update
    sudo apt install -y python3 python3-pip python3-dev build-essential git
    sudo pip3 install --upgrade Cython==0.29.21 virtualenv
    sudo pip3 install buildozer
    
    ```
    
2. Создайте и активируйте виртуальное окружение:
    
    ```
    virtualenv venv
    source venv/bin/activate
    
    ```
    
3. Установите Kivy в виртуальное окружение:
    
    ```
    pip install kivy
    
    ```
    
### Сборка приложения

1. Инициализируйте проект Buildozer:
    
    ```
    buildozer init
    
    ```
    
2. Отредактируйте файл `buildozer.spec`, чтобы указать параметры вашего проекта, такие как название, пакет и т.д.
3. Постройте APK:
    
    ```

    buildozer -v android debug
    
    ```
    
4. APK-файл будет находиться в папке `bin`.


# This project is a diploma of a student of the Py53-onl group Khvorosh Alexander Vladimirovich.

# Link to the site:
-

# Description:
External application on Kivy (instead of Frontend) - IT schools with courses, course registration, enrollment in groups and a group chat on websocket. Caching is done. To work with the backend on Fastapi

# Backend:

Server part - backend on Fastapi
https://github.com/Saatarko/-ourses-Fast_api-.git

# Technologies:

Programming languages: Python v3.8
Additionally: Kivy

# Placement:
-

# For local download you need:
1. Download the site to your PC.
2. Install a virtual environment with Python v3.8
3. Install libraries. (poetry was used in the project)
To do this, you need to install poetry - pip install poetry
Then to install all the libraries - poetry install
4. To run, run main.py

Additionally. The application can be built before the program is launched under Windows or Android.

The files with the settings for the build are already included in the project.

## 1. Building an application for Windows

### Installing the necessary tools

1. Install Python (version 3.7 or 3.8 is recommended).
2. Install `pip` and `virtualenv`:

```
pip install virtualenv

```

3. Create a virtual environment and activate it:

```
virtualenv venv
source venv/Scripts/activate # For Windows PowerShell

```

4. Install Kivy:

```
pip install kivy

```

5. Install `PyInstaller`:

```
pip install pyinstaller

```

### Building the application

1. Create your Kivy application file `main.py`.

2. Run `PyInstaller`:

```
pyinstaller --onefile --windowed main.py

```

3. After running the command, your application executable will appear in the `dist` folder.

## 2. Building an Android app

`Buildozer` is used to build a Kivy app for Android.

### Installing the required tools

1. Install `Buildozer` and dependencies (Linux or WSL on Windows is recommended):

```
sudo apt update
sudo apt install -y python3 python3-pip python3-dev build-essential git
sudo pip3 install --upgrade Cython==0.29.21 virtualenv
sudo pip3 install buildozer

```

2. Create and activate a virtual environment:

```
virtualenv venv
source venv/bin/activate

```

3. Install Kivy in the virtual environment:

```
pip install kivy

```

### Building the application

1. Initialize the Buildozer project:

```
buildozer init

```

2. Edit the `buildozer.spec` file to specify your project parameters, such as name, package etc.
3. Build the APK:

```

buildozer -v android debug

```
