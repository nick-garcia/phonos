import datetime

from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.orm import aliased
from werkzeug.security import generate_password_hash

from phonos import app, util, model


def admin_required(wrapped_fn):
    """ A decorator to ensure that the logged in user is an admin. """
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return abort(401)
        else:
            return wrapped_fn(*args, **kwargs)

    return wrapper

@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    review_query = model.PhoneNumber.query.filter(model.PhoneNumber.needs_review == True)
    query = model.PhoneNumber.query.join(model.PhoneAssignee, model.PhoneNumber.assigned_to).order_by(model.PhoneAssignee.name)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('index.html', pagination=pagination, reviewable=review_query.count())

@app.route('/login.html')
def login_html():
    return render_template('login.html', next_url=request.args.get('next', ''))

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index_html'))

    username = request.form['phonos_username']
    password = request.form['phonos_password']
    next_url = request.form.get('next')

    user = model.User.query.filter_by(username=username).first()
    if not user or not user.valid_password(password):
        flash('Invalid username or password.')
        return redirect(url_for('login_html'))

    login_user(user)
    session['is_admin'] = user.is_admin
    return redirect(next_url or url_for('index_html'))

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login_html'))

@login_required
@app.route('/assignees.html')
def assignees():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.PhoneAssignee.query.order_by(model.PhoneAssignee.name)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('assignees.html', pagination=pagination)

@login_required
@app.route('/assignee/<assignee_id>')
def assignee(assignee_id):
    assignee = model.PhoneAssignee.query.filter(model.PhoneAssignee.id == assignee_id).first_or_404()

    return render_template('assignee.html', assignee=assignee)

@login_required
@app.route('/country/<country_id>', methods=['GET', 'POST'])
def country(country_id):
    country = model.Country.query.filter(model.Country.id == country_id).first_or_404()
    updated = False

    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        
        country.name = name
        country.code = code
        model.db.session.commit()

        updated = True

    return render_template('country.html', country=country, updated=updated)

@login_required
@app.route('/countries.html')
def countries():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.Country.query.order_by(model.Country.name)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('countries.html', pagination=pagination)

@login_required
@app.route('/import.html', methods=['GET', 'POST'])
def import_html():
    imported = 0
    if request.method == 'POST':
        try:
            csvfile = request.files['csvfile']

            csvfile = [x.decode(errors='ignore') for x in csvfile]
            imported = util.import_numbers(csvfile)
            flash(f'Successfully imported {imported} numbers!')
        except RuntimeError as e:
            flash(str(e))
            return redirect(url_for('import_html'))
        
    return render_template('import.html')

@login_required
@admin_required
@app.route('/users.html')
def users():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.User.query.order_by(model.User.username)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('users.html', pagination=pagination)

@login_required
@admin_required
@app.route('/user/<user_id>', methods=['POST', 'GET', 'DELETE'])
def user(user_id):
    user = model.User.query.filter(model.User.id == user_id).first_or_404()

    if request.method == 'DELETE':
        model.db.session.delete(user)
        model.db.session.commit()

        flash(f'User {user.username} deleted!')
        return 'Deleted!'

    elif request.method == 'POST':
        new_password = request.form['new_password']
        is_admin = request.form.get('is_admin', False)

        if new_password:
            user.password = generate_password_hash(new_password)
        user.is_admin = bool(is_admin)

        model.db.session.add(user)
        model.db.session.commit()

        flash(f'User {user.username} updated!')

    return render_template('user.html', user=user)

