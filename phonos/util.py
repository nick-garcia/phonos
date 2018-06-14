import csv
import phonenumbers

from phonos import model

from collections import namedtuple

def import_numbers(file, filetype):
    if not file:
        raise FileNotFoundError("You need to provide a file to import!")
    if not filetype:
        raise TypeError("You must provide the type of the file to import!")
    elif filetype not in ("Avaya", "Cisco", "mobile"):
        raise TypeError("The filetype argument must be one of Avaya, Cisco or mobile.")

    reader = csv.DictReader(file)
    if filetype == "Avaya":
        return import_avaya_numbers(reader)
    elif filetype == "Cisco":
        return import_cisco_numbers(reader)
    elif filetype == "mobile":
        return import_mobile_numbers(reader)

    raise RuntimeError("Something went wrong and I didn't recognize the type of file you are importing.")

def import_avaya_numbers(file, country="US"):
    country_lookup = get_country_lookups()

    records = 0
    for row in file:
        firstname, lastname = row['Name'].split()
        person = model.Person.query.filter_by(firstname=firstname, lastname=lastname).first()
        if not person:
            person = model.Person(firstname=firstname, lastname=lastname)

        extra = {
            "phone_type" : row["Type"],
            "room" : row["Room"],
            "floor" : row["Floor"],
            "building" : row["Building"]
        }

        number = model.PhoneNumber(
            number=row["Extension"],
            type="Avaya",
            country=country_lookup.by_code[country],
            person = person,
            extra = extra
        )

        model.db.session.add(number)
        records += 1

    model.db.session.commit()
    return records

def import_cisco_numbers(file):
    raise NotImplementedError("Importing phone numbers from Cisco has not been implemented yet.")

def import_mobile_numbers(file):
    country_lookup = get_country_lookups()

    records = 0
    for row in file:
        lastname, firstname = row['name'].split(', ')
        person = model.Person.query.filter_by(firstname=firstname, lastname=lastname).first()
        if not person:
            person = model.Person(firstname=firstname, lastname=lastname)

        if len(row["country"]) == 2:
            country = country_lookup.by_code[row["country"]]
            country_code = row["country"]
        else:
            country = country_lookup.by_name.get(row['country'], 'Unknown')
            country_code = country_lookup.code_by_name[row['country']]

        parsed_number = phonenumbers.parse(row['number'], country_code)
        extra = {
            'carrier' : row['carrier'],
            'device_type' : row['devicetype']
        }

        number = model.PhoneNumber(
            number=phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            type="mobile",
            country=country,
            person=person,
            extra=extra
        )

        model.db.session.add(number)
        records += 1

    model.db.session.commit()
    return records

CountryLookup = namedtuple("CountryLookup", ["by_code", "by_name", "code_by_name"])
def get_country_lookups():
    by_code = {}
    by_name = {}
    code_by_name = {}

    for country in model.Country.query:
        by_code[country.code] = country
        by_name[country.name] = country
        code_by_name[country.name] = country.code

    return CountryLookup(by_code=by_code, by_name=by_name, code_by_name=code_by_name)