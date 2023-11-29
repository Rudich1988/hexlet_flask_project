import json
import os
from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages, make_response, session
import html
from hexlet_flask_project.modules.data import Repository
from hexlet_flask_project.modules.validator import validate


filepath = 'tests/fixtures/data.json'



# Это callable WSGI-приложение
app = Flask(__name__)


app.secret_key = "secret_key"
app.config['SECRET_KEY'] = 'fghjkoijmnbhjk000-=lkjhgkmhgfdxcvbhjm,'


@app.route('/')
def hello_world():
    return render_template('users/hello.html')


@app.route('/users/')
def search_users():
    user_logged = session.get('login_user')
    finish = request.cookies.get('user')
    name = request.args.get('name', '')
    data_user = request.cookies.get('user', json.dumps({'id': ''}))
    data = json.loads(data_user)
    if len(data) == 1:
        data['role'] = ''
    repo = Repository(filepath)
    users = repo.get_data()
    filtered_users = []
    for user in users:
        if name.lower() in user['name'].lower():
            filtered_users.append(user)
    messages = get_flashed_messages(with_categories=True)
    print(messages)
    return render_template('users/index.html', users=filtered_users,
                           search=html.escape(name), messages=messages,
                           role=data['role'], finish=finish, user_logged=user_logged)


@app.route('/users/<id>/')
def get_user(id):
    #id = json.loads(request.cookies.get('user'))['id']
    user = Repository(filepath).find(id)
    return render_template('users/show.html', user=user, id=id)


@app.post('/users/new')
def create_user():
    repo = Repository(filepath)
    users= repo.get_data()
    user = request.form.to_dict()
    errors = validate(user)
    if errors:
        return render_template('users/new.html', user=user, errors=errors), 422
    if users == []:
        user['id'] = 1
    else:
        result = []
        for person in users:
            result.append(person['id'])
        user['id'] = max(result) + 1
    users.append(user)
    repo.save(users)
    flash('User was added successfully', 'success')
    user_id = {'id': str(user['id'])}
    response = make_response(redirect(url_for('search_users'), code=302))
    response.set_cookie('user', json.dumps(user_id))
    return response


@app.get('/users/new')
def show_form():
    user = {
        'name': '',
        'email': ''
    }
    errors={}
    return render_template('users/new.html', user=user, errors=errors)


@app.get('/users/<id>/edit')
def edit_user(id):
    user = Repository(filepath).find(id)
    errors = {}
    return render_template('users/edit.html', user=user, errors=errors, id=int(id))


@app.route('/users/<id>/patch', methods=['POST'])
def patch_user(id):
    repo = Repository(filepath)
    users = repo.get_data()
    correct_user = request.form.to_dict()
    errors = validate(correct_user)
    if errors:
        return render_template('user/edit.html', user=correct_user, errors=errors), 422
    for user in users:
        if user['id'] == int(id):
            user['name'] = correct_user['name']
            user['email'] = correct_user['email']
    repo.save(users)
    flash('User has been updated', 'success')
    return redirect(url_for('search_users'))   


@app.route('/users/<id>/delete', methods=['POST'])
def delete_user(id):
    repo = Repository(filepath)
    repo.delete(id)
    flash('User has been delete')
    return redirect(url_for('search_users'))



@app.get('/users/superuser-show')
def show_superuser_form():
    password = {'password': ''}
    errors = {}
    return render_template('users/create_superuser.html', password=password, errors=errors)


@app.route('/users/superuser-create', methods=['POST'])
def create_superuser():
    data = json.loads(request.cookies.get('user'))
    password = request.form.get('password')
    true_password = 'I am superuser'
    if password != true_password:
        errors = {'password': 'password is not right'}
        return render_template('users/create_superuser.html', password=password, errors=errors)
    if password == true_password:
        repo = Repository(filepath)
        users = repo.get_data()
        for user in users:
            if user['id'] == int(data['id']):
                user['role'] = 'admin'
        repo.save(users)
        response = make_response(redirect(url_for('search_users')))
        data['role'] = 'admin'
        response.set_cookie('user', json.dumps(data))
        return response


@app.get('/users/login')
def show_login_form():
    email = {
        'email': ''
    }
    errors = {}
    return render_template('users/login.html', email=email, errors=errors)


@app.route('/users/login', methods=["POST"])
def login():
    repo = Repository(filepath)
    users = repo.get_data()
    email_data = []
    for user in users:
        email_data.append(user['email'])
    correct_email = request.form.get('email')
    if correct_email not in email_data:
        return render_template('users/login.html', email=correct_email, errors={'email': 'email is not correct'})
    for person in users:
        if person['email'] == correct_email:
            user = person
            break
    session['login_user'] = user
    if 'role' in user.keys():
        final_cookie = {'id': user['id'], 'role': user['role']}
    else:
        final_cookie = {'id': user['id']}
    response = make_response(redirect(url_for('search_users'), code=302))
    response.set_cookie('user', json.dumps(final_cookie))
    return response


@app.route('/users/logout', methods=['POST', 'DELETE'])
def logout():    
    session.clear()
    return render_template('users/hello.html')



if __name__ == '__main__':
    app.run()