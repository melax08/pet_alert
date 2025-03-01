from server.settings.components import config

# Yandex maps

YA_MAPS_API_KEY = config("YA_MAPS_API_KEY")
YA_MAPS_SUGGEST_API_KEY = config("YA_MAPS_SUGGEST_API_KEY")

# Telegram

TELEGRAM_TOKEN = config("TELEGRAM_TOKEN", default="")
