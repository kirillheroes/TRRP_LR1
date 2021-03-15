import vk_api
import requests

from cryptography.fernet import Fernet
import base64
import hashlib

CLIEND_ID = None

# Ограничение на количество символов в посте ВКонтакте
SYMBOL_LIMIT = 15000

# Данные приложения:

# Идентификатор
APP_ID = '7769596'
# Сервисный ключ доступа
TOKEN = 'cbace6fbcbace6fbcbace6fbbccbda6b07ccbaccbace6fbabe0541718ec05adae28a4b6'

# Версия API ВКонтакте
VERSION = 5.130

# Блок Create ===========================================================================


# Текст, вводимый для завершения ввода текста для создания нового поста
INPUT_END_CMD = '//end'


# Ввод текста из множества строк
# Кодовое слово для остановки ввода: end
def text_input():
    # первый ввод строк
    cur_text = input()
    text = cur_text
    cur_text = input()
    if cur_text == '':
        cur_text = '\n'

    # все последующие вводы строк
    while cur_text != INPUT_END_CMD:
        text = text + '\n' + cur_text
        cur_text = input()
        if cur_text == '':
            cur_text = '\n'

    return text


# Запрос на создание одного конкретного поста
def api_create_post(VK_API, text):
    api_url = 'https://api.vk.com/method/wall.post?'
    query = {
        'owner_id': CLIEND_ID,
        'message': text,
        'access_token': TOKEN,
        'v': VERSION
    }
    return requests.post(api_url, data=query)


# Операция создания
def create_posts(VK_API):
    print('Введите текст для нового поста')
    print('Писать текст можно в несколько строчек через enter!')
    print('(для окончания напишите "', INPUT_END_CMD, '"): ', sep='')
    text = text_input()
    # Если текст слишком большой необходимо сделать несколько постов
    if len(text) > SYMBOL_LIMIT:
        print('ВНИМАНИЕ: большой пост!')
        print('Возможно обрезание текста в посте из-за ограничений на количество символов ВКонтакте')
        print('Поэтому Ваш текст будет разбит на несколько новых постов')
        i = 0
        # Постим пост с ограничением на количество символов
        # и вырезаем запощенный текст из введённого текста.
        # Проделываем это до тех пор, пока не останется кусок текста,
        # не превосходящий заданный предел
        while len(text) > SYMBOL_LIMIT:
            # TO DO ПРОВЕРКА НА ОШИБКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if api_create_post(VK_API, text[:SYMBOL_LIMIT + 1]) is not True:
                return None
            text = text[SYMBOL_LIMIT + 1:]
            i = i + 1
            print('Создан пост №', i, '...', sep='')
        # Постим оставшийся кусок текста (последний необходимый пост)
        # TO DO ПРОВЕРКА НА ОШИБКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if api_create_post(VK_API, text) is not True:
            return None
        print('Создан пост №', i + 1, '...', sep='')
        print('Новые посты успешно созданы!')
    else:
        if api_create_post(VK_API, text) is True:
            print('Новый пост успешно создан!')



# Блок Read =============================================================================


# Операция чтения
# Сводится к выводу всех постов через get_posts, использующийся в других операциях
def read_post(VK_API):
    get_posts(VK_API)


# Запрос получения всех постов со стены пользователя
def api_get_wall(VK_API):
    api_url = 'https://api.vk.com/method/wall.get?'
    query = {
        'owner_id': CLIEND_ID,
        'filter': 'owner',
        'access_token': TOKEN,
        'v': VERSION
    }
    x = requests.post(api_url, data=query)
    print(x)
    return x


# Получение текста и идентификатора конкретного поста
# На основе его индекса в списке
def get_post(post_list):
    try:
        number = int(input())
    except ValueError:
        print('ОШИБКА: Введите целое число!')
        return None

    if number > len(post_list) or number <= 0:
        print('ОШИБКА: Неизвестный пост!')
        return None
    return post_list[number - 1]


# Получение всех постов на стене пользователя и их вывод
def get_posts(VK_API):
    # TO DO ПРОВЕРКА !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    posts_list_json = api_get_wall(VK_API)

    posts = [(item['id'], item['text']) for item in posts_list_json['items']]
    for i, item in enumerate(posts):
        print('Пост №', i + 1, ':\n', '"', item[1], '"\n', sep='')

    return posts



# Блок Update ===========================================================================


# Запрос редактирования поста по идентификатору
def api_update_post(VK_API, post_id, text):
    api_url = 'https://api.vk.com/method/wall.edit?'
    query = {
        'owner_id': CLIEND_ID,
        'message': text,
        'post_id': post_id,
        'access_token': TOKEN,
        'v': VERSION
    }
    return requests.post(api_url, data=query)


# TO DO: ЧТО БУДЕТ, ЕСЛИ РЕДАЧИТЬ ПОСТ С ВЛОЖЕНИЯМИ???? СОХРАНЯТСЯ ЛИ ОНИ??????????????????

# Операция редактирования
def update_post(VK_API):
    posts = get_posts(VK_API)
    print('Введите номер редактируемого поста:')

    post = get_post(posts)
    if post is None:
        return None

    print('Старый текст поста: "', post[1], '"', sep='')

    new_text = input('Введите новый текст: ')

    # TO DO ПРОВЕРКА НА ОШИБКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    try:
        api_update_post(post_id=post[0], text=new_text)
        print('Пост успешно отредактирован!')
    except vk_api.ApiError:
        print('ОШИБКА: Прошло 24 часа с момента создания поста. Редактирование запрещено!')



# Блок Delete ===========================================================================


