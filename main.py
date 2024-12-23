from flask import Flask, request, render_template
import os
from excel_to_db import import_excel_to_db, get_table_names
from calculate import get_premium  # Reimport get_premium function
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    total_premium = None
    error = None

    # Fetch all table names
    tables = get_table_names()

    if request.method == 'POST':
        # Handle Excel upload
        if 'upload_excel' in request.form:
            if 'file_upload' in request.files:
                file = request.files['file_upload']
                if file.filename.endswith('.xlsx'):
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)

                    # Import Excel data into database
                    try:
                        import_excel_to_db(filepath)
                        tables = get_table_names()  # Refresh table list
                    except Exception as e:
                        error = str(e)
                else:
                    error = "Only .xlsx files are supported"

        # Handle table deletion
        elif 'delete_table' in request.form:
            table_to_delete = request.form.get('table_to_delete')
            if table_to_delete:
                try:
                    delete_table(table_to_delete)
                    tables = get_table_names()  # Refresh table list
                except Exception as e:
                    error = str(e)

        # Handle death probability modification
        elif 'update_mortality_rate' in request.form:
            table_name = request.form.get('edit_table_name')
            age = request.form.get('edit_age', type=int)
            new_rate = request.form.get('new_mortality_rate', type=float)

            if table_name and age is not None and new_rate is not None:
                try:
                    update_mortality_rate(table_name, age, new_rate)
                except Exception as e:
                    error = str(e)

        # Handle premium calculation
        elif 'calculate_premium' in request.form:
            age = request.form.get('age', type=int)
            duration = request.form.get('duration', type=int)
            payment_duration = request.form.get('payment_duration', type=int)
            insurance_amount = request.form.get('insurance_amount', type=float)
            table_name = request.form.get('table_name')

            if age and duration and payment_duration and insurance_amount and table_name:
                try:
                    total_premium = get_premium(age, duration, payment_duration, insurance_amount, table_name)
                except Exception as e:
                    error = str(e)
            else:
                error = "Please fill in all required fields."

    return render_template('index.html', total_premium=total_premium, error=error, tables=tables)

def delete_table(table_name):
    mydb = mysql.connector.connect(
        host="localhost",
        user="tim",
        password="887414",
        database="LifeTableDB"
    )
    cursor = mydb.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        mydb.commit()
    finally:
        cursor.close()
        mydb.close()

def update_mortality_rate(table_name, age, new_rate):
    """
    Updates the death probability for a specific age in the given table.
    """
    mydb = mysql.connector.connect(
        host="localhost",
        user="tim",
        password="887414",
        database="LifeTableDB"
    )
    cursor = mydb.cursor()

    try:
        # Prepare the query to update the death probability
        query = f"UPDATE `{table_name}` SET `死亡機率` = %s WHERE `年齡` = %s"
        cursor.execute(query, (new_rate, str(age)))
        mydb.commit()
    finally:
        cursor.close()
        mydb.close()

if __name__ == '__main__':
    app.run(debug=True)
