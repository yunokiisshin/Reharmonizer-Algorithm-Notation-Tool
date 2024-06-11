from flask import render_template, request
from app import app
from app.modules import drumSolver, Notation, noteSolver, rant, utils  

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/process', methods=['POST'])
def process():
    # Example: Using existing Python functions
    if request.method == 'POST':
        input_data = request.form['input_data']
        result = some_function(input_data)  # Call functions from modules here
        return render_template('result.html', result=result)

def some_function(data):
    # Example function using your existing modules
    return utils.some_utility_function(data)  # Replace with actual function calls
