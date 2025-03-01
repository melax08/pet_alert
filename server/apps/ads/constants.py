ADS_PER_PAGE: int = 6
DIALOGS_PER_PAGE: int = 10
DESCRIPTION_MAP_LIMIT: int = 60
ROWS_IN_DIALOG_MESSAGE_FORM: int = 1

ADV_ATTRIBUTE_TEMPLATE_MAP: dict = {
    "type": "<b>Вид животного</b>: {}",
    "address": "<b>Адрес</b>: {}",
    "description": "<b>Описание объявления</b>:\n{}",
    "age": "<b>Возраст</b>: {}",
    "pet_name": "<b>Кличка</b>: {}",
    "condition": "<b>Состояние</b>: {}",
}

# Telegram image thumbnail settings
THUMBNAIL_GEOMETRY: str = "400x400"
THUMBNAIL_CROP: str = "center"
THUMBNAIL_QUALITY: int = 99
