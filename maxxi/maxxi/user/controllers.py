from flask import Blueprint, jsonify, request, make_response, render_template
from flask import current_app as app
from flask_jwt_extended import get_jwt, jwt_required
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from time import gmtime, strftime
import hashlib
import datetime
import cv2
import numpy as np
import base64
import random
import string

from . models import Data

user = Blueprint('user', __name__, static_folder = '../../upload/foto_user', static_url_path="/media")

#region ================================= FUNGSI-FUNGSI AREA ==========================================================================

def tambahLogs(logs):
	f = open(app.config['LOGS'] + "/" + secure_filename(strftime("%Y-%m-%d"))+ ".txt", "a")
	f.write(logs)
	f.close()

def save(encoded_data, filename):
	arr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
	img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
	return cv2.imwrite(filename, img)

def permission_failed():
    return make_response(jsonify({'error': 'Permission Failed','status_code':403}), 403)

def request_failed():
    return make_response(jsonify({'error': 'Request Failed','status_code':403}), 403)

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

def randomString(stringLength):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))

def random_string_number_only(stringLength):
	letters = string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))

#endregion ================================= FUNGSI-FUNGSI AREA ===============================================================


#region ================================= MY PROFILE AREA ==========================================================================

@user.route('/get_my_profile', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_my_profile():
	try:
		ROUTE_NAME = str(request.path)

		id_user = str(get_jwt()["id_user"])
		role = str(get_jwt()["role"])
		
		dt = Data()

		query = """ SELECT a.* FROM user a WHERE id_user = %s """
		values = (id_user, )

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@user.route('/update_my_profile', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_my_profile():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.now()
	id_user 		= str(get_jwt()["id_user"])
	role 			= str(get_jwt()["role"])
	
	try:
		dt = Data()
		data = request.json


		query_temp = " SELECT id_user FROM user WHERE id_user = %s "
		values_temp = (id_user, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE user SET id_user = id_user """
		values = ()
		
		if "password" in data:
			password = data["password"]

			if "old_password" not in data:
				return parameter_error("Missing old_password in Request Body")

			old_password = data["old_password"]
			old_pass_enc = hashlib.md5(old_password.encode('utf-8')).hexdigest()
			# check if old password is correct
			query_temp = "SELECT id_user, password FROM user WHERE id_user = %s AND password = %s LIMIT 1"
			values_temp = (id_user, old_pass_enc)
			if len(dt.get_data(query_temp, values_temp)) == 0:
				return defined_error("Password lama tidak sesuai")

			# Convert password to MD5
			pass_ency = hashlib.md5(password.encode('utf-8')).hexdigest()
			query += """ ,password = %s, waktu_terakhir_ganti_password = %s """
			values += (pass_ency, now, )

		if "nama" in data:
			nama = data["nama"]
			query += """ ,nama = %s """
			values += (nama, )

		if "tanggal_lahir" in data:
			tanggal_lahir = data["tanggal_lahir"]
			query += """ ,tanggal_lahir = %s """
			values += (tanggal_lahir, )

		if "jenis_kelamin" in data:
			jenis_kelamin = data["jenis_kelamin"].upper()
			# validasi data jenis kelamin
			if str(jenis_kelamin) not in ["LK", "PR"]:
				return parameter_error("Invalid jenis_kelamin Parameter")
			query += """ ,jenis_kelamin = %s """
			values += (jenis_kelamin, )

		if "nomor_telepon" in data:
			nomor_telepon = data["nomor_telepon"]
			query += """ ,nomor_telepon = %s """
			values += (nomor_telepon, )

		if "alamat" in data:
			alamat = data["alamat"]
			query += """ ,alamat = %s """
			values += (alamat, )
		
		query += """ WHERE id_user = %s """
		values += (id_user, )
		dt.insert_data(query, values)

		hasil = "Success Update My Profile"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= MY PROFILE AREA ==========================================================================


#region ================================= CUSTOMER AREA ==========================================================================

@user.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_customer():
	ROUTE_NAME = str(request.path)

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "email" not in data:
			return parameter_error("Missing email in Request Body")
		if "password" not in data:
			return parameter_error("Missing password in Request Body")
		if "nama" not in data:
			return parameter_error("Missing nama in Request Body")

		email = data["email"]
		password = data["password"]
		nama = data["nama"]

		# check if username already used or not
		query_temp = "SELECT id_user FROM user WHERE email = %s"
		values_temp = (email, )
		if len(dt.get_data(query_temp, values_temp)) != 0:
			return defined_error("Email Already Registered")

		# Convert password to MD5
		pass_ency = hashlib.md5(password.encode('utf-8')).hexdigest()

		# Check optional data
		# Default variables for optional data
		tanggal_lahir	= None
		jenis_kelamin	= None
		nomor_telepon 	= None
		alamat			= None

		if "tanggal_lahir" in data:
			tanggal_lahir = data["tanggal_lahir"]
		if "jenis_kelamin" in data:
			jenis_kelamin = data["jenis_kelamin"]
			# Validasi data jenis kelamin
			if jenis_kelamin not in ["LK", "PR"]:
				return parameter_error("Invalid jenis_kelamin Parameter")
		if "nomor_telepon" in data:
			nomor_telepon = data["nomor_telepon"]
		if "alamat" in data:
			alamat = data["alamat"]

		# Insert to table user
		query = "INSERT into user (email, password, nama, tanggal_lahir, jenis_kelamin, nomor_telepon, alamat) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		values = (email, pass_ency, nama, tanggal_lahir, jenis_kelamin, nomor_telepon, alamat)
		id_user = dt.insert_data_last_row(query, values)

		hasil = "Register Success"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str("umum")+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= CUSTOMER AREA ==========================================================================
