from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str


LOGGER_CHANEL_ID = env.int("LOGGER_CHANEL_ID")
NOTIFICATION_GROUP_ID = env.int("NOTIFICATION_GROUP_ID")

USER = env.str('USER_DB')
PASSWORD = env.str('PASSWORD')
HOST = env.str('HOST')
PORT = env.str('PORT')
DATABASE = env.str('DATABASE')

WEBHOOK_PATH = f"/bot"
WEBHOOK_HOST = env.str('WEBHOOK_HOST')
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH


POSTGRES_URI = f"postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "UTC"
}

