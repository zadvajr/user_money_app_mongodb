from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from schemas.account import AccountCreatePayload, AccountCreate, Account
from database import accounts_collection
from schemas.transaction import DepositTransactionPayload
from schemas.user import User
from serializers import account_serializer
from bson.objectid import ObjectId


class AccountService:

    @staticmethod
    def create_account(account_data: AccountCreatePayload, user: User) -> Account:
        account_data = account_data.model_dump()
        account_with_defaults = Account(
            **account_data,
            user_id=user.id,
            balance=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        account_id = accounts_collection.insert_one(jsonable_encoder(account_with_defaults)).inserted_id
        account = accounts_collection.find_one({"_id": account_id})
        return account_serializer(account)


    @staticmethod
    def get_account(user: User):
        account = accounts_collection.find_one({"user_id": user.id})
        return account_serializer(account)
    

    @staticmethod
    def get_account_by_id(account_id: str):
        account = accounts_collection.find_one({"_id": ObjectId(account_id)})
        return account_serializer(account)

    @staticmethod
    def deposit_fund(deposit_payload: DepositTransactionPayload, account_id):
        account = AccountService.get_account_by_id(account_id)
        old_balance = float(account.balance)
        new_balance = old_balance + float(deposit_payload.amount)
        account.balance = new_balance
        account = accounts_collection.find_one_and_update(
            {"_id": ObjectId(account.id)},
            {"$set": {"balance": new_balance}}
        )
        return "successful"


account_service = AccountService()
