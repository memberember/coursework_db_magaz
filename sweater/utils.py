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


def get_user_type_int(user_type):
    if user_type == "Администратор":
        return 0
    elif user_type == "Преподаватель":
        return 1
    elif user_type == "Студент":
        return 2
    else:
        return 3