# Запрос удаления поста по идентификатору
def api_delete_post(VK_API, post_id):
    api_url = 'https://api.vk.com/method/wall.delete?'
    query = {
        'owner_id': CLIEND_ID,
        'post_id': post_id,
        'access_token': TOKEN,
        'v': VERSION
    }
    return requests.post(api_url, data=query)


# Операция удаления поста
def delete_post(VK_API):
    posts = get_posts(VK_API)
    print('Введите номер удаляемого поста: ')

    post = get_post(posts)
    if post is None:
        return None

    # TO DO ПРОВЕРКА НА ОШИБКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    api_delete_post(post_id=post[0])
    print('Пост "', post[1], '" успешно удалён!', sep='')



# Блок сохранения параметров аутентификации  ============================================


# Считывание логина и пароля из файла
def get_file_session():
    try:
        file = open('session.txt', 'r', encoding='utf-8')
        file.close()
    except FileNotFoundError:
        print('нету файла слыш')
        return None

    file = open('session.txt', 'r', encoding='utf-8')
    file_info = file.read().splitlines()
    file.close()

    try:
        login = file_info[0]
        password = file_info[1]
    except Exception:
        return None

    # TO DO валидность введённой инфы?

    # TO DO ШИФРОВАНИЕ!!!!!!!!!

    print('login from file:', login)
    print('password from file:', password)

    return login, password


# Сохранение логина и пароля в файл
def safe_session(login, password):
    #password_bytes = bytes(password, 'utf-8')
    #hash_object = hashlib.sha224(password_bytes)
    #key = bytes(hash_object.hexdigest(), 'utf-8')
    #key = base64.urlsafe_b64encode(password_bytes)
    #print('key1= ', key)
    #print('key1 length= ', len(key))

    #key = Fernet.generate_key()
    #print('key2= ', key)
    #print('key2 length= ', len(key))
    #crypto = Fernet(key)

    #safe_login = crypto.encrypt(login.encode('utf-8'))
    #safe_password = crypto.encrypt(password.encode('utf-8'))

    file = open('session.txt', 'w', encoding='utf-8')
    #file.write(safe_login.decode("utf-8"))
    file.write(login)
    file.write('\n')
    #file.write(safe_password.decode("utf-8"))
    file.write(password)
    file.close()

    # TO DO ШИФРОВАНИЕ!!!!!!!!!


# Блок авторизации и аутентификации =====================================================


# Вход в систему
def authentication(session):
    try:
        session.auth()
    except vk_api.AuthError as error_msg:
        print('ОШИБКА: Неудачная авторизация ВКонтакте. Проверьте правильность логина и пароля. Описание ошибки:')
        print(error_msg)
        return None
    except vk_api.Captcha as error_msg:
        print('ОШИБКА: Приложение не может авторизоваться в Вашей странице из-за того, что ВКонтакте отправил Капчу')
        print('Попробуйте заново позднее...')
        print('Описание ошибки: ', error_msg)
        return None
    return True


# Открытие сессии пользователя
def open_session():
    saved_session = get_file_session()
    from_file = False

    # Проверяем, удаётся ли считать логин и пароль из файла
    if saved_session is None or saved_session[0] is None or saved_session[1] is None:
        # Файла либо нет,
        # либо какие-то данные отсутствуют
        # Вводим логин и пароль, будто файла и не существует
        login = input('Добро пожаловать! Необходимо войти во ВКонтакте для продолжения работы\nЛогин: ')
        password = input('Пароль: ')  # TO DO безопасность
    else:
        # Записываем логин и пароль из файла
        login = saved_session[0]
        password = saved_session[1]
        from_file = True

    print('login:', login)
    print('password:', password)

    # Создаём сессию
    session = vk_api.VkApi(login, password)

    # Проверка на успешный вход
    if authentication(session) is None:
        # Если войти не удалось
        if from_file is True:
            # Если войти не удалось из файла, то это особенный случай
            # Даём пользователю попытку ввести логин и пароль самостоятельно,
            # чтобы битый файл не помешал ему работать
            login = input('Не удалось войти по сохранённым логину и паролю. Введите их заново.\nЛогин: ')
            password = input('Пароль: ')
            session = vk_api.VkApi(login, password)
            if authentication(session) is None:
                return None
        else:
            # Если войти не удалось и проблема не в файле
            return None

    safe_session(login, password)

    return session.get_api()



# Основная часть
def main():
    #VK_API = open_session()

    VK_API = None

    api_url = 'https://oauth.vk.com/token?'
    query = {
        'grant_type': 'password',
        'client_id': APP_ID,
        'client_secret': 'qseO62duENxuq4azpJ2h',
        'username': login,
        'password': password,
        'v': VERSION
    }
    data = requests.post(api_url, data=query)
    print(data.json())

    VK_API = 0

    # Если что-то пошло не так
    if VK_API is None:
        # Следовательно не удалось успешно подключиться к пользователю ВКонтакте
        # Дальнейшая работа невозможна
        return 0

    # Ожидаем ввода команды
    while True:
        print('Доступные команды:')
        print('c (create) - создать пост...')
        print('r (read)   - вывести все посты на стене')
        print('u (update) - изменить текст определённого поста...')
        print('d (delete) - удалить определённый пост...')
        print('q (quit)   - выйти из программы')
        cmd = input()
        if cmd == 'c' or cmd == 'C':
            create_posts(VK_API)
        elif cmd == 'r' or cmd == 'R':
            read_post(VK_API)
        elif cmd == 'u' or cmd == 'U':
            update_post(VK_API)
        elif cmd == 'd' or cmd == 'D':
            delete_post(VK_API)
        elif cmd == 'q' or cmd == 'Q':
            break
        else:
            print('Неизвестная команда!')
        print()

    print('Выход из программы...')
    return 0


if __name__ == '__main__':
    main()
