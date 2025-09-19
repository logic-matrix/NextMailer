import os
from flask import Flask, render_template
from .config import Config
from .extensions import db, migrate, mail
from .routes import main
from flask_mail import Mail
 
"""
#Custom Path setup 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")  # <- your custom folder
)
app.register_blueprint(main)



#Custom Path setup 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")  # <- your custom folder
)
from .routes import main
app.register_blueprint(main)

"""


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize Flask-Mail
    mail.init_app(app)
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .models import User, Customer

    
    return app

 