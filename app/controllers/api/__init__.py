from flask import Blueprint


api = Blueprint('api', __name__)

from . import api_config
from . import student_api
from . import enrollment_api
from . import schedules_api
from . import activities_api
from . import attendance_api
from . import finance_api
from . import expense_api