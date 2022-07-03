
from typing import List
from uuid import UUID
from fastapi import Request

from loader import flash


class UserUpdateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.wallet: str = None
        self.balance: float = None
        self.frozen_balance: float = None
        self.referal_user_id: UUID = None
    
    async def load_data(self):
        form = await self.request.form()
        self.wallet = form.get("wallet") if form.get("wallet") else None
        self.balance = form.get("balance") if form.get("balance") else None
        self.frozen_balance = form.get("frozen_balance") if form.get("frozen_balance") else None
        self.referal_user_id = form.get("referal_user_id") if form.get("referal_user_id") else None
        
    def is_valid(self):
        try:
            self.balance = float(self.balance)
            if self.balance < 0:
                raise ValueError
        except (TypeError, ValueError):
            self.errors.append("Balance error value")

        try:
            self.frozen_balance = float(self.frozen_balance)
            if self.frozen_balance < 0:
                raise ValueError
        except (TypeError, ValueError):
            self.errors.append("Frozen balance error value")

        if self.referal_user_id:
            try:
                self.referal_user_id = UUID(self.referal_user_id)
            except ValueError:
                self.errors.append("Referal parent UUID error value")
        
        if not self.errors:
            return True
        return False

    def flash_error(self):
        for error in self.errors:
            flash(self.request, error, "danger")
        
