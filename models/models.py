from datetime import datetime
from decimal import Decimal
from uuid import UUID
from tortoise import Model, fields


class User(Model):
    """данные о пользователях"""
    uuid: UUID = fields.UUIDField(pk=True)
    telegram_id: int = fields.BigIntField(unique=True)
    tg_username: str = fields.CharField(max_length=255, null=True)
    wallet: str = fields.CharField(max_length=255, null=True)
    balance: float = fields.FloatField(default=0)
    frozen_balance: float = fields.FloatField(default=0)
    description: str = fields.TextField(null=True)
    referal_user: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="children_referal", null=True
    )
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    lang: str = fields.CharField(max_length=30, null=True)
    
    children_referal: fields.ReverseRelation["User"]
    history_balance: fields.ReverseRelation["UserBalanceChange"]
    send_referal: fields.ReverseRelation["UserReferalBonus"]
    get_referal: fields.ReverseRelation["UserReferalBonus"]
    payments_account: fields.ReverseRelation["UserPaymentAccount"]

    @property
    def permission_balance(self):
        return self.balance - self.frozen_balance

    class Meta:
        table = 'user'


TYPE_FIELD = ['topup', 'withdraw']
STATE_FIELD = ['created', "done", "failed"]
class UserBalanceChange(Model):
    """ данные пополнениях и списаниях баланса в Toncoin пользователя"""
    uuid: UUID = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="history_balance")
    type: str = fields.CharField(max_length=255)
    amount: float = fields.FloatField(null=True)
    hash: str = fields.CharField(max_length=255, null=True)
    wallet: str = fields.CharField(max_length=255, null=True)
    code: str = fields.CharField(max_length=255, null=True)
    state: str = fields.CharField(max_length=255)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "user_balance_change"


STATE_FIELD = ["created" ,"done" ,"cancelled"]
class UserReferalBonus(Model):
    """данные о вознаграждениях пользователям за регистрацию по их приглашениям"""
    uuid: UUID = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="send_referal")
    invited_user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="get_referal")
    state: str = fields.CharField(max_length=255)
    amount: float = fields.FloatField(default=1)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_referal_bonus"


class Lang(Model):
    """таблица с переводами всех названий и сообщений бота"""
    uuid: UUID = fields.UUIDField(pk=True)
    target_table: str = fields.CharField(max_length=255, null=True)
    target_id: int = fields.UUIDField(null=True)
    rus: str = fields.TextField()
    eng: str = fields.TextField()
    description: str = fields.CharField(max_length=255, null=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "lang"


class Currency(Model):
    """валюта платежа"""
    uuid: UUID = fields.UUIDField(pk=True)
    name: str = fields.CharField(max_length=255, unique=True)
    exchange_rate: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2)
    is_active: bool = fields.BooleanField()
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    user_payment_account_type: fields.ReverseRelation["UserPaymentAccountType"]
    class Meta:
        table = "currency"


class UserPaymentAccountType(Model):
    """способ оплаты, на который можно отправлять фиат при покупке Toncoin"""
    uuid: UUID = fields.UUIDField(pk=True)
    serial_int: int = fields.IntField(generated=True)
    name: str = fields.CharField(max_length=255)
    currency: fields.ForeignKeyRelation["Currency"] = fields.ForeignKeyField("models.Currency", related_name="user_payment_account_type")
    data = fields.JSONField()
    is_active: bool = fields.BooleanField()
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    payments_account: fields.ReverseRelation['UserPaymentAccount']

    class Meta:
        table = "user_payment_account_type"

    def __str__(self) -> str:
        return self.name

class UserPaymentAccount(Model):
    """данные о счете пользователя, на который можно отправлять фиат при покупке Toncoin"""
    uuid: UUID = fields.UUIDField(pk=True)
    serial_int: int = fields.IntField(generated=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="payments_account")
    type: fields.ForeignKeyRelation["UserPaymentAccountType"] = fields.ForeignKeyField("models.UserPaymentAccountType", related_name="payments_account")
    data = fields.JSONField()
    is_active: bool = fields.BooleanField()
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    
    order_user_payment_account: fields.ReverseRelation["OrderUserPaymentAccount"]
    
    class Meta:
        table = "user_payment_account"


class Staff(Model):
    """данные о администраторах системы"""
    uuid: UUID = fields.UUIDField(pk=True)
    login: str = fields.CharField(max_length=255)
    password: str = fields.TextField()
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    superuser: bool = fields.BooleanField(default=False)

    class Meta:
        table = "staff"


