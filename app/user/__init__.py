from flask import Blueprint

user = Blueprint('user', __name__,  static_folder='static', static_url_path='')

from . import views
from . import api