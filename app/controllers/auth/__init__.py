from flask import Blueprint
import logging


auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


from . import view