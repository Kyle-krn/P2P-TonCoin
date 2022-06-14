from models import models
from loader import db
from data.config import TORTOISE_ORM

ru_wallet_filter = ""
eng_wallet_filter = ""

ru_sell_coin_filter = ""
eng_sell_coin_filter = ""

async def init_message_filter():
    await db.init(config=TORTOISE_ORM)
    global ru_wallet_filter
    global eng_wallet_filter
    wallet_model = await models.Lang.get(uuid="1c6e2674-b90c-4ce5-8612-166305cb7a0b")
    ru_wallet_filter = f"^({wallet_model.rus})$"
    eng_wallet_filter = f"^({wallet_model.eng})$"
    return ru_wallet_filter, eng_wallet_filter
    # global ru_sell_coin_filter
    # global eng_sell_coin_filter
    # sell_model = await models.Lang.get(uuid="e152a847-4a4c-489c-b610-c9d926122973")
    # ru_sell_coin_filter = f"^({sell_model.rus})$"
    # eng_sell_coin_filter = f"^({sell_model.eng})$"
    # print(ru_sell_coin_filter)