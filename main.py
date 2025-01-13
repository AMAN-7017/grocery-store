from flask import Flask, render_template, request, url_for, redirect,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required
from flask_restful import Resource,Api
import json,requests,re,matplotlib.pyplot as plt,io
import matplotlib
matplotlib.use('Agg')
from datetime import datetime

#----------------------Flask Setup------------------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///grocery_store.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()
api = Api(app)
db.init_app(app)
app.app_context().push() 

login_manager = LoginManager()
login_manager.init_app(app)

#------------------------Create Models----------------------------------------

class Users(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False)
	email = db.Column(db.String(250), unique=True, nullable=False)
	password = db.Column(db.String(250), nullable=False)
	role = db.Column(db.String(250))

class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False, unique=True)
	products = db.relationship('Products', backref = 'category')
	
class Products(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False)
	qnt = db.Column(db.String(250), nullable=False)
	mfg_date = db.Column(db.String(250), nullable=True)
	exp_date = db.Column(db.String(250), nullable=True)
	price = db.Column(db.String(250), nullable=False)
	nop = db.Column(db.Integer, nullable=False)
	image = db.Column(db.String, nullable=False)
	cate_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	prod_id = db.Column(db.Integer, nullable=False)
	nop = db.Column(db.Integer, nullable=False)

class Sales(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	prod_id = db.Column(db.Integer, nullable=False)
	nop = db.Column(db.Integer, nullable=False)
	date = db.Column(db.String(12), nullable=False)


@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)


@app.route("/")
def home():
	return render_template("user_login.html")


#------------------------User Register-------------------------------


@app.route('/register', methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("user_register.html")
	if request.method == "POST":
		name = request.form.get("name")
		email = request.form.get("email")
		password = request.form.get("password")
		if request.method == "POST":
			new_user = Users(name=name,email=email,password=password,role='User')
			users = Users.query.all()
			for user in users:
				if user.email == request.form.get("email"):
					email_alert = '*Already exist, Please use different email!'	
					break
			else:	
				db.session.add(new_user)
				db.session.commit()
				return redirect(url_for("login"))
		return render_template("user_register.html",email_alert=email_alert)


#------------------------User Login-------------------------------


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("user_login.html")
	if request.method == "POST":
		role = request.form.get("role")
		email = request.form.get("email")
		password = request.form.get("password")
		if request.method == "POST":
			users = Users.query.filter_by(role="User").all()
			if users != None:
				if role == '1':
					users = Users.query.filter_by(role="Admin").all()
				for user in users:
					if user.email == email:
						user = Users.query.filter_by(email=email).first()
						if user.password == password:
							login_user(user)
							if role != '1':
								return redirect('/home/'+str(user.id))
							else:
								return redirect('/admin')
						else:	
							pass_alert = '*Wrong password, Please try again!'
							return render_template("user_login.html",pass_alert=pass_alert)
				else:	
					email_alert = "*Account not found, Please try again!"		
					return render_template("user_login.html",email_alert=email_alert)



#---------------------------------Logout----------------------------------------

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("login"))

# ------------------------------Api URL's-----------------------------

header = {'content-type':'application/json','Accept':'text/html'}
cate_api_url = "http://127.0.0.1:5000/api/category"
prod_api_url = "http://127.0.0.1:5000/api/product"

# ----------------------------Admin Home-------------------------------

@app.route("/admin",methods=['GET'])
def admin_home():
	categories = Category.query.all()
	products = Products.query.all()
	users = Users.query.filter_by(role="User").all()
	return render_template("admin_home.html",users=users,products=products,categories=categories)



# ---------------------------Add Category--------------------------------


@app.route("/add/category",methods=['POST','GET'])
def add_cate():
	if request.method == "GET":
		return render_template('add_cate_form.html')
	if request.method == "POST":
		cate_name = request.form.get('cate').capitalize()
		data = {
			"name":cate_name
		}
		response = requests.post(cate_api_url,data = json.dumps(data),headers=header)
		msg = response.json()
		if response.status_code != 200:
			return render_template('add_cate_form.html',error=msg['massage'])
		else:
			return render_template('add_cate_form.html',alert=msg['massage'])


# ----------------------------Delete Category------------------------------


@app.route("/del/category/<int:id>",methods=['GET'])
def del_cate(id):
	data = {
			"id":id
		}
	response = requests.delete(cate_api_url,data = json.dumps(data),headers=header)
	msg = response.json()
	return redirect('/admin')

# --------------------------Edit Category--------------------------------



@app.route("/update/category/<int:id>",methods=['POST','GET'])
def update_cate(id):
	if request.method == "GET":
		cate = Category.query.get(id)
		return render_template('update_cate_form.html',cate=cate)
	if request.method == "POST":
		cate = request.form.get('cate')
		if cate == "":
			return render_template('update_cate_form.html',cate=cate,error='Please, fill out category name!')
		else:
			data = {
				"id":id,
				"name":cate
			}
			response = requests.put(cate_api_url,data = json.dumps(data),headers=header)
			msg = response.json()
			if response.status_code != 200:
				return render_template('update_cate_form.html',cate=cate,error=msg['massage'])
			else:
				return render_template('update_cate_form.html',cate=cate,alert=msg['massage'])


