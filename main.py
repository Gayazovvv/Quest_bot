import telebgitot
import json


# Загрузка данных из файла
def load_data(quest_locations):
    with open(quest_locations, 'r', encoding="UTF-8") as file:
        data = json.load(file)
    return data


# Сохранение данных в файл
def save_data(data, quest_locations):
    with open(quest_locations, 'w') as file:
        json.dump(data, file)


# Инициализация бота
bot = telebot.TeleBot('5592459041:AAFM0e9fFmodzxvf6tg25OgiLQbbxp2sUY8')


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Загрузка пользовательских данных
    user_data = load_data('user_data.json')

    # Проверяем, если пользователь уже начал игру
    if str(message.chat.id) in user_data:
        bot.send_message(message.chat.id, "Вы уже начали игру!")
        bot.send_message(message.chat.id, "Выберите действие:",
                         reply_markup=generate_actions_keyboard(user_data["location"]))
    else:
        # Создаем новую запись для пользователя в данных
        user_progress = {
            'location': 'start',
            'level': 1,
            'experience': 0
        }
        user_data[str(message.chat.id)] = user_progress
        save_data(user_data, 'user_data.json')

        # Приветственное сообщение
        bot.send_message(message.chat.id, "Добро пожаловать в игру! Вы готовы начать свое приключение?\n"
                                          "Жил был мальчик, лет 16. Он очень любил играть в игры.\n"
                                          "В один день мальчику отключили свет, он решил выйти и прогуляться по улице.")
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=generate_actions_keyboard('start'))


# Генерация кнопок с доступными действиями
def generate_actions_keyboard(location):
    # Загрузка данных по локации
    locations_data = load_data('quest_locations.json')
    options = locations_data['locations'][location]['options']

    # Создаем клавиатуру с кнопками
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        keyboard.add(telebot.types.KeyboardButton(option))

    return keyboard


# Обработчик сообщений и выбор действий игрока
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Загрузка пользовательских данных и данных локаций
    user_data = load_data('user_data.json')
    locations_data = load_data('quest_locations.json')["locations"]

    # Проверяем, если пользователь уже начал игру
    if str(message.chat.id) in user_data:
        user_progress = user_data[str(message.chat.id)]
        current_location = user_progress['location']
        level = user_progress['level']
        experience = user_progress['experience']

        if not locations_data[current_location]['options']:
            del user_data[str(message.chat.id)]
            save_data(user_data, 'user_data.json')

            image_path = locations_data[current_location]["path_to_image"]

            # отправляем иллюстрацию
            if image_path:
                bot.send_photo(message.chat.id, open(image_path, "rb"))

            # Выводим описание новой локации и доступные действия
            bot.send_message(message.chat.id, locations_data[current_location])

            bot.send_message(message.chat.id, "Бла-бла-бла заново.", reply_markup=None)

            return

        # Проверяем введенное действие игрока
        if message.text in locations_data[current_location]['options']:
            # Обновляем пользовательские данные в зависимости от выбранного действия
            selected_action = message.text
            new_location = locations_data[current_location]['options'][selected_action]['to_location']
            new_experience = locations_data[current_location]['options'][selected_action]['experience']
            image_path = locations_data[current_location]['options'][selected_action]["path_to_image"]

            # Обновляем значения уровня и опыта
            user_progress['level'] = level + 1 if new_experience >= experience + 10 else level
            user_progress['experience'] = experience + new_experience

            # Обновляем текущую локацию
            user_progress['location'] = new_location

            # Сохраняем обновленные данные
            user_data[str(message.chat.id)] = user_progress
            save_data(user_data, 'user_data.json')

            # отправляем иллюстрацию
            if image_path:
                bot.send_photo(message.chat.id, open(image_path, "rb"))

            # Выводим описание новой локации и доступные действия
            bot.send_message(message.chat.id, locations_data[new_location]['description'])
            bot.send_message(message.chat.id, "Выберите действие:",
                             reply_markup=generate_actions_keyboard(new_location))
        else:
            # Отправляем сообщение об ошибке, если введенное действие недопустимо
            bot.send_message(message.chat.id, "Недопустимое действие! Выберите одно из предложенных вариантов.")
    else:
        # Отправляем сообщение об ошибке, если пользователь не начал игру
        bot.send_message(message.chat.id, "Для начала игры отправьте команду /start.")


# Запуск бота
bot.polling()