@login_required
@admin_required
@app.route('/user/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'GET':
        return render_template('user.html', new_user=True)
    elif request.method == 'POST':
        username = request.form.get('new_username')
        password = request.form.get('new_password')
        is_admin = request.form.get('is_admin', False)
        has_error = False

        if not username:
            has_error = True
            flash('A username is required to create a user.')

        if not password:
            has_error = True
            flash('A password is required to create a user.')

        # Check for duplicate username
        user = model.User.query.filter_by(username=username).first()
        if user:
            has_error = True
            flash(f'User {username} already exists!')

        if has_error:
            return render_template('user.html', new_user=True)

        user = model.User()
        user.username = username
        user.password = generate_password_hash(password)
        user.is_admin = bool(is_admin)

        model.db.session.add(user)
        model.db.session.commit()

        flash(f'User {username} successfully created!')
        return redirect(url_for('users'))

@login_required
@admin_required
@app.route('/groups.html')
def groups():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.Group.query.order_by(model.Group.name)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('groups.html', pagination=pagination)

@login_required
@admin_required
@app.route('/group/new', methods=['GET', 'POST'])
def new_group():
    if request.method == 'GET':
        users = model.User.query.order_by(model.User.username)
        return render_template('group.html', users=users, new_group=True)
    elif request.method == 'POST':
        name = request.form.get('new_group_name')
        desc = request.form.get('description')
        members = model.User.query.filter(model.User.id.in_(request.form.getlist('members'))).all()

        group = model.Group.query.filter_by(name=name).first()
        if group:
            flash(f'A group named {name} already exists!')
            users = model.User.query.order_by(model.User.username)
            return render_template('group.html', users=users, new_group=True)

        group = model.Group()
        group.name = name
        group.description = desc
        group.users = members

        model.db.session.add(group)
        model.db.session.commit()

        flash(f'{name} successfully created!')
        return redirect(url_for('groups'))

@login_required
@admin_required
@app.route('/group/<group_id>', methods=['POST', 'GET', 'DELETE'])
def group(group_id):
    group = model.Group.query.filter(model.Group.id == group_id).first_or_404()
    users = model.User.query.order_by(model.User.username).all()

    if request.method == 'GET':
        members = [m.id for m in group.users]

        return render_template('group.html', group=group, users=users, members=members)
    elif request.method == 'POST':
        name = request.form.get('new_group_name')
        desc = request.form.get('description')
        members = model.User.query.filter(model.User.id.in_(request.form.getlist('members'))).all()

        group.name = name
        group.description = desc
        group.users = members

        model.db.session.add(group)
        model.db.session.commit()

        flash(f'Group updated!')
        return render_template('group.html', group=group, users=users, members=[m.id for m in members])
    elif request.method == 'DELETE':
        model.db.session.delete(group)
        model.db.session.commit()

        flash(f'{group.name} successfully deleted.')
        return "Deleted!"

@login_required
@admin_required
@app.route('/review.html')
def review_html():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)
    Conflict = aliased(model.PhoneAssignee)
    ConflictNumber = aliased(model.PhoneNumber)

    query = model.PhoneNumber.query.filter(model.PhoneNumber.needs_review == True).join(model.PhoneAssignee)
    query = query.join(Conflict, Conflict.name == model.PhoneAssignee.name).filter(Conflict.id != model.PhoneAssignee.id)
    query = query.join(ConflictNumber, Conflict.id == ConflictNumber.assignee_id)
    query = query.add_entity(ConflictNumber)

    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('review.html', pagination=pagination)

@login_required
@admin_required
@app.route('/reviews/process', methods=['POST'])
def reviews_process():
    actions = request.form.getlist('action')
    now = datetime.datetime.now()

    for action in actions:
        if action.startswith('delete'):
            act, id = action.split('|')
            conflict = model.PhoneNumber.query.filter_by(id=id).first()
            model.db.session.delete(conflict)
        elif action.startswith('merge'):
            act, conflict_id, merge_id = action.split('|')
            conflict = model.PhoneNumber.query.filter_by(id=conflict_id).first()
            original = model.PhoneNumber.query.filter_by(id=merge_id).first()

            model.db.session.delete(conflict.assigned_to)
            conflict.assigned_to = original.assigned_to
            conflict.needs_review = False
            conflict.updated = now
            model.db.session.add(conflict)
        elif action.startswith('replace'):
            act, conflict_id, merge_id = action.split('|')
            conflict = model.PhoneNumber.query.filter_by(id=conflict_id).first()
            original = model.PhoneNumber.query.filter_by(id=merge_id).first()

            model.db.session.delete(original)
            conflict.needs_review = False
            conflict.updated = now
            model.db.session.add(conflict)
        elif action.startswith('save'):
            act, conflict_id = action.split('|')
            conflict = model.PhoneNumber.query.filter_by(id=conflict_id).first()

            conflict.needs_review = False
            conflict.updated = now
            model.db.session.add(conflict)

    model.db.session.commit()
    return redirect(url_for('review_html'))