# --------------------------Add Product----------------------------------


@app.route("/add/product",methods=['POST','GET'])
def add_prod():
	if request.method == "GET":
		cates = Category.query.all()
		return render_template('add_prod_form.html',cates=cates)
	if request.method == "POST":
		p_name = request.form.get('prod').capitalize()
		mfg_date = request.form.get('mfg_date')
		exp_date = request.form.get('mfg_date')
		price = request.form.get('price')
		cate_id = request.form.get('cate')
		qnt = request.form.get('qnt')
		nop = request.form.get('nop')
		image = request.form.get('image')
		l = [p_name,qnt,price,nop,cate_id,image]
		lot = ["Product name","Unit","price","Number of product","Category","image"]
		for i in range(len(l)):
			if (l[i] == ''):
				cates = Category.query.all()
				error = f"{lot[i]} are required!"
				return render_template('add_prod_form.html',error=error,cates=cates)
		data = {
			"name":p_name,
			"qnt":qnt,
			"mfg_date":mfg_date,
			"exp_date" : exp_date,
			"price":price,
			"nop":nop,
			"image":image,
			"cate_id":cate_id
		}
		response = requests.post(prod_api_url,data = json.dumps(data),headers=header)
		msg = response.json()
		cates = Category.query.all()
		if response.status_code != 200:
			return render_template('add_prod_form.html',cates=cates,error=msg['massage'])
		else:
			return render_template('add_prod_form.html',cates=cates,alert=msg['massage'])



# ---------------------------Edit Product-----------------------------------


@app.route("/update/product/<int:id>",methods=['POST','GET'])
def update_prod(id):
	if request.method == "GET":
		prod = Products.query.get(id)
		cates = Category.query.all()
		return render_template('update_prod_form.html',prod=prod,cates=cates)
	if request.method == "POST":
		prod = Products.query.get(id)
		p_name = request.form.get('prod').capitalize()
		mfg_date = request.form.get('mfg_date')
		exp_date = request.form.get('mfg_date')
		price = request.form.get('price')
		cate_id = request.form.get('cate')
		qnt = request.form.get('qnt')
		nop = request.form.get('nop')
		image = request.form.get('image')
		l = [p_name,qnt,price,nop,cate_id,image]
		lot = ["Product name","Unit","price","Number of product","Category","image"]
		for i in range(len(l)):
			if (l[i] == ''):
				cates = Category.query.all()
				error = f"{lot[i]} are required!"
				return render_template('add_prod_form.html',error=error,cates=cates,prod=prod)
		data = {
			"id":id,
			"name":p_name,
			"qnt":qnt,
			"mfg_date":mfg_date,
			"exp_date" : exp_date,
			"price":price,
			"nop":nop,
			"image":image,
			"cate_id":cate_id
		}
		response = requests.put(prod_api_url,data = json.dumps(data),headers=header)
		msg = response.json()
		cates = Category.query.all()
		prod = Products.query.get(id)
		if response.status_code != 200:
			return render_template('update_prod_form.html',prod=prod,cates=cates,error=msg['massage'])
		else:
			return render_template('update_prod_form.html',prod=prod,cates=cates,alert=msg['massage'])


# ---------------------------Delete Product---------------------------------

@app.route("/del/product/<int:id>",methods=['GET'])
def del_prod(id):
	data = {"id":id}
	response = requests.delete(prod_api_url,data = json.dumps(data),headers=header)
	msg = response.json()
	print(msg)
	return redirect(url_for('admin_home'))


# -------------------------------Summary-------------------------------

@app.route('/summary',methods=['GET'])

def summary():
	# admin = Users.query.get(admin_id)
	current_month = datetime.now().month
	sales = Sales.query.filter(extract('month', Sales.date) == current_month).all()
	s_data = {}
	revenue = 0
	for sale in sales:
		p = Products.query.get(sale.prod_id)
		revenue += sale.nop*int(p.price)
		if p.name in s_data:
			s_data[p.name] += sale.nop
		else:
			s_data[p.name] = sale.nop

	p_name = s_data.keys()	
	nop = s_data.values()
	plt.bar(p_name,nop,color = '#007bff')
	plt.xlabel('Products',fontsize=12)	
	plt.ylabel('Number of product',fontsize=12)	
	plt.xticks(rotation = 45)
	plt.title('Products sold out in a month',fontsize=15)
	plt.savefig('static/images/barchart.png')

	max = 0
	sold_prod = 0
	prod_name = ""
	for prod,nop in s_data.items():
		sold_prod += nop
		if nop >= max:
			max = nop
			prod_name = prod
	categories = Category.query.all()
	products = Products.query.all()
	users = Users.query.filter_by(role="User").all()

	return render_template('summary.html',sold_prod=sold_prod,users=users,revenue=revenue,prod_name=prod_name,products=products,categories=categories)





# ------------------------------User Home-----------------------------

