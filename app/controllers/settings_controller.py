from flask import flash
from ..extensions import db
from app.models import Service

def service_settings(name):
    try:
        data = Service(
            name=name
        )
        db.session.add(data)
        db.session.commit()
        flash("Service added successfully!", "success")
        return "Service added successfully!"   # explicit return
    except Exception as e:
        db.session.rollback()  # rollback in case of error
        flash(f"Error: {str(e)}", "danger")
        return f"Error: {str(e)}"


#All services 
def get_all_services():
    try:
        services = Service.query.all()
        return services
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return []