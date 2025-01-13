from flask_restful import Resource,Api,fields,marshal_with,request,reqparse
from main import app,db,Category,Products
from flask import Flask, render_template, request, url_for, redirect
import json
api = Api(app)
 
all_cates = {
    'id': fields.Integer,
    'name':fields.String
}
all_prods = {
    'id': fields.Integer,
    'name':fields.String,
    'qnt':fields.String,
    'mfg_date':fields.String,
    'exp_date':fields.String,
    'price':fields.String,
    'nop':fields.Integer,
    'cate_id':fields.Integer
}

cate_parser = reqparse.RequestParser()
cate_parser.add_argument('id')
cate_parser.add_argument('name')


prod_parser = reqparse.RequestParser()
prod_parser.add_argument('id')
prod_parser.add_argument('name')
prod_parser.add_argument('qnt')
prod_parser.add_argument('mfg_date')
prod_parser.add_argument('exp_date')
prod_parser.add_argument('price')
prod_parser.add_argument('nop')
prod_parser.add_argument('image')
prod_parser.add_argument('cate_id')


class Category_manage(Resource):
    @marshal_with(all_cates)
    def get(self):
        cates = Category.query.all()
        return cates
    
    def post(self):
        args = cate_parser.parse_args()
        cate_name = args['name']
        if cate_name != "":
            cates = Category.query.all()
            for cate in cates:
                if cate.name == cate_name:
                    error = f"{cate_name}, is already exist!"
                    return {'massage':error},405
        else:
                return {'massage':'Please fill out the category!'} ,405                    
        new_cate = Category(name=cate_name)
        db.session.add(new_cate)
        db.session.commit()
        return {'massage':f'Category "{new_cate.name}" created successfully!'},200

    def put(self):
        args = cate_parser.parse_args()
        cate_id = args['id']
        cate_name = args['name']
        if cate_name != "":
            cate = Category.query.get(cate_id)
            cate.name = cate_name
            db.session.commit()
            return {'massage':f'Category "{cate.name}" updated successfully!'},200
        else:
            return {'massage':'Please, fill out category name!'},405

        

    def delete(self):
        args = cate_parser.parse_args()
        id = args['id']
        cate = Category.query.get(id)
        if cate.products:
            prods = Products.query.filter_by(cate_id=id).all()
            for prod in prods:
                db.session.delete(prod)
                db.session.commit()
            db.session.delete(cate)
            db.session.commit()  
            return {'massage':f'Category "{cate.name}" deleted successfully'},200
        else:
            db.session.delete(cate)
            db.session.commit()
            return {'massage':'Category deleted successfully!'},200



class Product_manage(Resource):
    @marshal_with(all_prods)
    def get(self):
        prods = Products.query.all()
        return prods

    def post(self):
        print('from post')
        args = prod_parser.parse_args()
        name = args['name']
        qnt = args['qnt']
        mfg_date = args['mfg_date']
        exp_date = args['exp_date']
        price = args['price']
        nop = args['nop']
        cate_id = args['cate_id']
        image = args['image']

        new_prod = Products(name=name,
                            qnt=qnt,
                            mfg_date=mfg_date,
                            exp_date=exp_date,
                            price=price,
                            nop=nop,
                            image=image,
                            cate_id=cate_id
                            )
        
        db.session.add(new_prod)
        db.session.commit()
        return {'massage':f'Product "{new_prod.name}" created successfully!'},200





    def put(self):
        args = prod_parser.parse_args()
        prod_id = args['id']
        name = args['name']
        qnt = args['qnt']
        mfg_date = args['mfg_date']
        exp_date = args['exp_date']
        price = args['price']
        nop = args['nop']
        image = args['image']
        cate_id = args['cate_id']

        prod = Products.query.get(prod_id)
        
        prod.name = name
        prod.qnt = qnt
        prod.mfg_date = mfg_date
        prod.exp_date = exp_date
        prod.price = price
        prod.nop = nop
        prod.image = image
        prod.cate_id = cate_id

        db.session.commit()
        return {'massage':f'Product "{prod.name}" updated successfully!'},200

    def delete(self):
        args = prod_parser.parse_args()
        prod_id = args['id']
        prod = Products.query.get(prod_id)
        db.session.delete(prod)
        db.session.commit()
        return {'massage':f'Product "{prod.name}" deleted successfully'},200

api.add_resource(Category_manage, '/api/category')
api.add_resource(Product_manage, '/api/product')