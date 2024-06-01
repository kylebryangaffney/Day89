from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
Bootstrap5(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tasks.db"
db = SQLAlchemy(app)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    priority = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

with app.app_context():
    db.create_all()

class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('Less Important', 'Less Important'),
        ('Important', 'Important'),
        ('Critical', 'Critical')
    ], validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.today)
    description = StringField('Description', validators=[DataRequired()])
    completed = BooleanField("Completed")
    submit = SubmitField('Submit')

@app.context_processor
def inject_year():
    return {'year': datetime.now().year}

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            name=form.name.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            description=form.description.data,
            completed=form.completed.data
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_task.html', form=form)

@app.route('/delete')
def delete_task():
    task_id = request.args.get('id')
    task_to_delete = Task.query.get_or_404(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.name = form.name.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data
        task.description = form.description.data
        task.completed = form.completed.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_task.html', form=form, is_edit=True)

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)
