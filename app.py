# ./app.py
from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    request,
    logging,
)
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# Config MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "shivp436"
app.config["MYSQL_PASSWORD"] = "shivp436"
app.config["MYSQL_DB"] = "articles"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"  # fetch data as dictionary
# init MYSQL
mysql = MySQL(app)


Articles = Articles()


@app.route("/")  # root directory
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/articles")
def articles():
    return render_template("articles.html", articles=Articles)


@app.route("/article/<string:id>/")
def article(id):
    for article in Articles:
        if article["id"] == int(id):
            return render_template("article.html", article=article)


class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("User Name", [validators.Length(min=4, max=25)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.equal_to("confirm", "Passwords do not match"),
        ],
    )
    confirm = PasswordField("Confirm Password")


class LoginForm(Form):
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", validators=[validators.InputRequired()])


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create cursor
        cur = mysql.connection.cursor()
        # Execute query
        cur.execute(
            "INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
            (name, email, username, password),
        )
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash("You are now registered and can log in", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        email = form.email.data
        cur = mysql.connection.cursor()
        user = cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cur.fetchone()
        password = form.password.data
        if not user or not user_data:  # Check for empty result or no data
            print("no user data")
            # Handle no data scenario
            cur.close()
            return render_template(
                "login.html", form=form, error="No user found with that email"
            )
        password_saved = user_data["password"]
        cur.close()
        if sha256_crypt.verify(password, password_saved):
            print(user)
            session['logged_in'] = True
            session['username'] = user.username
            return render_template("dashboard.html")
        else:
            return render_template("login.html", form=form, error="Incorrect password")
    return render_template("login.html", form=form)


if __name__ == "__main__":
    app.secret_key = "secret123"
    app.run(debug=True)  # debug mode on
