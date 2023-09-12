# -*- coding: utf-8 -*-
import sys
from flask import Flask, jsonify, request, make_response, render_template, redirect
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from time import gmtime, strftime
import json
import datetime
import os
import base64
import random
import hashlib
import warnings

from . data import Data
from . import config as CFG


## IMPORT BLUEPRINT
# from .contoh_blueprint.controllers import contoh_blueprint
from .user.controllers import user
from .pegawai.controllers import pegawai
from .petani.controllers import petani

#region >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CONFIGURATION <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
app = Flask(__name__, static_url_path=None) #panggil modul flask

# CORS Configuration
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS']							= 'Content-Type'

# Flask JWT Extended Configuration
app.config['SECRET_KEY'] 							= CFG.JWT_SECRET_KEY
app.config['JWT_HEADER_TYPE']						= CFG.JWT_HEADER_TYPE
app.config['JWT_ACCESS_TOKEN_EXPIRES'] 				= datetime.timedelta(days=1) #1 hari token JWT expired
jwt = JWTManager(app)

# Application Configuration
app.config['PRODUCT_ENVIRONMENT']					= CFG.PRODUCT_ENVIRONMENT
app.config['BACKEND_BASE_URL']						= CFG.BACKEND_BASE_URL


# LOGS FOLDER PATH
app.config['LOGS'] 									= CFG.LOGS_FOLDER_PATH

# UPLOAD FOLDER PATH
UPLOAD_FOLDER_PATH									= CFG.UPLOAD_FOLDER_PATH

# Cek apakah Upload Folder Path sudah diakhiri dengan slash atau belum
if UPLOAD_FOLDER_PATH[-1] != "/":
	UPLOAD_FOLDER_PATH							= UPLOAD_FOLDER_PATH + "/"

app.config['UPLOAD_FOLDER_FOTO_USER'] 				= UPLOAD_FOLDER_PATH+"foto_user/"

#Create folder if doesn't exist
list_folder_to_create = [
	app.config['LOGS'],
	app.config['UPLOAD_FOLDER_FOTO_USER']
]
for x in list_folder_to_create:
	if os.path.exists(x) == False:
		os.makedirs(x)

#endregion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CONFIGURATION <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#region >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTION AREA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def defined_error(description, error="Defined Error", status_code=499):
	return make_response(jsonify({'description':description,'error': error,'status_code':status_code}), status_code)

def parameter_error(description, error= "Parameter Error", status_code=400):
	if app.config['PRODUCT_ENVIRONMENT'] == "DEV":
		return make_response(jsonify({'description':description,'error': error,'status_code':status_code}), status_code)
	else:
		return make_response(jsonify({'description':"Terjadi Kesalahan Sistem",'error': error,'status_code':status_code}), status_code)

def bad_request(description):
	if app.config['PRODUCT_ENVIRONMENT'] == "DEV":
		return make_response(jsonify({'description':description,'error': 'Bad Request','status_code':400}), 400) #Development
	else:
		return make_response(jsonify({'description':"Terjadi Kesalahan Sistem",'error': 'Bad Request','status_code':400}), 400) #Production

def tambahLogs(logs):
	f = open(app.config['LOGS'] + "/" + secure_filename(strftime("%Y-%m-%d"))+ ".txt", "a")
	f.write(logs)
	f.close()

#endregion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTION AREA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#region >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> AUTH AREA (JWT) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

@app.route("/login", methods=["POST"])
@cross_origin()
def login_customer():
	ROUTE_NAME = request.path

	data = request.json
	if "email" not in data:
		return parameter_error("Missing email in Request Body")
	if "password" not in data:
		return parameter_error("Missing password in Request Body")

	email = data["email"]
	password = data["password"]

	email = email.lower()
	password_enc = hashlib.md5(password.encode('utf-8')).hexdigest() # Convert password to md5

	# Check credential in database
	dt = Data()
	query = """ SELECT b.id_user, b.email, b.password
			FROM user b
			WHERE b.email = %s """
	values = (email, )
	data_user = dt.get_data(query, values)
	if len(data_user) == 0:
		return defined_error("Email not Registered", "Invalid Credential", 401)
	data_user = data_user[0]
	db_id_user = data_user["id_user"]
	db_password = data_user["password"]

	if password_enc != db_password:
		return defined_error("Wrong Password", "Invalid Credential", 401)

	role = 21
	role_desc = "CUSTOMER"

	jwt_payload = {
		"id_user" : db_id_user,
		"role" : role,
		"role_desc" : role_desc,
		"email" : email
	}

	access_token = create_access_token(email, additional_claims=jwt_payload)


	try:
		logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(db_id_user)+" - roles = "+str(role)+"\n"
	except Exception as e:
		logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
	tambahLogs(logs)

	return jsonify(access_token=access_token)

#endregion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> AUTH AREA (JWT) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#region >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> INDEX ROUTE AREA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

@app.route("/")
def homeee():
	return "Base Structure Backend"

#endregion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> INDEX ROUTE AREA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#region >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR HANDLER AREA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# fungsi error handle Halaman Tidak Ditemukan
@app.errorhandler(404)
@cross_origin()
def not_found(error):
	return make_response(jsonify({'error': 'Tidak Ditemukan','status_code':404}), 404)

#fungsi error handle Halaman internal server error
@app.errorhandler(500)
@cross_origin()
def not_found(error):
	return make_response(jsonify({'error': 'Error Server','status_code':500}), 500)

#endregion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR HANDLER AREA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#--------------------- REGISTER BLUEPRINT ------------------------

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(pegawai, url_prefix='/pegawai')
app.register_blueprint(petani, url_prefix='/petani')

#--------------------- END REGISTER BLUEPRINT ------------------------