@app.route("/home/<int:user_id>",methods=['GET'])
def user_home(user_id):
	categories = Category.query.all()
	cart = Cart.query.filter_by(user_id=user_id).all()
	user = Users.query.get(user_id)
	loi = []
	for i in cart:
		loi.append(i.prod_id)
	return render_template('user_home.html',loi=loi,categories=categories,cart=cart,user=user)

# --------------------------Cart------------------------------------------

@app.route("/cart/<int:user_id>",methods=['GET','POST'])
def cart(user_id):
	cart = Cart.query.filter_by(user_id=user_id).all()
	total = 0
	prods = []
	for i in cart:
		p = Products.query.get(i.prod_id)
		prods.append(p)
		total += i.nop*int(p.price)
	user = Users.query.get(user_id)
	return render_template('cart.html',total=total,cart=cart,user=user,prods=prods)



# -----------------------------Add Product to Cart--------------------------

@app.route("/add/product/cart/<int:user_id>/<int:prod_id>",methods=['GET'])
def add_prod_cart(user_id,prod_id):
	new_prod = Cart(user_id=user_id,prod_id=prod_id,nop=1)
	db.session.add(new_prod)
	db.session.commit()
	return redirect('/home/'+str(user_id))

# -----------------------------Remove Product to Cart--------------------------

@app.route("/delete/product/cart/<int:user_id>/<int:cart_id>",methods=['GET'])
def del_prod_cart(cart_id,user_id):
	cart_prod = Cart.query.get(cart_id)
	db.session.delete(cart_prod)
	db.session.commit()
	return redirect('/cart/'+str(user_id))
	
	

# ----------------------Add number of products to cart------------------------

@app.route("/decrease/product/cart/<int:user_id>/<int:cart_id>",methods=['GET'])
def decr_prod_cart(cart_id,user_id):
	cart_prod = Cart.query.get(cart_id)
	cart_prod.nop -= 1 
	db.session.commit()
	return redirect('/cart/'+str(user_id))


@app.route("/increase/product/cart/<int:user_id>/<int:cart_id>",methods=['GET'])
def incr_prod_cart(cart_id,user_id):
	cart_prod = Cart.query.get(cart_id)
	prod = Products.query.get(cart_prod.prod_id)
	user = Users.query.get(user_id)
	cart = Cart.query.filter_by(user_id=user_id).all()
	total = 0
	prods = []
	for i in cart:
		p = Products.query.get(i.prod_id)
		prods.append(p)
		total += i.nop*int(p.price)
	if cart_prod.nop < prod.nop:
		cart_prod.nop += 1 
		db.session.commit()
		return render_template('cart.html',cart=cart,user=user,prods=prods,total=total)
	else:
		alert = f"You can not add more then {prod.nop} {prod.name}!"
		return render_template('cart.html',p_alert=alert,cart=cart,user=user,prods=prods,total=total)
		


@app.route("/buy-all/<int:user_id>",methods=['GET'])
def buy_all(user_id):
	cart = Cart.query.filter_by(user_id=user_id).all()
	for item in cart:
		p = Products.query.get(item.prod_id)
		p.nop -= item.nop * 2
		sale = Sales(user_id=user_id,prod_id=item.prod_id,nop=item.nop * 2,date=datetime.now().date())
		db.session.add(sale)
		db.session.delete(item)
		db.session.commit()
	alert = f"Your order has been placed successfully!"	
	user = Users.query.get(user_id)
	return render_template('cart.html',alert=alert,user=user)




# --------------------------User Search------------------------------------


@app.route('/search/<int:user_id>',methods=['POST','GET'])
def search(user_id):
	if request.method == "GET":
		cart = Cart.query.filter_by(user_id=user_id).all()
		return render_template('search.html',cart=cart)
	if request.method == "POST":
		search = request.form.get('search').capitalize()
		prods = Products.query.all()
		cates = Category.query.all()
		search_results = []
		for prod in prods:
			if(re.findall(search, prod.name)):				
				search_results.append(prod)
		for cate in cates:
			if(re.findall(search, cate.name)):
				for prod in cate.products:
					if prod not in search_results:				
						search_results.append(prod)
		cart = Cart.query.filter_by(user_id=user_id).all()
		user = Users.query.get(user_id)
		return render_template('search.html',user=user,search_results=search_results,cart=cart,search=search)		

		
# --------------------------Admin Search------------------------------------


@app.route('/admin_search',methods=['POST','GET'])
def admin_search():
	if request.method == "GET":
		return render_template('admin_search.html')
	if request.method == "POST":
		search = request.form.get('search').capitalize()
		prods = Products.query.all()
		cates = Category.query.all()
		cart = Cart.query.all()
		search_results = []
		for prod in prods:
			if(re.findall(search, prod.name)):				
				search_results.append(prod)
		for cate in cates:
			if(re.findall(search, cate.name)):
				for prod in cate.products:
					if prod not in search_results:				
						search_results.append(prod)
		return render_template('admin_search.html',search_results=search_results,search=search)		



from api import *

if __name__ == "__main__":
	app.run(debug=True)
