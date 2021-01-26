import json

from flask import render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from sweater import app, db
from sweater.models import User, Zakaz, Magazin, Tovar, Kategorya, Magazinhastovar, Country, Color, SizeCategory, Sex, \
    Size, OrderStatus

from sqlalchemy.ext.declarative import DeclarativeMeta


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/users')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('inputEmail')
    password = request.form.get('inputPassword')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')
            if next_page != None:
                return redirect(next_page)
            return redirect(url_for('about'))

        else:
            flash('Логин и пароль не верные')
    return render_template('login_page.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('inputEmail')
    password = request.form.get('inputPassword')
    password2 = request.form.get('inputPassword2')
    sex = request.form.get('sex')
    adress = request.form.get('adress')
    phone = request.form.get('phone')
    fio = request.form.get('fio')
    user_type = request.form.get('user_type')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login,
                            password=hash_pwd,
                            type=user_type,
                            fio=fio,
                            sex=sex,
                            adress=adress,
                            phone=phone
                            )
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))
    return render_template('register_page.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


# страница "О нас"
@app.route('/about')
@login_required
def about():
    return render_template('about.html')


# страница "О нас"
@app.route('/report')
@login_required
def report():
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()
    return render_template('report.html', magazins=magazins)


def str_to_timestamp(string):
    import time
    import datetime
    return time.mktime(datetime.datetime.strptime(string, "%Y-%m-%d").timetuple())


# страница форка
@app.route('/getReport', methods=['POST'])
@login_required
def get_report_ajax():
    print(request.form)
    first_date = request.form.get('first_date')
    second_date = request.form.get('second_date')
    magaz = request.form.get('magaz')

    try:
        items = Zakaz.query.order_by(Zakaz.time).all()
        buffer = []
        sum = 0
        count = 0
        for i in items:
            if i.magazinhastovar.magazin_id == int(magaz):

                if (str_to_timestamp(first_date) <= str_to_timestamp(i.time) <= str_to_timestamp(second_date)):
                    buf = f'<td><img src = "{i.magazinhastovar.tovar.picture}" width = "40" height = "50"></td>' + \
                          f'<td>{i.time}</td>' + \
                          f'<td>{i.magazinhastovar.cost}</td>' + \
                          f'<td>{i.user.fio}</td>' + \
                          f'<td>{i.user.adress}</td>' + \
                          f'<td>{i.user.phone}</td>' + \
                          f'<td>{i.magazinhastovar.tovar.name}</td>' + \
                          f'<td>{i.magazinhastovar.magazin.name}</td>' + \
                          f'<td>{i.order_status.name}</td>'
                    sum += i.magazinhastovar.cost
                    count+=1
                    buffer.append(buf)
        header = f'<th>Фото</th>'
        header += f'<th>Время</th>'
        header += f'<th>Цена(Сумма:{sum})</th>'
        header += f'<th>Получатель</th>'
        header += f'<th>Адрес</th>'
        header += f'<th>Номер</th>'
        header += f'<th>Товар</th>'
        header += f'<th>Магазин(Заказов:{count})</th>'
        header += f'<th>Статус заказа</th>'
        buffer.insert(0, header)
        return jsonify({'success': buffer})
    except Exception as e:
        if not (first_date and second_date):
            return jsonify({'error': 'Обе даты должны быть выбраны'})
        return jsonify({'error': 'Что то пошло не так, попробуйте снова'})


# страница "Товаров"
@app.route('/tovar_list')
@login_required
def tovar_list():
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()
    magazinhastovar = Magazinhastovar.query.all()
    items = Tovar.query.order_by(Tovar.id.desc()).limit(50).all()
    countries = Country.query.all()
    sizes = Size.query.all()
    colors = Color.query.all()

    categories = Kategorya.query.order_by(Kategorya.id).all()
    return render_template('tovar_list.html',
                           data=items,
                           categories=categories,
                           magazins=magazins,
                           magazinhastovar=magazinhastovar,
                           countries=countries,
                           sizes=sizes,
                           colors=colors
                           )


# страница "О нас"
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    items = Magazin.query.filter_by(user_id=current_user.id).all()

    # инициализация данных
    password = request.form.get('inputPassword')
    password2 = request.form.get('inputPassword2')
    fio = request.form.get('fio')

    # запрос в бд на получение пользователя с id текущего пользователя
    user = User.query.get(current_user.id)

    if request.method == 'POST':

        # если не меняли пароль
        if not (password or password2):
            user.fio = fio
            flash(('s', 'Сохранено'))

        # если пароли тоже изменились но не совпадают
        elif password != password2:
            flash(('e', 'Пароли не совпадают!'))

        # если сменили пароль
        else:
            user.fio = fio
            hash_pwd = generate_password_hash(password)
            user.password = hash_pwd
            flash(('s', 'Сохранено'))
    db.session.add(user)
    db.session.commit()
    return render_template('profile.html', data=items)


# страница пользователей
@app.route('/users')
@login_required
def users():
    items = User.query.order_by(User.id).all()
    return render_template('users.html', data=items)


# страница магазинов
@app.route('/magazin_list')
@login_required
def magazin_list():
    items = Magazin.query.order_by(Magazin.id).all()
    owners = User.query.filter_by(type=1).all()
    return render_template('magazin_list.html', data=items, owners=owners)


# страница магазина
@app.route('/magazin/<int:id>')
@login_required
def magazin(id, orderby=0):
    magaz = Magazin.query.get(id)
    if orderby == 1:
        items = Magazinhastovar.query.filter_by(magazin_id=id).order_by(Magazinhastovar.cost.asc()).all()
    else:
        items = Magazinhastovar.query.filter_by(magazin_id=id).order_by(Magazinhastovar.cost.desc()).all()

    categories = Kategorya.query.order_by(Kategorya.id).all()
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()
    countries = Country.query.all()
    sizes = Size.query.all()
    colors = Color.query.all()

    return render_template('magazin.html',
                           data=items,
                           magaz=magaz,
                           categories=categories,
                           magazins=magazins,
                           countries=countries,
                           sizes=sizes,
                           colors=colors
                           )


# страница магазина
@app.route('/magazin/<int:id>&sorted_by=<int:sortedby>')
@login_required
def magazin_sorted(id, sortedby=0):
    magaz = Magazin.query.get(id)
    items = Magazinhastovar.query.filter_by(magazin_id=id).order_by(Magazinhastovar.cost.desc()).all()
    if sortedby == 1:
        items = Magazinhastovar.query.filter_by(magazin_id=id).order_by(Magazinhastovar.cost.asc()).all()
    categories = Kategorya.query.order_by(Kategorya.id).all()
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()

    return render_template('magazin.html', data=items, magaz=magaz, categories=categories, magazins=magazins)


# страница форка
@app.route('/sortTovars', methods=['POST'])
@login_required
def sortTovar_ajax():
    magazin_id = request.form.get('magazin_id')
    sort_type = request.form.get('sort_type')

    magaz = Magazin.query.get(magazin_id)
    items = Magazinhastovar.query.filter_by(magazin_id=magazin_id).order_by(Magazinhastovar.cost.desc()).all()
    if sort_type == 1:
        items = Magazinhastovar.query.filter_by(magazin_id=magazin_id).order_by(Magazinhastovar.cost.asc()).all()
    categories = Kategorya.query.order_by(Kategorya.id).all()
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()

    return render_template('magazin.html', data=items, magaz=magaz, categories=categories, magazins=magazins)


# страница форка
@app.route('/forkTovar', methods=['POST'])
@login_required
def forkTovar_ajax():
    print(request.form)
    tovar_count = request.form.get('tovar_count')
    tovar_cost = request.form.get('tovar_cost')
    tovar_id = request.form.get('tovar_id')
    magazin_id = request.form.get('magazin_id')

    try:
        tovar = Tovar.query.get(tovar_id)
        magazhastovar = Magazinhastovar(
            tovar_id=tovar_id,
            magazin_id=magazin_id,
            cost=tovar_cost,
            count=tovar_count)
        db.session.add(magazhastovar)
        db.session.commit()

        return jsonify({'success': f'Успешно сохранен: {tovar.name}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# страница категории
@app.route('/category/<int:id>')
@login_required
def categoria(id):
    category = Kategorya.query.get(id)
    items = Tovar.query.filter_by(category_id=id).all()
    categories = Kategorya.query.order_by(Kategorya.id).all()
    magazinhastovar = Magazinhastovar.query.all()
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()

    return render_template('category.html', data=items, magazins=magazins, category=category, categories=categories,
                           magazinhastovar=magazinhastovar)


# страница категории
@app.route('/category/<int:id>&sorted_by=<int:sortedby>')
@login_required
def categoria_sorted(id, sortedby):
    category = Kategorya.query.get(id)
    items = Tovar.query.filter_by(category_id=id).order_by(Tovar.name.desc()).all()
    if sortedby == 1:
        items = Tovar.query.filter_by(category_id=id).order_by(Tovar.name.asc()).all()
    # items = Tovar.query.filter_by(category_id=id).all()
    categories = Kategorya.query.order_by(Kategorya.id).all()
    magazinhastovar = Magazinhastovar.query.all()
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()

    return render_template('category.html', data=items, magazins=magazins, category=category, categories=categories,
                           magazinhastovar=magazinhastovar)


# страница категорий
@app.route('/category_list')
@login_required
def category_list():
    items = Kategorya.query.order_by(Kategorya.id).all()
    return render_template('category_list.html', data=items)


# страница заказов
@app.route('/orders')
@login_required
def orders():
    items = Zakaz.query.order_by(Zakaz.id).all()
    order_status = OrderStatus.query.order_by(OrderStatus.id).all()
    return render_template('orders.html', data=items, order_status=order_status)


# адрес для ajax запроса изменения пользователя
@app.route('/editUser', methods=['POST'])
def edit_user_ajax():
    fio = request.form.get('fio')
    user_id = request.form.get('user_id')
    try:
        user = User.query.get(user_id)
        user.fio = fio
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': f'Успешно сохранен: {user.fio}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса удаления пользователя
@app.route('/deleteUser', methods=['POST'])
def delete_user_ajax():
    user_id = request.form.get('user_id')
    fio = request.form.get('fio')

    try:
        User.query.filter(User.id == user_id).delete()
        db.session.commit()
        return jsonify({'success': f'Успешно удален: {fio}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления пользователя
@app.route('/addUser', methods=['POST'])
def add_user_ajax():
    # вытаскиваем данные с полученной формы
    login = request.form.get('login')
    password = request.form.get('password')
    fio = request.form.get('fio')
    user_type = request.form.get('user_type')
    sex = request.form.get('sex')
    adress = request.form.get('adress')
    phone = request.form.get('phone')

    # хешируем пароль
    hash_pwd = generate_password_hash(password)

    # проверка заполненности полей
    if not (login and password and fio):
        return jsonify({'error': 'Все поля должны быть заполнены'})

    # отловщик ошибок
    try:

        # создание объекта User
        user = User(login=login,
                    password=hash_pwd,
                    fio=fio,
                    type=user_type,
                    sex=sex,
                    adress=adress,
                    phone=phone
                    )
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': f'Успешно добавлен: {fio}'})

    # если поймалась ошибка, то выполняется этот блок
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса изменения магазина
@app.route('/editMagazin', methods=['POST'])
def edit_magazin_ajax():
    name = request.form.get('magaz_name')
    id = request.form.get('magaz_id')
    try:
        magaz = Magazin.query.get(id)
        magaz.name = name
        db.session.add(magaz)
        db.session.commit()
        return jsonify({'success': f'Успешно сохранен: {magaz.name}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса удаления магазина
@app.route('/deleteMagazin', methods=['POST'])
def delete_magazin_ajax():
    name = request.form.get('magaz_name')
    id = request.form.get('magaz_id')
    print(request.form)
    try:
        Magazin.query.filter(Magazin.id == id).delete()
        db.session.commit()
        return jsonify({'success': f'Успешно удален: {name}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления магазина
@app.route('/addMagazin', methods=['POST'])
def add_magazin_ajax():
    # вытаскиваем данные с полученной формы
    name = request.form.get('name')
    user_id = request.form.get('user_id')

    # проверка заполненности полей
    if not name:
        return jsonify({'error': 'Название не должно быть пустым'})

    # отловщик ошибок
    try:

        # создание объекта Magazin
        magaz = Magazin(name=name, user_id=user_id)
        db.session.add(magaz)
        db.session.commit()
        return jsonify({'success': f'Успешно добавлен: {name}'})

    # если поймалась ошибка, то выполняется этот блок
    except Exception as e:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса изменения товара
@app.route('/editTovar', methods=['POST'])
def edit_tovar_ajax():
    id = request.form.get('tovar_id')
    name = request.form.get('tovar_name')
    cvet = request.form.get('cvet')
    opisanie = request.form.get('opisanie')
    strana = request.form.get('strana')
    razmer = request.form.get('razmer')
    picture = request.form.get('picture')
    sex = request.form.get('sex')
    category_id = request.form.get('category_id')

    print(request
          .form)
    try:
        tovar = Tovar.query.get(id)
        tovar.name = name
        tovar.cvet = cvet
        tovar.opisanie = opisanie
        tovar.strana = strana
        tovar.razmer = razmer
        tovar.picture = picture
        tovar.sex = sex
        tovar.category_id = category_id

        db.session.add(tovar)
        db.session.commit()
        return jsonify({'success': f'Успешно сохранен: {tovar.name}'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса изменения товара
@app.route('/editTovarWithCost', methods=['POST'])
def edit_tovar_with_cost_ajax():
    id = request.form.get('tovar_id')
    name = request.form.get('tovar_name')
    cvet = request.form.get('cvet')
    opisanie = request.form.get('opisanie')
    strana = request.form.get('strana')
    razmer = request.form.get('razmer')
    picture = request.form.get('picture')
    sex = request.form.get('sex')
    category_id = request.form.get('category_id')
    cost = request.form.get('cost')
    count = request.form.get('count')
    magtovar_id = request.form.get('magtovar_id')
    print(cost + count)

    print(request
          .form)
    try:
        tovar = Tovar.query.get(id)
        tovar.name = name
        tovar.cvet = cvet
        tovar.opisanie = opisanie
        tovar.strana = strana
        tovar.razmer = razmer
        tovar.picture = picture
        tovar.sex = sex
        tovar.category_id = category_id
        db.session.add(tovar)
        db.session.commit()
        print(magtovar_id)
        magtovar = Magazinhastovar.query.get(magtovar_id)
        magtovar.cost = cost
        magtovar.count = count
        db.session.add(magtovar)
        db.session.commit()
        return jsonify({'success': f'Успешно сохранен: {tovar.name}'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса изменения товара
@app.route('/editTovarCost', methods=['POST'])
def edit_tovar_cost_ajax():
    cost = request.form.get('cost')
    count = request.form.get('count')
    magtovar_id = request.form.get('magtovar_id')
    print(request.form)

    try:
        magtovar = Magazinhastovar.query.get(magtovar_id)
        magtovar.cost = cost
        magtovar.count = count
        db.session.add(magtovar)
        db.session.commit()
        return jsonify({'success': f'Данные товара "{magtovar.tovar.name}" изменены.'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса удаления товара
@app.route('/deleteTovar', methods=['POST'])
def delete_tovar_ajax():
    name = request.form.get('tovar_name')
    tovar_id = request.form.get('tovar_id')
    print(request.form)
    try:
        Tovar.query.filter(Tovar.id == tovar_id).delete()

        db.session.commit()
        return jsonify({'success': f'Успешно удален: {name}'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса удаления товара
@app.route('/deleteTovarFromMagaz', methods=['POST'])
def delete_tovar_from_magaz_ajax():
    magtovar_id = request.form.get('magtovar_id')
    try:
        Magazinhastovar.query.filter(Magazinhastovar.id == magtovar_id).delete()

        db.session.commit()
        return jsonify({'success': f'Товар успешно удален'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления товара
@app.route('/addTovar', methods=['POST'])
def add_tovar_ajax():
    # вытаскиваем данные с полученной формы
    name = request.form.get('name')
    cvet = request.form.get('cvet')
    opisanie = request.form.get('opisanie')
    strana = request.form.get('strana')
    razmer = request.form.get('razmer')
    picture = request.form.get('picture')
    sex = request.form.get('sex')
    category_id = request.form.get('category_id')
    # magaz_id = request.form.get('magaz_id')
    # cost = request.form.get('cost')
    # count = request.form.get('count')

    # проверка заполненности полей
    if not name:
        return jsonify({'error': 'Название не должно быть пустым'})

    # отловщик ошибок
    try:

        # создание объекта Tovar
        tovar = Tovar(name=name,
                      cvet=cvet,
                      opisanie=opisanie,
                      strana=strana,
                      razmer=razmer,
                      picture=picture,
                      sex=sex,
                      category_id=category_id
                      )
        db.session.add(tovar)
        db.session.commit()
        # tovar = Tovar.query.order_by(Tovar.id.desc()).first()
        # magazin_has_tovar = Magazinhastovar(magazin_id=magaz_id, tovar_id=tovar.id,
        #                                     cost=cost,
        #                                     count=count
        #                                     )
        # db.session.add(magazin_has_tovar)
        # db.session.commit()
        return jsonify({'success': f'Успешно добавлен: {name}'})

    # если поймалась ошибка, то выполняется этот блок
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления товара с ценой
@app.route('/addTovarWithCost', methods=['POST'])
def add_tovar_with_cost_ajax():
    # вытаскиваем данные с полученной формы
    name = request.form.get('name')
    cvet = request.form.get('cvet')
    opisanie = request.form.get('opisanie')
    strana = request.form.get('strana')
    razmer = request.form.get('razmer')
    picture = request.form.get('picture')
    sex = request.form.get('sex')
    category_id = request.form.get('category_id')
    magaz_id = request.form.get('magaz_id')
    cost = request.form.get('cost')
    count = request.form.get('count')

    # проверка заполненности полей
    if not name:
        return jsonify({'error': 'Название не должно быть пустым'})

    # отловщик ошибок
    try:

        # создание объекта Tovar
        tovar = Tovar(name=name,
                      cvet=cvet,
                      opisanie=opisanie,
                      strana=strana,
                      razmer=razmer,
                      picture=picture,
                      sex=sex,
                      category_id=category_id
                      )
        db.session.add(tovar)
        db.session.commit()
        tovar = Tovar.query.order_by(Tovar.id.desc()).first()
        magazin_has_tovar = Magazinhastovar(magazin_id=magaz_id, tovar_id=tovar.id,
                                            cost=cost,
                                            count=count
                                            )
        db.session.add(magazin_has_tovar)
        db.session.commit()
        return jsonify({'success': f'Успешно добавлен: {name}'})

    # если поймалась ошибка, то выполняется этот блок
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса изменения категории
@app.route('/editCategory', methods=['POST'])
def edit_category_ajax():
    name = request.form.get('category_name')
    id = request.form.get('category_id')
    try:
        category = Kategorya.query.get(id)
        category.name = name
        db.session.add(category)
        db.session.commit()
        return jsonify({'success': f'Успешно сохранен: {category.name}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса удаления категории
@app.route('/deleteCategory', methods=['POST'])
def delete_category_ajax():
    name = request.form.get('category_name')
    id = request.form.get('category_id')
    try:
        Kategorya.query.filter(Kategorya.id == id).delete()
        db.session.commit()
        return jsonify({'success': f'Успешно удален: {name}'})
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления категории
@app.route('/addCategory', methods=['POST'])
def add_category_ajax():
    # вытаскиваем данные с полученной формы
    name = request.form.get('name')

    # проверка заполненности полей
    if not name:
        return jsonify({'error': 'Название не должно быть пустым'})

    # отловщик ошибок
    try:

        # создание объекта Tovar
        category = Kategorya(name=name
                             )
        db.session.add(category)
        db.session.commit()
        return jsonify({'success': f'Успешно добавлен: {name}'})

    # если поймалась ошибка, то выполняется этот блок
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления категории
@app.route('/addOrder', methods=['POST'])
def add_order_ajax():
    # вытаскиваем данные с полученной формы
    magazinhastovar_id = request.form.get('magazinhastovar_id')
    print(request.form)
    from datetime import date

    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    # отловщик ошибок
    magazinhastovar = Magazinhastovar.query.get(magazinhastovar_id)
    try:
        if magazinhastovar.count - 1 <= -1:
            return jsonify({'error': 'Товар кончился на складе'})

        # создание объекта заказ
        zakaz = Zakaz(all_cost=magazinhastovar.cost,
                      magaztovar_id=magazinhastovar.id,
                      user_id=current_user.id,
                      time=d1
                      )
        db.session.add(zakaz)
        db.session.commit()
        magazinhastovar.count -= 1
        db.session.add(magazinhastovar)
        db.session.commit()
        return jsonify({'success': f'Успешно добавлен: {d1}'})

    # если поймалась ошибка, то выполняется этот блок
    except:
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса добавления категории
@app.route('/editOrderStatus', methods=['POST'])
def edit_order_status_ajax():
    # вытаскиваем данные с полученной формы
    order_id = request.form.get('order_id')
    order_status = request.form.get('order_status')
    zakaz = Zakaz.query.get(order_id)
    try:
        zakaz.status = order_status
        db.session.add(zakaz)
        db.session.commit()
        return jsonify({'success': f'Статус заказа пользователя "{zakaz.user.fio}" успешно изменен'})

    # если поймалась ошибка, то выполняется этот блок
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса поиска
@app.route('/getData', methods=['POST'])
def get_data_ajax():
    search = request.form.get("search")
    type = request.form.get("type")
    second = request.form.get("second")
    magazinhastovar = Magazinhastovar.query.all()

    print(request.form)
    if search != '':
        items = Tovar.query.filter_by(name=search).all()
    else:
        items = Tovar.query.order_by(Tovar.id.desc()).limit(50).all()

    if type == '1':
        if search != '':
            items = Tovar.query.filter_by(name=search).filter_by(category_id=second).all()
        else:
            items = Tovar.query.filter_by(category_id=second).all()
    elif type == '2':
        if search != '':
            items = Tovar.query.filter_by(name=search).filter_by(cvet=second).all()
        else:
            items = Tovar.query.filter_by(cvet=second).all()
    elif type == '3':
        if search != '':
            items = Tovar.query.filter_by(name=search).filter_by(sex=second).all()
        else:
            items = Tovar.query.filter_by(sex=second).all()
    elif type == '4':
        if search != '':
            items = Tovar.query.filter_by(name=search).filter_by(strana=second).all()
        else:
            items = Tovar.query.filter_by(strana=second).all()

    buffer = []
    if current_user.type == 2:
        for i in items:
            buffer.append(get_html_tovar_user(i, magazinhastovar))
    elif current_user.type == 1:
        for i in items:
            buffer.append(get_html_tovar_owner(i))
    elif current_user.type == 0:
        for i in items:
            buffer.append(get_html_tovar_admin(i))
    try:

        return jsonify({'success': buffer})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# адрес для ajax запроса изменения товара
@app.route('/getSelectedData', methods=['POST'])
def get_selected_data_ajax():
    type = request.form.get("type")
    items = []

    if type == '1':
        items = Kategorya.query.all()
    elif type == '2':
        items = Color.query.all()
    elif type == '3':
        items = Sex.query.all()
    elif type == '4':
        items = Country.query.all()
    buffer = []
    for i in items:
        buffer.append(F'value="{i.id}">' + i.name)
    try:
        return jsonify({'success': buffer})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Что то пошло не так, попробуйте позже'})


# перенаправление на логин при неавторизованном пользователе
@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


def get_html_tovar_user(el, maghastovar):
    buf = '<div class="col-md-6"><div class="row g-0 border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative"><div class="col p-4 d-flex flex-column position-static">' + \
          '<form id=' + f'{el.id}' + '><strong class="d-inline-block mb-2 text-primary">' + \
          f'{el.country.name}</strong><h3 class="mb-0">' + \
          f'{el.name}</h3><div class="mb-1 text-muted">' \
          f'{el.sex_name.name} {el.color.name}' + \
          f'. Стандарт: {el.size.size_category.name} {el.size.name}</div><p class="card-text mb-auto">' + \
          f'{el.opisanie}</p><p class="card-text mb-auto">' + \
          f'Категория: {el.category.name}</p>'

    # button
    buf += '<div class ="input-group mb-3"> <div class ="input-group"> <select ' \
           'name="magazinhastovar_id" id="magazinhastovar_id" class ="form-control">'

    # magazins

    for mag in maghastovar:
        if el.id == mag.tovar_id:
            buf += f'<option value = "{mag.id}"> {mag.magazin.name}' + \
                   f' Осталось: {mag.count}' + \
                   f'шт.{mag.cost}₽ </option>'

    buf += '</select> <button onclick = "ajax_fun(this.form,' + "'addOrder'" + ');" class ="btn btn-outline-secondary" type="button" id="button-addon2"> Заказать </button></div> </div>'

    buf += f'</form> </div><div class="col-auto d-none d-lg-block"><img ' + \
           f'src="{el.picture}" width="200" height="250"></div></div></div> '
    return buf


def get_html_tovar_owner(el):
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()

    buf = '<div class="col-md-6"><div class="row g-0 border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250' \
          ' position-relative"><div class="col p-4 d-flex flex-column position-static">' + \
          '<form id=' + f'{el.id}' + '><strong class="d-inline-block mb-2 text-primary">' + \
          f'{el.country.name}</strong><h3 class="mb-0">' + \
          f'{el.name}</h3><div class="mb-1 text-muted">' \
          f'{el.sex_name.name} {el.color.name}' + \
          f' Стандарт: {el.size.size_category.name} {el.size.name}</div><p class="card-text mb-auto">' + \
          f'{el.opisanie}</p><p class="card-text mb-auto">' + \
          f'Категория: {el.category.name}</p>' + \
          '<div class="input-group"> <span class ="input-group-text"> Количество </span> <input type="text"' \
          ' name="tovar_count" id="tovar_count" class ="form-control" value="100"> </div >' + \
          '<div class="input-group"><span class="input-group-text">Цена</span><input type="text" ' \
          'name="tovar_cost" id="tovar_cost" class="form-control" value="100"></div>' + \
          '<input type = "hidden" name = "tovar_id" id = "tovar_id" value = ' + \
          f"'{el.id}'" + '/>'

    buf += '<div class ="input-group mb-3"> <div class ="input-group"> <select ' \
           'name="magazin_id" id="magazin_id" class ="form-control">'

    # magazins
    for mag in magazins:
        if current_user.id == mag.user_id:
            buf += f'<option value = "{mag.id}"> {mag.name}' + '</option>'

    # button

    buf += '</select> <button onclick = "ajax_fun(this.form,' + "'forkTovar'" + ');" class ="btn btn-outline-secondary" type="button" id="button-addon2"> Добавить к себе </button></div> </div>'

    buf += f'</form> </div><div class="col-auto d-none d-lg-block"><img ' + \
           f'src="{el.picture}" width="200" height="250"></div></div></div> '
    return buf


def get_html_tovar_admin(el):
    magazins = Magazin.query.filter_by(user_id=current_user.id).all()
    magazinhastovar = Magazinhastovar.query.all()
    countries = Country.query.all()
    sizes = Size.query.all()
    colors = Color.query.all()
    categories = Kategorya.query.order_by(Kategorya.id).all()

    buf = ' <div name=' + f"'tr{el.id}'" + 'class="">' + \
          ' <div id=' + f"'tr{el.id}'" + '' + \
          'class="row border rounded flex-md-row mb-4 ">' + \
          '<div class="col p-4">'

    # name
    buf += '<form id = ' + f"'{el.id}'" + '>' + \
           '<input type = "hidden" name = "tovar_id" id = "tovar_id" value = ' + f"'{el.id}'" + ' id = "minput"/><div class ="input-group">' + \
           '<span class ="input-group-text">Название</span><input type = "text" name = "tovar_name" ' + \
           f'id = "tovar_name" aria-label = "Название" class ="form-control" value="{el.name}"></div>'

    # color
    buf += '<div class ="input-group"><label class ="input-group-text" for ="inputGroupSelect01">Цвет</label><select ' + \
           'name = "cvet" id = "cvet" class ="form-control">'

    for color in colors:
        buf += f'<option value = "{color.id}"'
        if el.cvet == color.id:
            buf += 'selected'
        buf += f'>{color.name}</option>'
    buf += '</select></div>'

    # strana
    buf += '<div class ="input-group"><label class ="input-group-text" for ="inputGroupSelect01">Страна</label><select ' + \
           'name = "strana" id = "strana" class ="form-control">'

    for country in countries:
        buf += f'<option value = "{country.id}"'
        if el.strana == country.id:
            buf += 'selected'
        buf += f'>{country.name}</option>'
    buf += '</select></div>'

    # razmer
    buf += '<div class ="input-group"><label class ="input-group-text" for ="inputGroupSelect01">Размер</label><select ' + \
           'name = "razmer" id = "razmer" class ="form-control">'

    for size in sizes:
        buf += f'<option value = "{size.id}"'
        if el.razmer == size.id:
            buf += 'selected'
        buf += f'>Стандарт: {size.size_category.name} {size.name}</option>'
    buf += '</select></div>'

    # category
    buf += '<div class ="input-group"><label class ="input-group-text" for ="inputGroupSelect01">Страна</label><select ' + \
           'name = "category_id" id = "category_id" class ="form-control">'

    for category in categories:
        buf += f'<option value = "{category.id}"'
        if el.category_id == category.id:
            buf += 'selected'
        buf += f'>{category.name}</option>'
    buf += '</select></div>'

    # picture
    buf += '<div class ="input-group">' + \
           '<span class ="input-group-text">Изображение</span><input type = "text" name = "picture" ' + \
           f'id = "picture" aria-label = "Название" class ="form-control" value="{el.picture}"></div>'

    # opisanie
    buf += '<div class ="input-group">' + \
           '<input type = "text" name = "opisanie" ' + \
           f'id = "opisanie" aria-label = "Описание" class ="form-control" value="{el.opisanie}"></div>'

    # radio

    buf += '<div class ="form-check form-check-inline"><input '
    if el.sex == 2:
        buf += 'checked'
    buf += ' class ="form-check-input" type="radio" name="sex" id = "sex" value = "2"><label '
    buf += 'class ="form-check-label" for ="inlineRadio1">Для мужчин</label></div>'

    buf += '<div class ="form-check form-check-inline"><input '
    if el.sex == 1:
        buf += 'checked'
    buf += ' class ="form-check-input" type="radio" name="sex" id = "sex" value = "1"><label '
    buf += 'class ="form-check-label" for ="inlineRadio2">Для женщин</label></div>'

    buf += '<div class="d-grid gap-2 d-md-block">'
    buf += '<button onclick = "ajax_fun(this.form,' + "'editTovar'" + ');" class ="btn btn-outline-success" type="button" id="button-addon2">Сохранить</button>'
    buf += '<button onclick = "ajax_delete(this.form,' + "'deleteTovar'" + ');" class ="btn btn-outline-danger" type="button" id="button-addon2"> Удалить </button></div>'

    buf += '</form></div>' + '<div class="col-auto d-none d-lg-block">' + \
           f'<img src="{el.picture}" width="280" height="350">' \
           + '</svg>' + '</div>' + '</div>' + '</div>'
    return buf

# todo
# Фильтрация по нескольким атрибутам (2).