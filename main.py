from flask import Flask, render_template, request, redirect, flash, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, URL
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap(app)

# setup login manager
login_manager = LoginManager()
login_manager.init_app(app)

# connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes-2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##Cafe TABLE Configuration
class User(UserMixin, db.Model):
    __tablename__ = "user_list"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()

class RegistrationForm(FlaskForm):
    email = StringField('Your Email', validators=[InputRequired()])
    password = StringField('Enter a Password', validators=[InputRequired()])
    name = StringField('Your Name', validators=[InputRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Your Email', validators=[InputRequired()])
    password = StringField('Enter a Password', validators=[InputRequired()])
    submit = SubmitField('Log In')

class CafeForm(FlaskForm):
    cafe_name = StringField('Cafe name', validators=[InputRequired()])
    map_url = StringField('Cafe Location on Google Maps (URL)', validators=[InputRequired(), URL()])
    image_url = StringField('Image of Cafe (URL)', validators=[InputRequired(), URL()])
    location = StringField('Suburb', validators=[InputRequired()])
    has_sockets = SelectField('Has power sockets', choices=['Yes', 'No'])
    has_toilet = SelectField('Has toilets', choices=['Yes', 'No'])
    has_wifi = SelectField('Has wifi', choices=['Yes', 'No'])
    can_take_calls = SelectField('Can take calls', choices=['Yes', 'No'])
    seats = SelectField('Number of seats', choices=['0-10', '10-20', '20-30', '30-40', '40-50', '50+'], validators=[InputRequired()])
    coffee_price = StringField('Coffee price', validators=[InputRequired()])
    submit = SubmitField('Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(403)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")


# ## HTTP GET - Read Record (GET is allowed by default on all routes)
# @app.route("/random")
# def get_random_cafe():
#     cafes = Cafe.query.all()
#     random_cafe = random.choice(cafes)
#     print(random_cafe)
#     return jsonify(random_cafe.to_dict())
#
#
@app.route("/all")
def get_all_cafes():
    all_cafes = Cafe.query.all()
    return render_template("cafes.html", all_cafes=all_cafes)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_name = request.form['name']
        new_password = request.form['password']
        hash_password = generate_password_hash(new_password, 'pbkdf2:sha256', salt_length=8)
        new_email = request.form['email']
        # check if email already in db
        check_user = User.query.filter_by(email=new_email).first()
        if not check_user:
            new_user = User(name=new_name, password=hash_password, email=new_email)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_cafes'))
        else:
            flash('There is already an account with that email. Please log in.')
            return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_email = request.form['email']
        login_password = request.form['password']
        # check if email is in db
        user = User.query.filter_by(email=login_email).first()
        if not user:
            flash('That email does not exist. Try again.')
            return redirect(url_for('login'))
        else:
            # check if password matches
            if check_password_hash(user.password, login_password):
                login_user(user)
                return redirect(url_for('get_all_cafes'))
            else:
                flash('Incorrect password. Try again')
                return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#
# @app.route("/search")
# def find_cafe():
#     query_location = request.args.get("loc").title()
#     cafes = Cafe.query.filter_by(location=query_location).all()
#     if len(cafes) > 0:
#         return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
#     else:
#         return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Create Record
@app.route("/add", methods=["GET","POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        print("True")
        new_cafe = Cafe(
            name=request.form['cafe_name'],
            map_url=request.form['map_url'],
            img_url=request.form['image_url'],
            location=request.form['location'],
            has_sockets=request.form['has_sockets'],
            has_toilet=request.form['has_toilet'],
            has_wifi=request.form['has_wifi'],
            can_take_calls=request.form['can_take_calls'],
            seats=request.form['seats'],
            coffee_price=request.form['coffee_price']
        )
        db.session.add(new_cafe)
        db.session.commit()
        # return jsonify(response={"Success": "successfully added the new cafe."})
        return redirect(url_for('get_all_cafes'))
    return render_template('add.html', form=form)

#
# ## HTTP PUT/PATCH - Update Record
@app.route("/edit-cafe/<int:cafe_id>", methods=["GET", "POST", "PATCH"])
def edit_cafe(cafe_id):
    cafe_to_edit = Cafe.query.get(cafe_id)
    edit_form = CafeForm(
        cafe_name=cafe_to_edit.name,
        map_url=cafe_to_edit.map_url,
        image_url=cafe_to_edit.img_url,
        location=cafe_to_edit.location,
        has_sockets=cafe_to_edit.has_sockets,
        has_toilet=cafe_to_edit.has_toilet,
        has_wifi=cafe_to_edit.has_wifi,
        can_take_calls=cafe_to_edit.can_take_calls,
        seats=cafe_to_edit.seats,
        coffee_price=cafe_to_edit.coffee_price
    )
    if edit_form.validate_on_submit():
        cafe_to_edit.name = edit_form.cafe_name.data
        cafe_to_edit.map_url = edit_form.map_url.data
        cafe_to_edit.img_url = edit_form.image_url.data
        cafe_to_edit.location = edit_form.location.data
        cafe_to_edit.has_sockets = edit_form.has_sockets.data
        cafe_to_edit.has_toilet = edit_form.has_toilet.data
        cafe_to_edit.has_wifi = edit_form.has_wifi.data
        cafe_to_edit.can_take_calls = edit_form.can_take_calls.data
        cafe_to_edit.seats = edit_form.seats.data
        cafe_to_edit.coffee_price = edit_form.coffee_price.data
        db.session.commit()
        return redirect(url_for('get_all_cafes'))
    return render_template('edit.html', form=edit_form)

# ## HTTP DELETE - Delete Record
@app.route("/delete-cafe/<cafe_id>", methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_cafes'))


if __name__ == '__main__':
    app.run(debug=True)
