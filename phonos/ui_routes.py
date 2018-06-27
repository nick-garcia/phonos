from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from phonos import app, util, model

@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.PhoneNumber.query.join(model.Person, model.PhoneNumber.person).order_by(model.Person.firstname, model.Person.lastname)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('index.html', pagination=pagination)

@app.route('/login.html')
def login_html():
    return render_template('login.html', next_url=request.args.get('next', ''))

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_html'))

    username = request.form['phonos_username']
    password = request.form['phonos_password']
    next_url = request.form.get('next')

    user = model.User.query.filter_by(username=username).first()
    if not user or not user.valid_password(password):
        flash('Invalid username or password.')
        return redirect(url_for('login_html'))

    login_user(user)
    return redirect(next_url or url_for('index_html'))

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login_html'))

@app.route('/people.html')
@login_required
def people():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.Person.query.order_by(model.Person.firstname, model.Person.lastname)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('people.html', pagination=pagination)

@app.route('/person/<person_id>')
@login_required
def person(person_id):
    person = model.Person.query.filter(model.Person.id == person_id).first_or_404()

    return render_template('person.html', person=person)

@app.route('/country/<country_id>', methods=['GET', 'POST'])
@login_required
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

@app.route('/countries.html')
@login_required
def countries():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.Country.query.order_by(model.Country.name)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('countries.html', pagination=pagination)

@app.route('/import.html', methods=['GET', 'POST'])
@login_required
def import_html():
    imported = 0
    if request.method == 'POST':
        csvfile = request.files['csvfile']
        filetype = request.form['filetype']

        csvfile = [x.decode() for x in csvfile]
        imported = util.import_numbers(csvfile, filetype)
        
    return render_template('import.html', imported=imported)
