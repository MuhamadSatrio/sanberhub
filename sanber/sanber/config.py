import os

#General
PRODUCT_NAME = "Sanberhub"
PRODUCT_ENVIRONMENT = "DEV" # DEV/PROD

IS_USE_VENV = "YES" # YES/NO
VENV_FOLDER_PATH = os.path.abspath(os.path.join(__file__,"../../../venv_app_name")) +"/" # Just Change value after __file__,

#JWT
JWT_SECRET_KEY = "JWT_SECRET_KEY"
JWT_HEADER_TYPE = "JWT"

#Database
DB_NAME     = "cggmnfbl"
DB_USER     = "cggmnfbl"
DB_PASSWORD = "uxUb0ekgvcdKmj-0MykMheqJ6Euv55Zd"
DB_HOST     = "rain.db.elephantsql.com"

#URL
BACKEND_BASE_URL = "https://localhost:20000/base_structure_python_flask/"

#Folder Path
# 2 variabel dibawah merupakan default logs dan upload (didalam direktori projek)
# 2 variabel dibawah jangan dihapus, jika tidak ingin menggunakan default
# cukup comment 2 variabel dibawah dan buat 2 variabel baru dengan nama yang sama
UPLOAD_FOLDER_PATH  = os.path.abspath(os.path.join(__file__,"../../upload")) +"/"
LOGS_FOLDER_PATH    = os.path.abspath(os.path.join(__file__,"../../logs"))

#CRONTAB
CRON_FOLDER_PATH            = os.path.abspath(os.path.join(__file__,"../crontab")) +"/"
CRON_TEMPLATE_PATH          = os.path.abspath(os.path.join(__file__,"../crontab/templates")) +"/"
CRON_ERROR_LOG_FOLDER_PATH  = os.path.abspath(os.path.join(__file__,"../crontab/crontab_error_logs")) +"/"
