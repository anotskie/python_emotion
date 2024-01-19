import mysql.connector
import pandas as pd
import os
import csv
import final_emotioncam_teams as emotioncam
import final_eyegazecam_teams as eyegazecam

# REGISTER STUDENT ACCOUNT
def student_signup(lastname, firstname, email, password):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
)
  try:
    mycursor = realtime_db.cursor()

    sql = '''
            INSERT INTO student_tbl (stud_LastName, stud_FirstName, stud_YearLevel, stud_Email, stud_Password) VALUES (%s, %s, %s, %s, %s)
          '''
    values = (f'{lastname}', f'{firstname}', '1', f'{email}', f'{password}')
    mycursor.execute(sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# REGISTER PROFESSOR ACCOUNT
def prof_signup(lastname, firstname, email, password):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
)
  try:
    mycursor = realtime_db.cursor()

    sql = '''
            INSERT INTO professor_tbl (professor_LastName, professor_FirstName, professor_desc, professor_Email, professor_Password) VALUES (%s, %s, %s, %s, %s)
          '''
    values = (f'{lastname}', f'{firstname}', '', f'{email}', f'{password}')
    mycursor.execute(sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# CHECK STUDENT CREDENTIALS
def login_student(email, password):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
)
  success = False

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    sql = '''
            SELECT * FROM student_tbl WHERE stud_Email=%s AND stud_Password=%s
          '''

    mycursor.execute(sql, (email, password))

    records = mycursor.fetchall()

    for row in records:
      registered_email = row["stud_Email"]
      registered_pass = row["stud_Password"]

      if registered_email == email and registered_pass == password:
        success = True

    realtime_db.commit()

  except mysql.connector.Error as e:
      print("Error reading data from MySQL table", e)

  finally:
    realtime_db.close()
  
  print(success)

  return success

# CHECK PROFESSOR CREDENTIALS
def login_professor(email, password):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
)
  success = False

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    sql = '''
            SELECT * FROM professor_tbl WHERE professor_Email=%s AND professor_Password=%s
          '''
    
    mycursor.execute(sql, (email, password))

    records = mycursor.fetchall()

    for row in records:
      registered_email = row["professor_Email"]
      registered_pass = row["professor_Password"]

      if registered_email == email and registered_pass == password:
        success = True

    realtime_db.commit()

  except mysql.connector.Error as e:
      print("Error reading data from MySQL table", e)

  finally:
    realtime_db.close()
  
  print(success)

  return success

# CHECK ADMIN CREDENTIALS
def login_admin(email, password):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
)
  success = False

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    sql = '''
            SELECT * FROM admin_tbl WHERE admin_Email=%s AND admin_Password=%s
          '''

    mycursor.execute(sql, (email, password))

    records = mycursor.fetchall()

    for row in records:
      registered_email = row["admin_Email"]
      registered_pass = row["admin_Password"]

      if registered_email == email and registered_pass == password:
        success = True

    realtime_db.commit()

  except mysql.connector.Error as e:
      print("Error reading data from MySQL table", e)

  finally:
    realtime_db.close()
  
  print(success)

  return success

# Convert image to Binary Data
def imgToBinaryData(image_pathfile):
  # Convert digital data to binary format
  with open(image_pathfile, 'rb') as file:
    binaryData = file.read()
      
  return binaryData

