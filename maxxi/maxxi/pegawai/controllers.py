from flask import Blueprint, jsonify, request, make_response, render_template
from flask import current_app as app
from flask_jwt_extended import get_jwt, jwt_required
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from time import gmtime, strftime
import datetime
import cv2
import numpy as np
import base64
import random
import string

from . models import Data

pegawai = Blueprint('pegawai', __name__, static_folder = '../../upload/pegawai', static_url_path="/media")

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


#region ================================= TEMPAT UJI KOMPETENSI AREA ==========================================================================

@pegawai.route('/', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_tempat_uji_kompetensi():
	try:
		ROUTE_NAME = str(request.path)
		
		dt = Data()

		query = """ SELECT a.*, b.divisi
					FROM pegawai a
					RIGHT JOIN divisi b ON a.id_divisi=b.id
					WHERE a.nomor_pegawai !=0 """
		values = ()

		page = request.args.get("page")
		id_divisi = request.args.get("id_divisi")
		nomor_pegawai = request.args.get("nomor_pegawai")
		divisi = request.args.get("divisi")
		is_aktif = request.args.get("is_aktif")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_divisi:
			query += " AND a.id_divisi = %s "
			values += (id_divisi, )
		if nomor_pegawai:
			query += " AND a.nomor_pegawai = %s "
			values += (nomor_pegawai, )
		if divisi:
			query += " AND b.divisi = %s "
			values += (divisi, )
		if is_aktif:
			query += " AND a.is_aktif = %s "
			values += (is_aktif, )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.nama ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.nama DESC "
			else:
				query += " ORDER BY a.nama ASC "
		else:
			query += " ORDER BY a.nama ASC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str("umum")+" - roles = "+str("umum")+" - param_logs = "+param_logs+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL - param_logs = "+param_logs+"\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@pegawai.route('/', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_tempat_uji_kompetensi():
	ROUTE_NAME = str(request.path)

	id_user = str(get_jwt()["id_user"])
	role = str(get_jwt()["role"])

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama" not in data:
			return parameter_error("Missing nama in Request Body")
		if "no_hp" not in data:
			return parameter_error("Missing no_hp in Request Body")
		if "email" not in data:
			return parameter_error("Missing email in Request Body")
		if "alamat" not in data:
			return parameter_error("Missing alamat in Request Body")
		if "id_divisi" not in data:
			return parameter_error("Missing id_divisi in Request Body")

		nama 						= data["nama"]
		no_hp 						= data["no_hp"]
		email 						= data["email"]
		alamat 						= data["alamat"]
		id_divisi 					= data["id_divisi"]


		# cek apakah data kota ada
		query_temp = "SELECT id FROM divisi WHERE id = %s"
		values_temp = (id_divisi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Divisi tidak ditemukan")

		# Insert to table tempat uji kompetensi
		query = "INSERT INTO pegawai (nama, alamat, email, no_hp, id_divisi) VALUES (%s,%s,%s,%s,%s)"
		values = (nama, alamat, email, no_hp, id_divisi)
		nomor_pegawai = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan pegawai"
		hasil_data = {
			"nomor_pegawai" : nomor_pegawai
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pegawai.route('/', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_tempat_uji_kompetensi():
	ROUTE_NAME = str(request.path)

	id_user 		= str(get_jwt()["id_user"])
	role 			= str(get_jwt()["role"])

	nomor_pegawai = request.args.get("nomor_pegawai")

	
	try:
		dt = Data()
		data = request.json

		# Cek apakah data skema sertifikasi ada
		query_temp = " SELECT nomor_pegawai FROM pegawai WHERE nomor_pegawai = %s "
		values_temp = (nomor_pegawai, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE pegawai SET nomor_pegawai=nomor_pegawai """
		values = ()
		
		if "id_divisi" in data:
			id_divisi = data["id_divisi"]
			
			# cek apakah data kota ada
			query_temp = "SELECT id FROM divisi WHERE id = %s"
			values_temp = (id_divisi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data divisi tidak ditemukan")
			
			query += """ ,id_divisi = %s """
			values += (id_divisi, )

		if "nama" in data:
			nama = data["nama"]	
			query += """ ,nama = %s """
			values += (nama, )

		if "email" in data:
			email = data["email"]	
			query += """ ,email = %s """
			values += (email, )

		if "alamat" in data:
			alamat = data["alamat"]	
			query += """ ,alamat = %s """
			values += (alamat, )

		if "no_hp" in data:
			no_hp = data["no_hp"]	
			query += """ ,no_hp = %s """
			values += (no_hp, )
		
		query += """ WHERE nomor_pegawai = %s """
		values += (nomor_pegawai, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data pegawai"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))
	

@pegawai.route('/', methods=['DELETE'])
@jwt_required()
@cross_origin()
def delete_tempat_uji_kompetensi():
	ROUTE_NAME = str(request.path)

	id_user 		= str(get_jwt()["id_user"])
	role 			= str(get_jwt()["role"])

	nomor_pegawai = request.args.get("nomor_pegawai")
	
	try:
		dt = Data()
		data = request.json

		# Cek apakah data skema sertifikasi ada
		query_temp = " SELECT nomor_pegawai FROM pegawai WHERE nomor_pegawai = %s "
		values_temp = (nomor_pegawai, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ DELETE pegawai FROM pegawai WHERE nomor_pegawai = %s """
		values = (nomor_pegawai,)
		
		dt.insert_data(query, values)

		hasil = "Berhasil menghapus data pegawai"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= TEMPAT UJI KOMPETENSI AREA ==========================================================================