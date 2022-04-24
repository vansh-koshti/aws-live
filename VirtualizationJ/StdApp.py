from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = "addstudent1"
region = "us-west-2"

db_conn = connections.Connection(
    host="attendance.c4fhql9b7yel.us-west-2.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="password",
    db="attendance"

)
output = {}
table = 'student'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddStd.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('')


@app.route("/addstd", methods=['POST'])
def AddStd():
    std_id = request.form['std_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    course = request.form['course']
    status = request.form['status']


    insert_sql = "INSERT INTO stdinfo VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

 

    try:

        cursor.execute(insert_sql, (std_id, first_name, last_name, course, status))
        db_conn.commit()
        std_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "std-id-" + str(std_id) 
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(bucket).put_object(Key=emp_image_file_name_in_s3)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                bucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddStdOutput.html', name=std_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
