from typing import List
from uuid import UUID
from fastapi import Request
from tortoise.exceptions import DoesNotExist
from jinja_func import flash
from models import models

# class Form:


class UpdateOrderForm:
    errors: List = []
    
    all_state = ('created', 'ready_for_sale' ,'wait_buyer_send_funds',
                'buyer_sent_funds' ,'seller_approved_funds' ,'done',
                'problem_seller_no_funds' ,'need_admin_resolution' ,'request_cancelled_by_seller',
                'cancelled_by_seller' ,'cancelled_by_customer' ,'suspended')

    def __init__(self, request: Request):
        self.request: Request = request
        self.parent_id: UUID = None
        self.seller_id: UUID = None
        self.customer_id: UUID = None
        self.currency_id: UUID = None
        self.origin_amount: float = None
        self.amount: float = None
        self.commission: float = None
        self.margin: float = None
        self.min_buy_sum: float = None
        self.final_price: float = None


    async def load_data(self):
        form = await self.request.form()
        self.parent_id = form.get("parent_id") if form.get("parent_id") else None
        self.seller_id = form.get("seller_id") if form.get("seller_id") else None
        self.customer_id = form.get("customer_id") if form.get("cutomer_id") else None
        self.currency_id = form.get("currency_id") if form.get("currency_id") else None
        self.origin_amount = form.get("origin_amount") if form.get("origin_amount") else None 
        self.amount = form.get("amount") if form.get("amount") else None 
        self.commission = form.get("commission") if form.get("commission") else None
        self.margin = form.get("margin") if form.get("margin") else None
        self.min_buy_sum = form.get("min_buy_sum") if form.get("min_buy_sum") else None
        self.final_price = form.get("final_price") if form.get("final_price") else None

    async def is_valid(self):
        if self.parent_id:
            try:
                self.parent_id = UUID(self.parent_id)
                await models.Order.get(uuid=self.parent_id)
            except (ValueError, DoesNotExist) as exc:
                if isinstance(exc, ValueError):
                    self.errors.append("Error parent UUID")
                else:
                    self.errors.append("Parent order does not exist")
        
        if self.seller_id:
            try:
                self.seller_id = UUID(self.seller_id)
                await models.User.get(uuid=self.seller_id)
            except (ValueError, DoesNotExist) as exc:
                if isinstance(exc, ValueError):
                    self.errors.append("Error seller UUID")
                else:
                    self.errors.append("Seller does not exist")
        else:
            self.errors.append("Seller required")
            
        if self.customer_id:
            try:
                self.customer_id = UUID(self.customer_id)
                await models.User.get(uuid=self.customer_id)
            except (ValueError, DoesNotExist) as exc:
                if isinstance(exc, ValueError):
                    self.errors.append("Error customer UUID")
                else:
                    self.errors.append("Customer does not exist")

        if self.currency_id:
            try:
                self.currency_id = UUID(self.currency_id)
                await models.Currency.get(uuid=self.currency_id)
            except (ValueError, DoesNotExist) as exc:
                if isinstance(exc, ValueError):
                    self.errors.append("Error currency UUID")
                else:
                    self.errors.append("Currency does not exist")

        if self.origin_amount:
            try:
                self.origin_amount = float(self.origin_amount)
                if self.origin_amount < 0:
                    self.errors.append("Error origin amount value")
            except ValueError:
                self.errors.append("Origin amount is not digit")
        else:
            self.errors.append("Origin amount is required")
        print(self.amount)
        if self.amount:
            try:
                self.amount = float(self.amount)
                if self.amount < 0:
                    self.errors.append("Error amount value")
            except ValueError:
                self.errors.append("amount is not digit")
        else:
            self.errors.append("amount is required")
        

        if self.commission:
            try:
                self.commission = float(self.commission)
                if self.commission < 0:
                    raise ValueError 
            except ValueError:
                self.errors.append("Commission is not digit")
        else:
            self.errors.append("Commission is required")
        
        if self.margin:
            try:
                self.margin = int(self.margin)
                if (0 < self.margin <= 100) is False:
                    self.errors.append("Error margin value")
            except ValueError:
                self.errors.append("Margin is not digit")
        else:
            self.errors.append("Margin is required")


        if self.min_buy_sum:
            try:
                self.min_buy_sum = float(self.min_buy_sum)
                if self.min_buy_sum < 0:
                    self.errors.append("Error min buy sum value")
            except ValueError:
                self.errors.append("Min buy sum is not digit")
        else:
            self.errors.append("Min buy sum is required")
        
        if self.final_price:
            try:
                self.final_price = float(self.final_price)
                if self.final_price < 0:
                    self.errors.append("Error final price value")
            except ValueError:
                self.errors.append("Final price is not digit")
       
        if not self.errors:
            return True
        return False
    
    def flash_error(self):
        for error in self.errors:
            flash(self.request, error, "danger")


class UpdateOrderAmountForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.amount: float = None
        self.description: str = None
    
    async def load_data(self):
        form = await self.request.form()
        self.amount = form.get("amount") if form.get("amount") else None
        self.description = form.get("description") if form.get("description") else None
    
    def is_valid(self):
        try:
            self.amount = float(self.amount)
            if self.amount < 0:
                self.errors.append("Error amount value")
        except (ValueError, TypeError) as exc:
            if isinstance(exc, ValueError):
                self.errors.append("Amount is not digit")
            else:
                self.errors.append("Amount is required")
        
        if not self.description:
            self.errors.append("Description is required")
        
        if not self.errors:
            return True
        return False
    
    def flash_error(self):
        for error in self.errors:
            flash(self.request, error, "danger")




class UpdateOrderStateForm:
    all_state = ('created', 'ready_for_sale' ,'wait_buyer_send_funds',
                'buyer_sent_funds' ,'seller_approved_funds' ,'done',
                'problem_seller_no_funds' ,'need_admin_resolution' ,'request_cancelled_by_seller',
                'cancelled_by_seller' ,'cancelled_by_customer' ,'suspended')

    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.state: float = None
        self.description: str = None
    
    async def load_data(self):
        form = await self.request.form()
        self.state = form.get("state") if form.get("state") else None
        self.description = form.get("description") if form.get("description") else None
    
    def is_valid(self):
        if not self.state:
            self.errors.append("Description is required")
        if self.state not in self.all_state:
            self.errors.append("Unknown state")

        if not self.description:
            self.errors.append("Description is required")
        
        if not self.errors:
            return True
        return False
    
    def flash_error(self):
        for error in self.errors:
            flash(self.request, error, "danger")