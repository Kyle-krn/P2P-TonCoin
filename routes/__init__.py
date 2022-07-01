from .event_routes import event_router
# from .users_routes import user_router
from .history_balance_routes import history_balance_router
# from .login_routes import login_router
from .referal_routes import referal_router
# from .payments_routes import payment_account_router
from .currency_routes import currency_router
from .order_by_routes import order_by_router

from .payments.route import payments_router
from .users.route import user_router
from .auth.route import auth_router
from .orders.route import order_router
from .lang.route import lang_router