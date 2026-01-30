from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

DAYS_OF_WEEK = {1: 'Poniedziałek', 2: 'Wtorek', 3: 'Środa', 4: 'Czwartek', 5: 'Piątek', 6: 'Sobota', 7: 'Niedziela'}

TASK_COLORS_BY_DAYS = {
    1: {'background': '#fcece9 0%, #cbe2f7 100%', 'font_color': '#000000'},
    2: {'background': '#f9e5e1 0%, #fcece9 100%', 'font_color': '#000000'},
    3: {'background': '#f5a898 0%, #f9e5e1 100%', 'font_color': '#000000'},
    4: {'background': '#ea8367 0%, #f5a898 100%', 'font_color': '#000000'},
    5: {'background': '#ff0000 0%, #ea8367 100%', 'font_color': '#FFFFFF'},
    6: {'background': '#3B150C 0%, #ff0000 100%', 'font_color': '#FFFFFF'},
}

db = SQLAlchemy()


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(4000))
    result = db.Column(db.String(4000))
    goal_day_of_week = db.Column(db.Integer, default=1)
    goal_datetime = db.Column(db.DateTime, default=datetime.utcnow())
    goal_deadline_date = db.Column(db.Date)
    goal_achieved = db.Column(db.Boolean, default=False)
    goal_cyclic_weekly = db.Column(db.Boolean, default=True)
    goal_cyclic_daily = db.Column(db.Boolean, default=True)
    goal_one_day_only = db.Column(db.Boolean, default=True)
    carried_over_if_not_achieved = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
