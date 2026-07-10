import resend
import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_email(to_email, subject, html_body):

    params = {
        "from": "notifications@anvayaconnect.org",
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    resend.Emails.send(params)

# ================= CONFIGURATION =================

app.config["SECRET_KEY"] = "anvaya_secret_key"

database_url = os.environ.get("DATABASE_URL")

if database_url:
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ================= DATABASE TABLES =================

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngo_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(300), nullable=False)


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant = db.Column(db.String(100))
    food_name = db.Column(db.String(100))
    quantity = db.Column(db.String(50))
    address = db.Column(db.String(200))
    ready_until = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Available")
    claimed_by = db.Column(db.String(100), default="")


# ================= HOME =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= RESTAURANT REGISTRATION =================

@app.route("/restaurant/register", methods=["GET", "POST"])
def restaurant_register():

    if request.method == "POST":

        restaurant_name = request.form["restaurant_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Basic Validation
        if restaurant_name == "" or email == "" or password == "":
            return "Please fill in all fields."

        # Duplicate Email Check
        existing_restaurant = Restaurant.query.filter_by(email=email).first()

        if existing_restaurant:
            return "An account with this email already exists."

        # Hash Password
        hashed_password = generate_password_hash(password)

        restaurant = Restaurant(
            restaurant_name=restaurant_name,
            email=email,
            password=hashed_password
        )

        db.session.add(restaurant)
        db.session.commit()

        return redirect("/restaurant/login")

    return render_template("restaurant_register.html")


# ================= RESTAURANT LOGIN =================

@app.route("/restaurant/login", methods=["GET", "POST"])
def restaurant_login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        restaurant = Restaurant.query.filter_by(
            email=email
        ).first()

        if restaurant and check_password_hash(restaurant.password, password):

            session["restaurant"] = restaurant.restaurant_name

            return redirect("/restaurant/dashboard")

        return "Invalid email or password."

    return render_template("restaurant_login.html")

# ================= RESTAURANT DASHBOARD =================

@app.route("/restaurant/dashboard")
def restaurant_dashboard():

    if "restaurant" not in session:
        return redirect("/restaurant/login")

    donations = Donation.query.filter_by(
        restaurant=session["restaurant"]
    ).all()

    return render_template(
        "restaurant_dashboard.html",
        restaurant=session["restaurant"],
        donations=donations
    )


# ================= ADD DONATION =================

@app.route("/restaurant/add-donation", methods=["GET", "POST"])
def add_donation():

    if "restaurant" not in session:
        return redirect("/restaurant/login")

    if request.method == "POST":

        donation = Donation(
            restaurant=session["restaurant"],
            food_name=request.form["food_name"],
            quantity=request.form["quantity"],
            address=request.form["address"],
            ready_until=request.form["ready_until"],
            phone=request.form["phone"]
        )

        db.session.add(donation)
        db.session.commit()

        # Notify all NGOs
        ngos = NGO.query.all()

        for ngo in ngos:

            subject = "🍛 New Food Donation Available"

            body = f"""
            <h2>New Food Donation</h2>

            <p><b>Restaurant:</b> {donation.restaurant}</p>

            <p><b>Food:</b> {donation.food_name}</p>

            <p><b>Quantity:</b> {donation.quantity}</p>

            <p><b>Pickup Address:</b> {donation.address}</p>

            <p><b>Available Until:</b> {donation.ready_until}</p>

            <p>Please login to Anvaya and claim it.</p>
            """

            send_email(
                ngo.email,
                subject,
                body
            )

        return redirect("/restaurant/dashboard")

    return render_template("add_donation.html")


# ================= NGO REGISTRATION =================

@app.route("/ngo/register", methods=["GET", "POST"])
def ngo_register():

    if request.method == "POST":

        ngo_name = request.form["ngo_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Basic Validation
        if ngo_name == "" or email == "" or password == "":
            return "Please fill in all fields."

        # Duplicate Email Check
        existing_ngo = NGO.query.filter_by(email=email).first()

        if existing_ngo:
            return "An account with this email already exists."

        # Hash Password
        hashed_password = generate_password_hash(password)

        ngo = NGO(
            ngo_name=ngo_name,
            email=email,
            password=hashed_password
        )

        db.session.add(ngo)
        db.session.commit()

        return redirect("/ngo/login")

    return render_template("ngo_register.html")


# ================= NGO LOGIN =================

@app.route("/ngo/login", methods=["GET", "POST"])
def ngo_login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        ngo = NGO.query.filter_by(
            email=email
        ).first()

        if ngo and check_password_hash(ngo.password, password):

            session["ngo"] = ngo.ngo_name

            return redirect("/ngo/dashboard")

        return "Invalid email or password."

    return render_template("ngo_login.html")


# ================= NGO DASHBOARD =================


@app.route("/ngo/dashboard")
def ngo_dashboard():

    if "ngo" not in session:
        return redirect("/ngo/login")

    # Show only available donations
    donations = Donation.query.filter_by(
        status="Available"
    ).all()

    # Show donations claimed by the logged-in NGO
    claimed_donations = Donation.query.filter_by(
        claimed_by=session["ngo"]
    ).all()

    return render_template(
        "ngo_dashboard.html",
        ngo=session["ngo"],
        donations=donations,
        claimed_donations=claimed_donations
    )


# ================= CLAIM DONATION =================

@app.route("/claim/<int:donation_id>", methods=["POST"])
def claim_donation(donation_id):

    if "ngo" not in session:
        return redirect("/ngo/login")

    donation = Donation.query.get(donation_id)

    if donation and donation.status == "Available":

        donation.status = "Claimed"
        donation.claimed_by = session["ngo"]

        db.session.commit()

        restaurant = Restaurant.query.filter_by(
            restaurant_name=donation.restaurant
        ).first()

        ngo = NGO.query.filter_by(
            ngo_name=session["ngo"]
        ).first()

        if restaurant and ngo:

            subject = "✅ Your Donation Has Been Claimed"

            body = f"""
            <h2>Your Donation Has Been Claimed</h2>

            <p><b>NGO:</b> {ngo.ngo_name}</p>

            <p><b>Food:</b> {donation.food_name}</p>

            <p><b>Quantity:</b> {donation.quantity}</p>

            <p><b>Pickup Address:</b> {donation.address}</p>

            <p>Thank you for reducing food waste with Anvaya.</p>
            """

            send_email(
                restaurant.email,
                subject,
                body
            )

    return redirect("/ngo/dashboard")


    # ================= COLLECT DONATION =================

@app.route("/collect/<int:donation_id>", methods=["POST"])
def collect_donation(donation_id):

    if "ngo" not in session:
        return redirect("/ngo/login")

    donation = Donation.query.get(donation_id)

    if donation and donation.claimed_by == session["ngo"]:

        donation.status = "Collected"

        db.session.commit()

    return redirect("/ngo/dashboard")


    # ================= RESTAURANT LOGOUT =================

@app.route("/restaurant/logout")
def restaurant_logout():

    session.pop("restaurant", None)

    return redirect("/")


# ================= NGO LOGOUT =================

@app.route("/ngo/logout")
def ngo_logout():

    session.pop("ngo", None)

    return redirect("/")

    # ================= CREATE ADMIN (TEMPORARY) =================

@app.route("/reset-admin")
def reset_admin():

    admin = Admin.query.first()

    if not admin:
        return "No admin found."

    admin.username = "admin"
    admin.password = generate_password_hash("Admin@12345")

    db.session.commit()

    return "Admin reset successfully!"


    # ================= ADMIN LOGIN =================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):

            session["admin"] = admin.username

            return redirect("/admin/dashboard")

        return "Invalid username or password."

    return render_template("admin_login.html")


    # ================= ADMIN DASHBOARD =================

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin/login")

    restaurant_count = Restaurant.query.count()
    ngo_count = NGO.query.count()
    donation_count = Donation.query.count()

    return render_template(
        "admin_dashboard.html",
        admin=session["admin"],
        restaurant_count=restaurant_count,
        ngo_count=ngo_count,
        donation_count=donation_count
    )


# ================= ADMIN RESTAURANTS =================

@app.route("/admin/restaurants")
def admin_restaurants():

    if "admin" not in session:
        return redirect("/admin/login")

    restaurants = Restaurant.query.all()

    return render_template(
        "admin_restaurants.html",
        restaurants=restaurants
    )


# ================= ADMIN NGOS =================

@app.route("/admin/ngos")
def admin_ngos():

    if "admin" not in session:
        return redirect("/admin/login")

    ngos = NGO.query.all()

    return render_template(
        "admin_ngos.html",
        ngos=ngos
    )

# ================= ADMIN DONATIONS =================

@app.route("/admin/donations")
def admin_donations():

    if "admin" not in session:
        return redirect("/admin/login")

    donations = Donation.query.all()

    return render_template(
        "admin_donations.html",
        donations=donations
    )


# ================= ADMIN LOGOUT =================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin/login")

    
# ================= START APPLICATION =================

with app.app_context():
    print("===== STARTING DATABASE INITIALIZATION =====")

    from sqlalchemy import inspect

    print("DATABASE URI =", app.config["SQLALCHEMY_DATABASE_URI"])

    try:
        
        db.create_all()
        print("CREATE ALL SUCCESS")

        inspector = inspect(db.engine)
        print("TABLES FOUND:", inspector.get_table_names())

    except Exception as e:
        print("DATABASE ERROR:", repr(e))
        raise

    admin = Admin.query.filter_by(username="admin").first()

    if not admin:
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

    print("===== ADMIN CHECK COMPLETE =====")


@app.route("/test-email")
def test_email():

    send_email(
    "apoorva30me@gmail.com",
    "Anvaya Test Email",
    """
    <h2>Hello!</h2>
    <p>Your Resend integration is working successfully.</p>
    <p><b>Welcome to Anvaya 🚀</b></p>
    """
)

    return "Email sent successfully!"


if __name__ == "__main__":
    app.run(debug=True)