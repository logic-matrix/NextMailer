import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash
from app.controllers.main_controller import home
from app.controllers.settings_controller import service_settings
from .models import Customer, Service, Template, User
from .extensions import db, mail
from werkzeug.security import check_password_hash
from flask_login import login_required, current_user

main = Blueprint("main", __name__)
# Load .env variables
load_dotenv()
# Collect email settings from .env
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ["true", "1"]
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ["true", "1"]
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Fixed: tuple with name and email
MAIL_DEFAULT_SENDER = (
    "Logic Matrix",
    EMAIL_HOST_USER
)

# Initialize Flask-Mail instance
mail = Mail()

# Update Flask app config with email settings
def configure_mail(app):
    app.config.update(
        MAIL_SERVER=EMAIL_HOST,
        MAIL_PORT=EMAIL_PORT,
        MAIL_USE_TLS=EMAIL_USE_TLS,
        MAIL_USE_SSL=EMAIL_USE_SSL,
        MAIL_USERNAME=EMAIL_HOST_USER,
        MAIL_PASSWORD=EMAIL_HOST_PASSWORD,
        MAIL_DEFAULT_SENDER=MAIL_DEFAULT_SENDER
    )
    mail.init_app(app)
#######################################################################
@main.route("/", methods=["GET", "POST"])
def landing_page():
    return render_template("landing.html")

#######################################################################
@main.route("/login", methods=["GET", "POST"])
def index():
    return render_template("index.html")

#######################################################################
@main.route("/home", methods=["GET", "POST"])
##@login_required
def home_route():
    return home()
 
########################################################################
@main.route("/login_01", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Store user in session
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect("home")
        else:
            flash("Invalid email or password.", "danger")
            return redirect("/")
########################################################################
@main.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect("/")

################################################################################
@main.route("/subscribe", methods=["GET", "POST"])
##@login_required
def add_subscriber():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        service = request.form.get("service")
        description = request.form.get("description")

        # Validation
        if not name or not email or not service:
            flash("Name, Email, and Service are required!", "error")
            return redirect(subscribers)

        # Check for duplicate email
        if Customer.query.filter_by(email=email).first():
            flash("Email already subscribed!", "error")
            return redirect("subscribers")

        # Save to DB
        new_customer = Customer(
            name=name,
            email=email,
            service=service,
            description=description
        )
        db.session.add(new_customer)
        db.session.commit()

        flash("Subscription successful!", "success")
        return redirect("subscribers")

##########################################################################
    # GET request → render form
@main.route("/subscribers")
#@login_required
def subscribers():
    page = request.args.get("page", 1, type=int)
    subs = Customer.query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=5)
    services = Service.query.all()
    return render_template("subscriber.html", subscribers=subs, services=services)
#########################################################################
@main.route("/delete_subscriber/<int:subscriber_id>", methods=["POST"])
def delete_subscriber(subscriber_id):
    subscriber = Customer.query.get(subscriber_id)
    if subscriber:
        db.session.delete(subscriber)
        db.session.commit()
        flash("Subscriber deleted successfully!", "success")
        return redirect(url_for("main.subscribers"))

    else:
        flash("Subscriber not found!", "error")
        return redirect(url_for("main.subscribers"))


#########################################################################
@main.route("/users", methods=["POST"])
#@login_required
#@role_required('admin')
def add_user():
    data = request.get_json()
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User added!"}), 201

#########################################################################
@main.route("/user_list", methods=["GET"])
#@login_required
def users():
    users = User.query.all()

    data = []
    for user in users:
        data.append({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "service": user.service,
            "created_at": user.created_at,
            "description": user.description})

    return jsonify({"data": data})

##########################################################################
@main.route("/campaigns", methods=["GET", "POST"])
#@login_required
def campaigns():
    services = Service.query.all()
    Templates = Template.query.all()
    return render_template("campaigns.html", services=services, templates=Templates)
###########################################################################
@main.route("/start_campaign", methods=["GET", "POST"])
def start_campaign():
    campaign_name = request.form.get("campaign_name")
    subject = request.form.get("subject")
    recipient_list = request.form.get("recipient_list")
    template_name = request.form.get("template")
    schedule = request.form.get("schedule")

    print("Starting campaign with the following details:")
    print(campaign_name, subject, recipient_list, template_name, schedule)

    # Fetch template
    template = Template.query.filter_by(name=template_name).first()
    print("Fetched template:")
    print(template)
    if not template:
        flash("Selected template not found!", "error")
        return redirect(url_for("main.campaigns"))

    # Fetch recipients
    customers = Customer.query.filter_by(service=recipient_list).all()
    emails = [c.email for c in customers]
    if not emails:
        flash(f"No customers found for service '{recipient_list}'", "warning")
        return redirect(url_for("main.campaigns"))

    # Configure mail dynamically from .env
    configure_mail(current_app)

    # Build the email
    msg = Message(
        subject=subject,
        recipients=emails,
        html=template.final_html
    )

    try:
        mail.send(msg)
        flash(f"Campaign '{campaign_name}' sent successfully!", "success")
    except Exception as e:
        flash(f"Error sending email: {str(e)}", "danger")

    return redirect(url_for("main.campaigns"))

