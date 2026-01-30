"""
 Copyright (C) 2025 Wojciech Szyba - All Rights Reserved
 You may use, distribute and modify this code under the
 terms of the GNU GENERAL PUBLIC LICENSE license,
 You should have received a copy of the license with
 this file. If not, please visit :
 https://github.com/wojciech-szyba/siedmiodniowe-cele/blob/main/LICENSE
 */
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from .models import Goal, User, db, DAYS_OF_WEEK, TASK_COLORS_BY_DAYS
from datetime import datetime, timedelta
from .login import LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///goals.db"
app.config['SECRET_KEY'] = '...'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return
    except Exception as e:
        print(str(e))


@app.route("/", defaults={"week_start_date": None, "week_end_date": None}, methods=['GET'])
@app.route("/<week_start_date>/<week_end_date>", methods=['GET'])
@login_required
def main(week_start_date, week_end_date):
    print(f"current_user.is_authenticated: {current_user.is_authenticated}, user_id: {current_user.get_id()}")
    today = datetime.now()
    today_day_of_week_number = today.weekday() + 1
    current_week_start_date = today - timedelta(days=today.weekday()) if not week_start_date else datetime.strptime(week_start_date, "%Y-%m-%d")
    current_week_end_date = current_week_start_date + timedelta(days=6) if not week_end_date else datetime.strptime(week_end_date, "%Y-%m-%d")
    try:
        goals = db.session.execute(db.select(Goal).where(Goal.name == Goal.name)).scalars()
        goals = goals.all()
        for goal in goals:
            goal_dt = goal.goal_datetime
            if not (goal_dt >= current_week_start_date and goal_dt <= current_week_end_date):
                goals.remove(goal)
            if goal.goal_deadline_date:
                if goal.goal_deadline_date < datetime.now():
                    if not goal.carried_over_if_not_achieved:
                        goals.remove(goal)
    except Exception as e:
        print(str(e))
        goals = []
    return render_template('index.html', days_of_week=DAYS_OF_WEEK, goals=goals,
                           task_colors_by_days=TASK_COLORS_BY_DAYS, today_day_of_week_number=today_day_of_week_number,
                           weekly=True, start_week=current_week_start_date.strftime('%Y-%m-%d'),
                           end_week=current_week_end_date.strftime('%Y-%m-%d'))


@app.route('/week_ago/<week_start_date>', methods=['GET'])
@login_required
def week_ago_grid(week_start_date):
    week_ago = datetime.strptime(week_start_date, "%Y-%m-%d") - timedelta(days=7)
    end_date = datetime.strptime(week_start_date, "%Y-%m-%d") - timedelta(days=1)
    return redirect(url_for('main', week_start_date=week_ago.strftime('%Y-%m-%d'),
                            week_end_date=end_date.strftime('%Y-%m-%d')))


@app.route('/next_week/<week_start_date>', methods=['GET'])
@login_required
def next_week_grid(week_start_date):
    next_week = datetime.strptime(week_start_date, "%Y-%m-%d") + timedelta(days=7)
    next_week_end = datetime.strptime(week_start_date, "%Y-%m-%d") + timedelta(days=14)
    return redirect(url_for('main', week_start_date=next_week.strftime('%Y-%m-%d'),
                            week_end_date=next_week_end.strftime('%Y-%m-%d')))


@app.route('/daily', methods=['GET'])
@login_required
def daily_grid():
    today_day_of_week_number = datetime.now().weekday() + 1
    try:
        goals = db.session.execute(db.select(Goal)).scalars()
        goals = goals.all()
    except Exception as e:
        print(str(e))
        goals = []
    return render_template('index.html', days_of_week=DAYS_OF_WEEK, goals=goals,
                           task_colors_by_days=TASK_COLORS_BY_DAYS, today_day_of_week_number=today_day_of_week_number,
                           weekly=False)


@app.route('/add_goal/<int:day_of_week>/', methods=['GET', 'POST'])
@login_required
def insert_goal(day_of_week):
    if request.method == 'POST':
        is_goal_cyclic_weekly = True if request.form.get("goal_cyclic_weekly", 0) == "on" else False
        is_goal_cyclic_daily = True if request.form.get("goal_cyclic_daily", 0) == "on" else False
        is_carried_over_if_not_achieved = True if request.form.get("carried_over_if_not_achieved", 0) == "on" else False
        last_day_goal_present = day_of_week if not is_goal_cyclic_daily else 7
        for day in range(day_of_week, last_day_goal_present + 1):
            goal = Goal(name=request.form['name'], description=request.form['description'],
                        result=request.form['result'], goal_day_of_week=day,
                        goal_cyclic_weekly=is_goal_cyclic_weekly,
                        goal_cyclic_daily=is_goal_cyclic_daily,
                        carried_over_if_not_achieved=is_carried_over_if_not_achieved)
            db.session.add(goal)
            db.session.commit()

        return redirect(url_for('main'))
    else:
        return render_template('new.html', day_of_week=day_of_week, goal=None)


@app.route('/update_goal/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    goal = db.get_or_404(Goal, id)
    if request.method == 'POST':
        goal.name = request.form['name']
        goal.description = request.form['description']
        goal.result = request.form['result']
        goal.goal_cyclic_weekly = True if request.form.get("goal_cyclic_weekly", False) == "on" else False
        goal.goal_cyclic_weekly = True if request.form.get("goal_cyclic_daily", False) == "on" else False
        goal.carried_over_if_not_achieved = True if request.form.get("carried_over_if_not_achieved", False) == "on" \
            else False
        db.session.commit()
        return redirect(url_for('main'))
    else:
        goal = db.get_or_404(Goal, id)
        return render_template('new.html', day_of_week=goal.goal_day_of_week, goal=goal)


@app.route('/delete_goal/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    goal = db.get_or_404(Goal, id)
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for('main'))


@app.route('/goal_achieved/<int:id>', methods=['GET', 'POST'])
@login_required
def set_achieved(id):
    goal = db.get_or_404(Goal, id)
    if goal.goal_achieved == 1:
        print(f'Goal id: {id} set to not achieved')
        goal.goal_achieved = 0
    else:
        print(f'Goal id: {id} set to achieved')
        goal.goal_achieved = 1
    db.session.commit()
    return redirect(url_for('main'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            if form.email.data != 'test@test.pl':
                flash('User does not exists!')
                return render_template('login.html', form=form)
        if user.check_password(form.password.data):
            is_success = login_user(user, remember=form.remember_me.data)
            if is_success:
                next_page = request.args.get('next') if request.args.get('next') != '/' else None
                return redirect(next_page) if next_page else redirect(url_for('main'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))


def move_goals_from_previous_day():
    pass


if __name__ == "__main__":
    app.run()
