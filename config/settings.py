# PostgreSQL
POSTGRES_HOST = "65.1.203.54"
POSTGRES_PORT = 5432
POSTGRES_DATABASE = "BCT-BOT-QA"
POSTGRES_USERNAME = "admin"
POSTGRES_PASSWORD = "bct123456"
POSTGRES_SSL_MODE = "require"

# JWT
SECRET_KEY = "f9a4f1c6d4934ba81b12b6fa89dda24c9e41c3c3e8b2e512723c3efd451878a4"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# File Upload
FILE_UPLOAD_API_URL = "https://qacoreplugin.consulttechies.com/api/Media/UploadDocsOnR2"
FILE_UPLOAD_BUCKET_NAME = "bctbot-assets"
FILE_UPLOAD_KEY = None
FILE_UPLOAD_PUBLIC_URL = "https://mbot.consulttechies.com/"

# Allowed Hosts
ALLOWED_HOSTS = "*"

# Chatbot Configuration
CHATBOT_BASE_URL = "https://devchatagent.consulttechies.com"
CHATBOT_API_KEY = "BCT_CHATAGENT_API_KEY_1"
CHATBOT_TIMEOUT_SECONDS = 3000

# Lip Sync Configuration
LIP_SYNC_BASE_URL = "http://15.185.89.253:5002"
LIP_SYNC_TIMEOUT_SECONDS = 3000

# DB Bot Configuration
DB_BOT_BASE_URL = "https://dbengine.consulttechies.com"
DB_BOT_API_KEY = "BCT_CHATAGENT_API_KEY_1"
DB_BOT_TIMEOUT_SECONDS = 3000