##########################################################################
@main.route("/send_email", methods=["GET", "POST"])
def send_email():
    # Configure mail dynamically from .env
    configure_mail(current_app)
    recepient = request.form.get("recipient")
    subject = request.form.get("subject")
    template_name = request.form.get("message")

    msg = Message(
        subject=subject,
        recipients=[recepient],
        html=template_name
    )

    try:
        mail.send(msg)
        flash("Email sent successfully!", "success")
    except Exception as e:
        flash(f"Error sending email: {str(e)}", "danger")

    return redirect(url_for("main.campaigns"))
####################################################################################
@main.route("/sms_campaigns", methods=["GET", "POST"])
#@login_required
def sms_campaigns():
    return render_template("sms_campaign.html")
####################################################################################
@main.route("/about")
def about():
    return "<h2>About Us</h2><p>This is the about page.</p>"


#####################################################################################
@main.route("/settings", methods=["GET", "POST"])
#@login_required
def settings():
    services = Service.query.all()
    users = User.query.all()
    return render_template("settings.html", services=services, users=users)
#####################################################################################
@main.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
        return redirect(url_for("main.settings"))

    else:
        flash("User not found!", "error")
        return redirect(url_for("main.settings"))
#####################################################################################
@main.route("/delete_service/<int:service_id>", methods=["POST"])
def delete_service(service_id): 
    service = Service.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!", "success")
        return redirect(url_for("main.settings"))

    else:
        flash("Service not found!", "error")
        return redirect(url_for("main.settings"))

#####################################################################################
@main.route("/add_service", methods=["POST"])
#@login_required
def add_service():
    if request.method == "POST":
        # Handle form submission
        name = request.form.get("name")

        if not name :
            flash("Name is required!", "error")
            return redirect(settings)

        if Customer.query.filter_by(name=name).first():
            flash("Service is already in use!", "error")
            return redirect(settings)
        
    service_settings(name)
    return redirect("settings")

@main.route("/services", methods=["GET"])
#@login_required

#############################################################################
@main.route("/add_admin", methods=["POST"])
#@login_required
def add_admin():
    if request.method == "POST":
        # Handle form submission
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if not name or not email or not password or not role:
            flash("All fields are required!", "error")
            return redirect(add_admin)

        if User.query.filter_by(email=email).first():
            flash("Email is already in use!", "error")
            return redirect(add_admin)
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_admin = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )
        print(new_admin)
        db.session.add(new_admin)
        db.session.commit()
        flash("Admin added successfully!", "success")
        return redirect("settings")



#####################################################################################
@main.route("/templates_list", methods=["GET", "POST"])
#@login_required
def templates():
    templates = Template.query.all()
    return render_template("templates_list.html", templates=templates)

####################################################################################
@main.route("/delete_template/<int:id>", methods=["POST"])
def delete_template(id):
    template = Template.query.get(id)
    if template:
        db.session.delete(template)
        db.session.commit()
        flash("Template deleted successfully!", "success")
        return redirect(url_for("main.templates_list"))

    else:
        flash("Template not found!", "error")
        return redirect(url_for("main.templates_list"))

####################################################################################
@main.route("/add_template", methods=["GET", "POST"])
def builder():
    if request.method == "POST":
        name = request.form.get("name")
        final_html = request.form.get("final_html")

        if not name or not final_html:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("main.builder"))

        new_template = Template(name=name, final_html=final_html)
        db.session.add(new_template)
        db.session.commit()

        flash("Template saved successfully!", "success")
        return redirect("templates")

    return redirect("main.builder")

############################################################################
@main.route("/templates", methods=["GET", "POST"])
def list_templates():
    templates = Template.query.order_by(Template.created_at.desc()).all()
    return render_template("templates.html", templates=templates)

############################################################################
@main.route("/external_template", methods=["GET", "POST"])
def external_template():
    if request.method == "POST":
        name = request.form.get("name")
        final_html = request.form.get("final_html")

        # Use your model class Template
        data = Template(
            name=name,
            final_html=final_html
        )

        db.session.add(data)
        db.session.commit()

        flash("Template saved successfully!", "success")
        return redirect(url_for("main.templates"))  # use url_for for safety
    else:
        return render_template("save_external_template.html")
#############################################################################
@main.route("/ai_templates", methods=["GET", "POST"])
def ai_templates():
    user_prompt = None
    if request.method == "POST":
        user_prompt = request.form.get("prompt")
    
    return render_template("template_ai.html", user_prompt=user_prompt)
 
############################################################################
@main.route("/forms", methods=["GET"])
#@login_required
def forms():
    return render_template("forms.html")

############################################################################
@main.route("/uploads", methods=["GET"])
def uploads():
    return render_template("uploads.html")