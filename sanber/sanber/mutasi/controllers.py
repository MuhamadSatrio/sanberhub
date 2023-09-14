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

mutasi = Blueprint('mutasi', __name__, static_folder = '../../upload/foto_mutasi', static_url_path="/media")

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

@mutasi.route('/get_mutasi', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_mutasi():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.id, b.no_rekening, a.kode_transaksi, a.nominal  FROM mutasi a 
					JOIN nasabah b 
					ON a.nasabah_id = b.id 
					WHERE a.id=a.id """
		values = ()

		page = request.args.get("page")
		id_mutasi = request.args.get("id_mutasi")
		no_rekening = request.args.get("no_rekening")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_mutasi:
			query += " AND a.id = %s "
			values += (id_mutasi, )
		if no_rekening:
			query += " AND b.no_rekening = %s "
			values += (no_rekening, )
		if search:
			query += """ AND CONCAT_WS("|", a.nasabah_id ) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "nominal_asc":
				query += " ORDER BY a.nominal ASC "
			if order_by == "nominal_desc":
				query += " ORDER BY a.nominal DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)

		if no_rekening and len(hasil) == 0:
			return defined_error("Gagal, data nasabah dengan no rekening tidak ditemukan")

		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"

		logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_mutasi = "+str(id_mutasi) + "- param_logs = "+param_logs+"\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

	
@mutasi.route('/update', methods=['PUT', 'OPTIONS'])
@cross_origin()
def update_mutasi():
	ROUTE_NAME = str(request.path)

	try:
		dt = Data()
		data = request.json

		id_mutasi = request.args.get("id_mutasi")

		query_temp = " SELECT id FROM mutasi WHERE id = %s "
		values_temp = (id_mutasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE mutasi SET id = id """
		values = ()

		if "kode_transaksi" in data:
			kode_transaksi = data["kode_transaksi"]
			query += """ ,kode_transaksi = %s """
			values += (kode_transaksi, )

		if "nominal" in data:
			nominal = data["nominal"]
			query += """ ,nominal = %s """
			values += (nominal, )
		
		query += """ WHERE id = %s """
		values += (id_mutasi, )
		dt.insert_data(query, values)

		hasil = "Success Update Mutasi"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_mutasi = "+str(id_mutasi)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_mutasi = " +str(id_mutasi)+"\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= MY PROFILE AREA ==========================================================================
