# функция получения строкового типа пользователя по id
def get_user_type(user_type):
    if user_type == 0:
        return "Администратор"
    elif user_type == 1:
        return "Преподаватель"
    elif user_type == 2:
        return "Студент"
    else:
        return "Посетитель"
