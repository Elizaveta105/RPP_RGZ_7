class Config:
    DB_NAME = "RPP_7_RGZ"
    DB_USER = "liza_u_nastya"
    DB_PASSWORD = "password"
    DB_HOST = "localhost"
    DB_PORT = 5432
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
