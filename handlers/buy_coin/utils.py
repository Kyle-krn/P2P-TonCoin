from keyboards.inline import buy_keyboards
from models import models
from tortoise.queryset import Q


async def check_unfinished_deal(user:models.User):
    query = Q(customer=user) & Q(Q(state="wait_buyer_send_funds") | Q(state="buyer_sent_funds") | Q(state="problem_seller_no_funds") | Q(state="need_admin_resolution"))
    buy_order_user = await models.Order.filter(query)
    if len(buy_order_user) > 0:
        keyboard = None
        if buy_order_user[0].state == "wait_buyer_send_funds":
            keyboard = await buy_keyboards.go_to_buy_order_keyboard(order_uuid=buy_order_user[0].uuid,
                                                                    user=user)
        return True, keyboard
    return False, None
    