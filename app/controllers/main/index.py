from flask import render_template
from flask_login import login_required
from ..main import main

@main.route('/', methods=['GET', 'POST'])
@main.route('/portal', methods=['GET', 'POST'])
@login_required
def index():
    """_summary_
 
    Returns:
        _type_: _description_
    """
    #session.permanent = True

    return render_template('index.html')


       
