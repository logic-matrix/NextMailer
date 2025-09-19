"""from flask import flash, redirect, render_template, request, url_for
from app.models import Customer
from app.routes import subscribers
from ..extensions import db


def all_subscriber():
    subscribers = Customer.query.all()
    data = []
    for subscriber in subscribers:
        data.append({
            "id": subscriber.id,
            "email": subscriber.email,
            "created_at": subscriber.created_at
        })
    return render_template("subscribers.html", subscribers=data)


def add_subscriber(name, email, service, description):
    # Validation
        if not name or not email or not service:
            flash("Name, Email, and Service are required!", "error")
            return redirect(subscribers)

        # Check for duplicate email
        if Customer.query.filter_by(email=email).first():
            flash("Email already subscribed!", "error")
            return redirect(subscribers)

        # Save to DB
        new_customer = Customer(
            name=name,
            email=email,
            service=service,
            description=description
        )
        db.session.add(new_customer)
        db.session.commit()

        return redirect(subscribers, message="Subscription successful!", status=200)
        """
