from flask import render_template, request
from phonos import app, util, model

@app.route('/')
@app.route('/index.html')
def index_html():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.PhoneNumber.query.join(model.Person, model.PhoneNumber.person).order_by(model.Person.firstname, model.Person.lastname)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('index.html', pagination=pagination)

@app.route('/people.html')
def people():
    page = request.args.get('page', 1)
    qty = request.args.get('qty', 20)

    query = model.Person.query.order_by(model.Person.firstname, model.Person.lastname)
    pagination = query.paginate(page=int(page), per_page=int(qty))

    return render_template('people.html', pagination=pagination)

@app.route('/person/<person_id>')
def person(person_id):
    person = model.Person.query.filter(model.Person.id == person_id).first_or_404()

    return render_template('person.html', person=person)

@app.route('/import.html', methods=['GET', 'POST'])
def import_html():
    imported = 0
    if request.method == 'POST':
        csvfile = request.files['csvfile']
        filetype = request.form['filetype']

        csvfile = [x.decode() for x in csvfile]
        imported = util.import_numbers(csvfile, filetype)
        
    return render_template('import.html', imported=imported)
