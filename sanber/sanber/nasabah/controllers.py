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

nasabah = Blueprint('nasabah', __name__, static_folder = '../../upload/foto_nasabah', static_url_path="/media")

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

def defined_error(description, error="Defined Error", status_code=400):
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

@nasabah.route('/get_nasabah', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_nasabah():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT * FROM nasabah a WHERE a.id=a.id """
		values = ()

		page = request.args.get("page")
		id_nasabah = request.args.get("id_nasabah")
		no_rekening = request.args.get("no_rekening")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_nasabah:
			query += " AND a.id = %s "
			values += (id_nasabah, )
		if no_rekening:
			query += " AND a.no_rekening = %s "
			values += (no_rekening, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama ) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "nama_asc":
				query += " ORDER BY a.nama ASC "
			if order_by == "nama_desc":
				query += " ORDER BY a.nama DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)
		if no_rekening and len(hasil) == 0:
			return defined_error("Gagal, data nasabah dengan no rekening tidak ditemukan")

		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"

		logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = NULL - roles = NULL - param_logs = "+param_logs+"\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

	
@nasabah.route('/update', methods=['PUT', 'OPTIONS'])
@cross_origin()
def update_nasabah():
	ROUTE_NAME = str(request.path)

	try:
		dt = Data()
		data = request.json

		id_nasabah = request.args.get("id_nasabah")

		query_temp = " SELECT id FROM nasabah WHERE id = %s "
		values_temp = (id_nasabah, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE nasabah SET id = id """
		values = ()

		if "nama" in data:
			nama = data["nama"]
			query += """ ,nama = %s """
			values += (nama, )

		if "nik" in data:
			nik = data["nik"]
			query += """ ,nik = %s """
			values += (nik, )

		if "no_hp" in data:
			no_hp = data["no_hp"]
			query += """ ,no_hp = %s """
			values += (no_hp, )
		
		query += """ WHERE id = %s """
		values += (id_nasabah, )
		dt.insert_data(query, values)

		hasil = "Success Update Nasabah"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = "+str(id_nasabah)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))
	
@nasabah.route('/tabung', methods=['PUT', 'OPTIONS'])
@cross_origin()
def tabung_nasabah():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.now()
	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "no_rekening" not in data:
			return parameter_error("Missing no_rekening in Request Body")
		if "nominal" not in data:
			return parameter_error("Missing nominal in Request Body")

		no_rekening = data["no_rekening"]
		nominal = data["nominal"]

		query_temp = " SELECT * FROM nasabah WHERE no_rekening = %s "
		values_temp = (no_rekening, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data nasabah dengan no rekening tidak ditemukan")

		saldo_sebelumnya = data_temp[0]["saldo"]
		saldo_sekarang = saldo_sebelumnya + nominal
		query = """ UPDATE nasabah SET id = id """
		values = ()

		query += """ ,saldo = %s """
		values += (saldo_sekarang, )
		
		query += """ WHERE no_rekening = %s """
		values += (no_rekening, )
		dt.insert_data(query, values)

		# Insert to table mutasi
		query2 = "INSERT into mutasi (kode_transaksi, nominal, waktu_transaksi, nasabah_id) VALUES (%s, %s, %s, %s)"
		values2 = ("C", nominal, now, data_temp[0]["id"])
		dt.insert_data_last_row(query2, values2)

		hasil = "Success Menambah Uang Nasabah"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = "+str()+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data': {'saldo': saldo_sekarang}} ), 200)
	except Exception as e:
		return bad_request(str(e))
	

@nasabah.route('/tarik', methods=['PUT', 'OPTIONS'])
@cross_origin()
def tarik_nasabah():
	ROUTE_NAME = str(request.path)
	now = datetime.datetime.now()

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "no_rekening" not in data:
			return parameter_error("Missing no_rekening in Request Body")
		if "nominal" not in data:
			return parameter_error("Missing nominal in Request Body")

		no_rekening = data["no_rekening"]
		nominal = data["nominal"]

		query_temp = " SELECT * FROM nasabah WHERE no_rekening = %s "
		values_temp = (no_rekening, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data nasabah dengan no rekening tidak ditemukan")

		saldo_sebelumnya = data_temp[0]["saldo"]
		if (saldo_sebelumnya < nominal):
			return defined_error("Gagal, Saldo anda tidak cukup, saldo anda "+str(saldo_sebelumnya))
		
		saldo_sekarang = saldo_sebelumnya - nominal
		query = """ UPDATE nasabah SET id = id """
		values = ()

		query += """ ,saldo = %s """
		values += (saldo_sekarang, )
		
		query += """ WHERE no_rekening = %s """
		values += (no_rekening, )
		dt.insert_data(query, values)

		# Insert to table mutasi
		query2 = "INSERT into mutasi (kode_transaksi, nominal, waktu_transaksi, nasabah_id) VALUES (%s, %s, %s, %s)"
		values2 = ("D", nominal, now, data_temp[0]["id"])
		dt.insert_data_last_row(query2, values2)

		hasil = "Success Menarik Uang Nasabah"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = "+str()+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data': {'saldo': saldo_sekarang}} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= MY PROFILE AREA ==========================================================================


#region ================================= CUSTOMER AREA ==========================================================================

@nasabah.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_nasabah():
	ROUTE_NAME = str(request.path)

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama" not in data:
			return parameter_error("Missing nama in Request Body")
		if "nik" not in data:
			return parameter_error("Missing NIK in Request Body")
		if "no_hp" not in data:
			return parameter_error("Missing no hp in Request Body")

		nama = data["nama"]
		nik = data["nik"]
		no_hp = data["no_hp"]

		# check if nasabah already used or not
		query_temp = "SELECT id FROM nasabah WHERE nik = %s AND no_hp = %s"
		values_temp = (nik, no_hp)
		if len(dt.get_data(query_temp, values_temp)) != 0:
			return defined_error("Nasabah Already Registered")
		
		no_rekening = 'ACC' + str(random.randint(0, 999999999))

		# Insert to table nasabah
		query = "INSERT into nasabah (nama, nik, no_hp, no_rekening, saldo) VALUES (%s, %s, %s, %s, %s)"
		values = (nama, nik, no_hp, no_rekening, 0)
		id_nasabah = dt.insert_data_last_row(query, values)

		hasil = "Register Nasabah Success"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_nasabah = "+str(id_nasabah)+" - roles = "+str("umum")+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_id_nasabah = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data': {'no_rekening': no_rekening}} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= CUSTOMER AREA ==========================================================================
