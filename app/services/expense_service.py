import os 
from pathlib import Path
from sqlalchemy import func
from app.models import *
from app import db
from app.utils.api_response import ApiResponse
from datetime import datetime, timedelta


class ExpenseService:
    def __init__(self, request=None,form=None):
        self.request = request
        self.form = form

    