STATE_FIELD = ['created', 'ready_for_sale', 'wait_buyer_send_funds', 
               'buyer_sent_funds', 'seller_approved_funds', 'done', 'problem_seller_no_funds',
               'need_admin_resolution', 'request_cancelled_by_seller', 'cancelled_by_seller']
class Order(Model):
    """заказ на покупку-продажу Toncoin"""
    uuid: UUID = fields.UUIDField(pk=True)
    serial_int: int = fields.IntField(generated=True)
    state: str = fields.CharField(max_length=255)
    seller: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="sell_orders")
    customer: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField("models.User", related_name="buy_orders", null=True)
    currency: fields.ForeignKeyRelation["Currency"] = fields.ForeignKeyField("models.Currency", related_name="orders")
    amount: float = fields.FloatField()
    origin_amount: float = fields.FloatField()
    margin: int = fields.IntField()
    final_price: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, null=True)
    commission: float = fields.FloatField()
    min_buy_sum: float = fields.FloatField()
    parent: fields.ForeignKeyNullableRelation["Order"] = fields.ForeignKeyField(
        "models.Order", related_name="children_order", null=True, on_delete="SET NULL"
    )
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    customer_pay_type: fields.ForeignKeyNullableRelation["UserPaymentAccountType"]  \
                      = fields.ForeignKeyField("models.UserPaymentAccountType", related_name="customer_pay_type", null=True, on_delete="SET NULL")

    order_user_payment_account: fields.ReverseRelation["OrderUserPaymentAccount"]
    children_order: fields.ReverseRelation["Order"]
    payment_operation: fields.ReverseRelation["PaymentOperation"]
    
    class Meta:
        table = "order"


class OrderUserPaymentAccount(Model):
    """модель изменения статуса заказ Order"""
    uuid: UUID = fields.UUIDField(pk=True)
    order: fields.ForeignKeyRelation['Order'] = fields.ForeignKeyField("models.Order", related_name="order_user_payment_account")
    account: fields.ForeignKeyRelation['UserPaymentAccount'] = fields.ForeignKeyField("models.UserPaymentAccount", related_name="order_user_payment_account")
    is_active: bool = fields.BooleanField()
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "order_user_payment_account"


class OrderStateChange(Model):
    """модель изменения статуса заказ Order"""
    uuid: UUID = fields.UUIDField(pk=True)
    order: fields.ForeignKeyRelation['Order'] = fields.ForeignKeyField("models.Order", related_name="order_state_change")
    old_state: str = fields.CharField(max_length=255)
    new_state: str = fields.CharField(max_length=255)
    staff: fields.ForeignKeyNullableRelation = fields.ForeignKeyField("models.Staff", related_name="order_state_change", null=True)
    description: str = fields.TextField(null=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "order_state_change"


class OrderAmountChange(Model):
    """модель изменения продаваемого количества Toncoin в заказе Order"""
    uuid: UUID = fields.UUIDField(pk=True)
    order: fields.ForeignKeyRelation['Order'] = fields.ForeignKeyField("models.Order", related_name="order_amount_change")
    target_order: fields.ForeignKeyNullableRelation['Order'] = fields.ForeignKeyField("models.Order", related_name="target_order_amount_change", null=True)
    old_amount: float = fields.FloatField()
    new_amount: float = fields.FloatField()
    staff: fields.ForeignKeyNullableRelation = fields.ForeignKeyField("models.Staff", related_name="order_amount_change", null=True)
    description: str = fields.TextField(null=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "order_amount_change"


class PaymentOperation(Model):
    """операция перечисления средств от покупателя продавцу"""
    uuid: UUID = fields.UUIDField(pk=True)
    order: fields.ForeignKeyRelation['Order'] = fields.ForeignKeyField("models.Order", related_name="payment_operation")
    sender: fields.ForeignKeyRelation['User'] = fields.ForeignKeyField("models.User", related_name="payment_operation_sender")
    recipient: fields.ForeignKeyRelation['User'] = fields.ForeignKeyField("models.User", related_name="payment_operation_recipient")
    recipient_data: str = fields.TextField()
    state: str = fields.CharField(max_length=255)
    check: str = fields.CharField(max_length=255, null=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "payment_operation"


class ProblemOrderProof(Model):
    uuid: UUID = fields.UUIDField(pk=True)
    order: fields.ForeignKeyRelation['Order'] = fields.ForeignKeyField("models.Order", related_name="proof_problem_order")
    file_path: str = fields.CharField(max_length=255)

    class Meta:
        table = "order_proof"