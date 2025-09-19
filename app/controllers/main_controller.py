from flask import render_template
from app.models import Customer, Template


def home():
    data = Customer.query.count()   
    template = Template.query.count()
    return render_template("home.html", customers=data, templates=template)