# Function to get student ID using email
def get_stud_ID(email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    select_sql = '''
                  SELECT student_ID FROM student_tbl WHERE stud_Email=%s
                '''
    select_value = ((email,))
    mycursor.execute(select_sql, (select_value))

    stud_records = mycursor.fetchall()

    for row in stud_records:
      stud_ID = row['student_ID']
      print(stud_ID)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return stud_ID

# Function to get professor ID using email
def get_prof_ID(email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    select_sql = '''
                  SELECT professor_ID FROM professor_tbl WHERE professor_Email=%s
                '''
    select_value = ((email,))
    mycursor.execute(select_sql, (select_value))

    prof_records = mycursor.fetchall()

    for row in prof_records:
      prof_ID = row['professor_ID']

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return prof_ID

# Function to get admin ID using email
def get_admin_ID(email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    select_sql = '''
                  SELECT admin_ID FROM admin_tbl WHERE admin_Email=%s
                '''
    select_value = ((email,))
    mycursor.execute(select_sql, (select_value))

    admin_records = mycursor.fetchall()

    for row in admin_records:
      admin_ID = row['admin_ID']

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return admin_ID

# DISPLAY SUMMARY REPORT
def emotion_summary_report(email):
  data = pd.read_csv (r"emotion_output.csv")
  dataframe = pd.DataFrame(data)

  try:
    realtime_db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="realtime_test_db"
      # host="sql12.freesqldatabase.com",
      # user="sql12667483",
      # password="WIpJivQd9R",
      # database="sql12667483"
      )

    for index, row in dataframe.iterrows():
      pathfile = os.getcwd() + "\\" + row['path'] + "\\image0.jpg"
      img_data = imgToBinaryData(pathfile)
      stud_ID = get_stud_ID(email)
      xmin = row['xmin']
      ymin = row['ymin']
      xmax = row['xmax']
      ymax = row['ymax']
      confidence = row['confidence']
      class_num = row['class']
      name = row['name']
      date = row['date']
      time = row['time']

      try:
        mycursor = realtime_db.cursor()

        insert_sql = '''
                      INSERT INTO emotion_tbl (emotion_xmin, emotion_ymin, emotion_xmax, emotion_ymax, emotion_confidence, emotion_class, emotion_name, emotion_date_captured, emotion_time_captured, emotion_img, emotion_student_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
        values = (xmin, ymin, xmax, ymax, confidence, class_num, name, date, time, img_data, stud_ID)
        mycursor.executemany(insert_sql, (values,))

        realtime_db.commit()
      except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)

  finally:
    realtime_db.close()

# DISPLAY SUMMARY REPORT
def eyegaze_summary_report(email):
  data = pd.read_csv (r"eyegaze_output.csv")
  dataframe = pd.DataFrame(data)

  try:
    realtime_db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="realtime_test_db"
      # host="sql12.freesqldatabase.com",
      # user="sql12667483",
      # password="WIpJivQd9R",
      # database="sql12667483"
      )

    for index, row in dataframe.iterrows():
      pathfile = os.getcwd() + "\\" + row['path'] + "\\image0.jpg"
      img_data = imgToBinaryData(pathfile)
      stud_ID = get_stud_ID(email)
      xmin = row['xmin']
      ymin = row['ymin']
      xmax = row['xmax']
      ymax = row['ymax']
      confidence = row['confidence']
      class_num = row['class']
      name = row['name']
      date = row['date']
      time = row['time']

      try:
        mycursor = realtime_db.cursor()

        insert_sql = '''
                      INSERT INTO eyegaze_tbl (eyegaze_xmin, eyegaze_ymin, eyegaze_xmax, eyegaze_ymax, eyegaze_confidence, eyegaze_class, eyegaze_name, eyegaze_date_captured, eyegaze_time_captured, eyegaze_img, eyegaze_student_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
        values = (xmin, ymin, xmax, ymax, confidence, class_num, name, date, time, img_data, stud_ID)
        mycursor.executemany(insert_sql, (values,))

        realtime_db.commit()
      except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)

  finally:
    realtime_db.close()

# FUNCTION TO DELETE PREVIOUS EMOTION RECORDS
def delete_previous_emotion_records():
  os.remove(r"emotion_output.csv")
  emotioncam.move_folder()

# FUNCTION TO DELETE PREVIOUS EYE GAZE RECORDS
def delete_previous_eyegaze_records():
  os.remove(r"eyegaze_output.csv")
  eyegazecam.move_folder()

# FETCH EMOTION RECORDS THEN INPUT TO CSV FILE
def emotion_db_to_csv():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT emotion_tbl.emotion_name, emotion_tbl.emotion_date_captured, emotion_tbl.emotion_time_captured, CONCAT(student_tbl.stud_LastName, ", ", student_tbl.stud_FirstName) AS student_FullName
                  FROM emotion_tbl
                  INNER JOIN student_tbl ON emotion_tbl.emotion_student_ID = student_tbl.student_ID
                '''
    mycursor.execute(select_sql)

    with open(r"csv/emotion_db_to_csv.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# FETCH EYEGAZE RECORDS THEN INPUT TO CSV FILE
def eyegaze_db_to_csv():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT eyegaze_tbl.eyegaze_name, eyegaze_tbl.eyegaze_date_captured, eyegaze_tbl.eyegaze_time_captured, CONCAT(student_tbl.stud_LastName, ", ", student_tbl.stud_FirstName) AS student_FullName
                  FROM eyegaze_tbl
                  INNER JOIN student_tbl ON eyegaze_tbl.eyegaze_student_ID = student_tbl.student_ID
                '''
    mycursor.execute(select_sql)

    with open(r"csv/eyegaze_db_to_csv.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# GET STUDENT FIRST NAME
def get_stud_name(email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    select_sql = '''
                  SELECT student_tbl.stud_FirstName FROM student_tbl WHERE student_tbl.stud_Email=%s
                '''
    values = ((email,))
    mycursor.execute(select_sql, (values))

    student_records = mycursor.fetchall()

    for student in student_records:
      stud_firstname = student['stud_FirstName']

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()
  
  return stud_firstname

# GET PROFESSOR FIRST NAME
def get_prof_name(email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    select_sql = '''
                  SELECT professor_tbl.professor_FirstName FROM professor_tbl WHERE professor_tbl.professor_Email=%s
                '''
    values = ((email,))
    mycursor.execute(select_sql, (values))

    prof_records = mycursor.fetchall()

    for prof in prof_records:
      prof_firstname = prof['professor_FirstName']

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()
  
  return prof_firstname

# GET ADMIN FIRST NAME
def get_admin_name(email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor(dictionary=True)

    select_sql = '''
                  SELECT admin_tbl.admin_FirstName FROM admin_tbl WHERE admin_tbl.admin_Email=%s
                '''
    values = ((email,))
    mycursor.execute(select_sql, (values))

    admin_records = mycursor.fetchall()

    for admin in admin_records:
      admin_firstname = admin['admin_FirstName']

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()
  
  return admin_firstname

# ADD RECORD TO STUDENT AUDIT TRAIL
def add_record_stud_audittrail(stud_id, logdate, logtime, logstatus):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    sql = '''
            INSERT INTO student_audit_trail (audit_stud_ID, stud_audit_date_log, stud_audit_time_log	, stud_log_status) VALUES (%s, %s, %s, %s)
          '''
    values = (f'{stud_id}', f'{logdate}', f'{logtime}', f'{logstatus}')
    mycursor.execute(sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# ADD RECORD TO PROFESSOR AUDIT TRAIL
def add_record_prof_audittrail(prof_ID, logdate, logtime, logstatus):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    sql = '''
            INSERT INTO professor_audit_trail (audit_prof_ID, prof_audit_date_log, prof_audit_time_log	, prof_log_status) VALUES (%s, %s, %s, %s)
          '''
    values = (f'{prof_ID}', f'{logdate}', f'{logtime}', f'{logstatus}')
    mycursor.execute(sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# ADD RECORD TO ADMIN AUDIT TRAIL
def add_record_admin_audittrail(admin_ID, logdate, logtime, logstatus):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    sql = '''
            INSERT INTO admin_audit_trail (audit_admin_ID, admin_audit_date_log, admin_audit_time_log	, admin_log_status) VALUES (%s, %s, %s, %s)
          '''
    values = (f'{admin_ID}', f'{logdate}', f'{logtime}', f'{logstatus}')
    mycursor.execute(sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# FETCH STUDENT AUDIT TRAIL RECORDS THEN INPUT TO CSV FILE
def fetch_stud_audittrail():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT CONCAT(student_tbl.stud_LastName, ', ', student_tbl.stud_FirstName) AS student_FullName, student_audit_trail.stud_audit_date_log, student_audit_trail.stud_audit_time_log, student_audit_trail.stud_log_status
                  FROM student_audit_trail
                  INNER JOIN student_tbl ON student_audit_trail.audit_stud_ID = student_tbl.student_ID
                '''
    mycursor.execute(select_sql)

    with open(r"csv/stud_logsheet.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# FETCH PROFESSOR AUDIT TRAIL RECORDS THEN INPUT TO CSV FILE
def fetch_prof_audittrail():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT CONCAT(professor_tbl.professor_LastName, ', ', professor_tbl.professor_FirstName) AS professor_FullName, professor_audit_trail.prof_audit_date_log, professor_audit_trail.prof_audit_time_log, professor_audit_trail.prof_log_status
                  FROM professor_audit_trail
                  INNER JOIN professor_tbl ON professor_audit_trail.audit_prof_ID = professor_tbl.professor_ID
                '''
    mycursor.execute(select_sql)

    with open(r"csv/prof_logsheet.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# FETCH ADMIN AUDIT TRAIL RECORDS THEN INPUT TO CSV FILE
def fetch_admin_audittrail():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT CONCAT(admin_tbl.admin_LastName, ', ', admin_tbl.admin_FirstName) AS admin_FullName, admin_audit_trail.admin_audit_date_log, admin_audit_trail.admin_audit_time_log, admin_audit_trail.admin_log_status
                  FROM admin_audit_trail
                  INNER JOIN admin_tbl ON admin_audit_trail.audit_admin_ID = admin_tbl.admin_ID
                '''
    mycursor.execute(select_sql)

    with open(r"csv/admin_logsheet.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# Function to display all student users
def fetch_student_table():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT * FROM `student_tbl` WHERE 1
                '''
    mycursor.execute(select_sql)

    with open(r"csv/all_students.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# Function to display all professor users
def fetch_professor_table():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT * FROM `professor_tbl` WHERE 1
                '''
    mycursor.execute(select_sql)

    with open(r"csv/all_professors.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# Function to display all admin users
def fetch_admin_table():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT * FROM `admin_tbl` WHERE 1
                '''
    mycursor.execute(select_sql)

    with open(r"csv/all_admins.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# Function to display all admin users
def fetch_student_eyegaze_table():
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  try:
    mycursor = realtime_db.cursor()

    select_sql = '''
                  SELECT student_tbl.stud_Email, eyegaze_tbl.eyegaze_name, eyegaze_tbl.eyegaze_date_captured, eyegaze_tbl.eyegaze_time_captured
                  FROM eyegaze_tbl
                  INNER JOIN student_tbl ON eyegaze_tbl.eyegaze_student_ID = student_tbl.student_ID
                '''
    mycursor.execute(select_sql)

    with open(r"csv/student_eyegaze_tbl.csv", "w", newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in mycursor.description]) # write headers
      csv_writer.writerows(mycursor)

    realtime_db.commit()
  except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

# Function to update STUDENT DETAILS (except password)
def update_stud_info(lastname, firstname, year, prog, contactnum, bio, email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  success = True

  try:
    mycursor = realtime_db.cursor()

    update_sql = '''
                  UPDATE student_tbl
                  SET stud_LastName = %s, stud_FirstName = %s, stud_YearLevel = %s, stud_Course = %s, stud_ContactNo = %s, stud_Bio = %s
                  WHERE stud_Email = %s
                '''
    values = (f'{lastname}', f'{firstname}', f'{year}', f'{prog}', f'{contactnum}', f'{bio}', f'{email}')
    mycursor.execute(update_sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    success = False
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return success

# Function to update STUDENT ACCOUNT PASSWORD
def update_stud_password(password, email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  success = True

  try:
    mycursor = realtime_db.cursor()

    update_sql = '''
                  UPDATE student_tbl
                  SET stud_Password = %s
                  WHERE stud_Email = %s
                '''
    values = (f'{password}', f'{email}')
    mycursor.execute(update_sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    success = False
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return success

# Function to update PROFESSOR DETAILS (except password)
def update_prof_info(lastname, firstname, contactnum, desc, email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  success = True

  try:
    mycursor = realtime_db.cursor()

    update_sql = '''
                  UPDATE professor_tbl
                  SET professor_LastName = %s, professor_FirstName = %s, professor_ContactNo = %s, professor_desc = %s
                  WHERE professor_Email = %s
                '''
    values = (f'{lastname}', f'{firstname}', f'{contactnum}', f'{desc}', f'{email}')
    mycursor.execute(update_sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    success = False
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return success

# Function to update PROFESSOR ACCOUNT PASSWORD
def update_prof_password(password, email):
  realtime_db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="realtime_test_db"
  # host="sql12.freesqldatabase.com",
  # user="sql12667483",
  # password="WIpJivQd9R",
  # database="sql12667483"
  )

  success = True

  try:
    mycursor = realtime_db.cursor()

    update_sql = '''
                  UPDATE professor_tbl
                  SET professor_Password = %s
                  WHERE professor_Email = %s
                '''
    values = (f'{password}', f'{email}')
    mycursor.execute(update_sql, values)

    realtime_db.commit()
  except mysql.connector.Error as e:
    success = False
    print("Error reading data from MySQL table", e)
  finally:
    realtime_db.close()

  return success

# Function to update ADMIN DETAILS
def update_admin_info():
  pass