# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, make_response, render_template, redirect
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from time import gmtime, strftime
import datetime
import os

from . data import Data
from . import config as CFG


## IMPORT BLUEPRINT
# from .contoh_blueprint.controllers import contoh_blueprint
from .nasabah.controllers import nasabah
from .mutasi.controllers import mutasi

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

app.register_blueprint(nasabah, url_prefix='/nasabah')
app.register_blueprint(mutasi, url_prefix='/mutasi')

#--------------------- END REGISTER BLUEPRINT ------------------------
