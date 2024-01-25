import customtkinter as tk
import os
import hashlib
import time
import threading
import cv2
import PIL
import csv
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from PIL import ImageTk, Image
from tkinter import ttk, filedialog
from datetime import datetime, date
from matplotlib.backends.backend_pdf import PdfPages
import time
import operator
# Custom Library
import queries
import final_emotioncam_teams
import final_eyegazecam_teams
import logging

# Libraries to connect to Teams via Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


tk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
tk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# ============================ START ==================================

class App(tk.CTk):
    def __init__ (self):
        super().__init__()
        # Window configuration
        self.title("Real-time Eye Gaze and Emotion Detection App")
        self.geometry(f"{1100}x{600}")
        self.resizable(0,0)
        self.login_attempts = 0
        self.lockout_timer = None
        # Grid Layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.show_login_frame()

        self.failed_login_attempts = 0
        self.lockout_timer_start = 0
        self.lockout_duration = 180

    # ========== LOGIN FRAME =============
    def show_login_frame(self):
        # Background Image
        current_path = os.path.dirname(os.path.realpath(__file__))
        # self.bg_image = tk.CTkImage(Image.open(current_path + r"/pics/letran.png"), size=(1100, 600))
        # self.bg_image = tk.CTkImage(Image.open(os.getcwd() + "\_internal\pics\letran.png", 'r'), size=(1100, 600))
        self.bg_image = tk.CTkImage(Image.open(os.getcwd() + "\pics\letran.png", 'r'), size=(1100, 600))
        # self.bg_image = tk.CTkImage(Image.open(r"/pics/letran.png"), size=(1100, 600))
        self.bg_image_label = tk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Login Panel
        self.login_frame = tk.CTkFrame(self, corner_radius=0)
        self.login_frame.place(x=425, y=110)

        self.login_label = tk.CTkLabel(self.login_frame, text="Welcome!", font=tk.CTkFont(size=20, weight="bold"))
        self.login_label.grid(row=0, column=0, padx=30, pady=(30, 15))

        self.username_entry = tk.CTkEntry(self.login_frame, width=200, placeholder_text="email")
        self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))

        self.password_entry = tk.CTkEntry(self.login_frame, width=200, show="*", placeholder_text="password")
        self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))

        self.password = tk.BooleanVar()
        self.password.set(False)
        self.show_password = tk.CTkCheckBox(self.login_frame, text="Show Password", checkbox_width=15, checkbox_height=15, variable=self.password, command=self.toggle_password_visibility)
        self.show_password.grid(row=3, column=0, padx=30, pady=(0, 10))

        self.login_button = tk.CTkButton(self.login_frame, text="Login", command=self.login_event, width=200)
        self.login_button.grid(row=4, column=0, padx=30, pady=(15, 100))
        
        # ========== Forgot password =============
        self.forgot_password_label = tk.CTkLabel(self.login_frame, text="Forgot Password? Click here!", font=tk.CTkFont(size=12), cursor="hand2")
        self.forgot_password_label.grid(row=5, column=0, padx=30, pady=(10, 10))
        self.forgot_password_label.bind("<Button-1>", lambda event: self.show_forgot_password_panel())

        self.signup_label = tk.CTkLabel(self.login_frame, text="No account yet? Sign up here!")
        self.signup_label.place(x=40, y=275)

        self.signup_button = tk.CTkButton(self.login_frame, text="Sign Up", command=self.show_signup_panel, width=200)
        self.signup_button.place(x=30, y=305)
        
    # ========== Forgot EVENT =============
    def show_forgot_password_panel(self):
        # Create a new frame for forgot password
        self.forgot_password_frame = tk.CTkFrame(self, corner_radius=0)
        self.forgot_password_frame.place(x=425, y=110)

        self.forgot_password_label = tk.CTkLabel(self.forgot_password_frame, text="Forgot Password?", font=tk.CTkFont(size=20, weight="bold"))
        self.forgot_password_label.grid(row=0, column=0, padx=30, pady=(30, 15))

        self.email_entry = tk.CTkEntry(self.forgot_password_frame, width=200, placeholder_text="email")
        self.email_entry.grid(row=1, column=0, padx=30, pady=(15, 15))

        self.send_reset_button = tk.CTkButton(self.forgot_password_frame, text="Reset Password", command=self.reset_email, width=200)
        self.send_reset_button.grid(row=2, column=0, padx=30, pady=(15, 10))

        self.back_to_login_button = tk.CTkButton(self.forgot_password_frame, text="Back to Login", command=self.back_to_login, width=200)
        self.back_to_login_button.grid(row=3, column=0, padx=30, pady=(10, 100))

        # Hide the login frame
        self.login_frame.place_forget()

    def back_to_login(self):
        # Destroy the forgot password frame and show the login frame
        self.forgot_password_frame.destroy()
        self.show_login_frame()

    def reset_email(self):
        # Get the user-entered email
        self.email = self.email_entry.get()

        # Check if the email exists in the database
        if self.is_email_in_database(self.email):
            # Email exists, proceed to the next step
            self.show_reset_password_panel()
        else:
            # Email does not exist, show an error message
            self.show_email_not_found_error()


    def is_email_in_database(self, email):
        try:
            with mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="realtime_test_db"
            ) as realtime_db:
                mycursor = realtime_db.cursor()

                # Assuming you have a table named 'user_tbl' with an 'email' column
                sql = "SELECT COUNT(*) FROM student_tbl WHERE stud_email = %s"
                values = (email,)

                mycursor.execute(sql, values)
                result = mycursor.fetchone()[0]

                return result > 0  # If the count is greater than 0, the email exists
        except mysql.connector.Error as e:
            print("Error checking email existence in the database:", e)
            return False

    def show_email_not_found_error(self):
        
        self.incorrect_login_frame = tk.CTkFrame(self, width=390, height=150)
        self.incorrect_login_frame.place(x=360, y=200)

        # Confirmation Label
        self.success_signup_label = tk.CTkLabel(self.incorrect_login_frame, text="Email not found in the database")
        self.success_signup_label.place(x=120, y=30)
        
        self.back_to_login_button = tk.CTkButton(self.incorrect_login_frame, text="OK", width=100, command=self.retry_to_login)
        self.back_to_login_button.place(x=140, y=70)
        # # Destroy any existing error label to prevent overlap
        # for widget in self.forgot_password_frame.winfo_children():
        #     if isinstance(widget, tk.CTkLabel) and widget.cget("text") == "Email not found in the database":
        #         widget.destroy()

        # # Display an error message indicating that the email was not found
        # error_label = tk.CTkLabel(self.forgot_password_frame, text="Email not found in the database", fg="red")
        # error_label.grid(row=4, column=0, padx=30, pady=10)



    def show_reset_password_panel(self):
        self.forgot_password_frame.place_forget()
        self.reset_password_frame = tk.CTkFrame(self, corner_radius=0)
        self.reset_password_frame.place(x=425, y=110)

        self.new_password_entry = tk.CTkEntry(self.reset_password_frame, width=200, show="*", placeholder_text="New Password")
        self.new_password_entry.grid(row=0, column=0, padx=30, pady=(30, 15))

        self.confirm_reset_button = tk.CTkButton(self.reset_password_frame, text="Update Password", command=self.confirm_password_update, width=200)
        self.confirm_reset_button.grid(row=1, column=0, padx=30, pady=(15, 10))

        self.back_to_login_button = tk.CTkButton(self.reset_password_frame, text="Back to Login", command=self.back_to_login, width=200)
        self.back_to_login_button.grid(row=2, column=0, padx=30, pady=(10, 100))


    def confirm_password_update(self):
        # Get the user-entered new password
        new_password = self.new_password_entry.get()

        # Update the password in the database
        if self.update_password(self.email, new_password):
            # Password update successful, you can show a success message or navigate to the login panel
            print("Password updated successfully!")
            self.show_login_frame()
        else:
            # Password update failed, you can show an error message or handle accordingly
            print("Password update failed.")

    def update_password(self, email, new_password):
        try:
            with mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="realtime_test_db"
            ) as realtime_db:
                mycursor = realtime_db.cursor()

                # Hash the new password before updating (using SHA-256)
                hash_object = hashlib.sha256()
                hash_object.update(new_password.encode())
                hashed_password = hash_object.hexdigest()

                # Assuming you have a table named 'student_tbl' with columns 'stud_email' and 'stud_password'
                sql = "UPDATE student_tbl SET stud_password = %s WHERE stud_email = %s"
                values = (hashed_password, email)

                mycursor.execute(sql, values)
                realtime_db.commit()

                return True  # Password update successful
        except mysql.connector.Error as e:
            print("Error updating password in the database:", e)
            return False

    # def show_login_frame(self):
    #     # Implement the logic to show the login frame
    #     pass

    # ========== SIGN UP PANEL =============
    def show_signup_panel(self):
        self.login_frame.place_forget()
        self.signup_panel()

    def signup_panel(self):
        # Window configuration
        self.title("Real-time Eye Gaze and Emotion Detection App")
        self.geometry(f"{1100}x{600}")
        self.resizable(0,0)

        # Grid Layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Signup Panel
        self.signup_frame = tk.CTkFrame(self, corner_radius=0)
        self.signup_frame.place(x=400, y=3)

        self.signup_label = tk.CTkLabel(self.signup_frame, text="Sign up", font=tk.CTkFont(size=20, weight="bold"))
        self.signup_label.grid(row=0, column=0, padx=30, pady=(30, 15))

        self.signup_username_entry = tk.CTkEntry(self.signup_frame, width=200, placeholder_text="Email")
        self.signup_username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))

        self.signup_firstname_entry = tk.CTkEntry(self.signup_frame, width=200, placeholder_text="First Name")
        self.signup_firstname_entry.grid(row=2, column=0, padx=30, pady=(15, 15))

        self.signup_lastname_entry = tk.CTkEntry(self.signup_frame, width=200, placeholder_text="Last Name")
        self.signup_lastname_entry.grid(row=3, column=0, padx=30, pady=(15, 15))

        self.signup_password_entry = tk.CTkEntry(self.signup_frame, width=200, show="*", placeholder_text="Password")
        self.signup_password_entry.grid(row=4, column=0, padx=30, pady=(15, 15))

        self.signup_confirmpassword_entry = tk.CTkEntry(self.signup_frame, width=200, show="*", placeholder_text="Confirm Password")
        self.signup_confirmpassword_entry.grid(row=5, column=0, padx=30, pady=(15, 20))

        self.radio_frame = tk.CTkFrame(self.signup_frame)
        self.radio_frame.grid(row=6, column=0, padx=(40, 40), pady=(0, 0), sticky="nsew")
        self.radio_var = tk.IntVar(value=0)
        self.student_option = tk.CTkRadioButton(master=self.radio_frame, variable=self.radio_var, value=1, text="Student", command=self.check_radio_selection)
        self.student_option.grid(row=1, column=0, padx=10, pady=10, sticky="")
        self.professor_option = tk.CTkRadioButton(master=self.radio_frame, variable=self.radio_var, value=2, text="Professor", command=self.check_radio_selection)
        self.professor_option.grid(row=1, column=1, padx=10, pady=10, sticky="")

        self.final_signup_button = tk.CTkButton(self.signup_frame, text="Submit", width=200, command=self.submit_registration)
        self.final_signup_button.grid(row=7, column=0, padx=30, pady=(20, 20))

        self.has_account_label = tk.CTkLabel(self.signup_frame, text="Already have an account?")
        self.has_account_label.grid(row=8, column=0, padx=15, pady=(15, 5))

        self.back_to_login_button = tk.CTkButton(self.signup_frame, text="Sign in", command=self.return_to_login, width=200)
        self.back_to_login_button.grid(row=9, column=0, padx=30, pady=(5, 30))

    # ============================================ AFTER LOGIN ============================================
    # ========= STUDENT SIDE PANEL =========
    def stud_default_main(self):
        # Window configuration
        self.title("Real-time Eye Gaze and Emotion Detection App")
        self.geometry(f"{1100}x{600}")
        self.resizable(0,0)

        # Grid Layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # SIDE PANEL
        self.stud_sidebar_frame = tk.CTkFrame(self, width=180, corner_radius=0)
        self.stud_sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.stud_sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo
        self.logo_label = tk.CTkLabel(self.stud_sidebar_frame, text="CustomLogo", font=tk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Dashboard Button
        self.sidebar_button_1 = tk.CTkButton(self.stud_sidebar_frame, text="Dashboard", command=self.stud_sidebar_dashboard_clicked)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        # Class Link Button
        self.sidebar_button_2 = tk.CTkButton(self.stud_sidebar_frame, text="Class Link", command=self.stud_sidebar_classlink_clicked)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        # Summary Report Button
        self.sidebar_button_3 = tk.CTkButton(self.stud_sidebar_frame, text="Summary Report", command=self.stud_sidebar_report_clicked)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Settings Button
        self.sidebar_button_4 = tk.CTkButton(self.stud_sidebar_frame, text="Settings", command=self.stud_sidebar_settings_clicked)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        # Logout Button
        self.sidebar_button_5 = tk.CTkButton(self.stud_sidebar_frame, text="Log Out", command=self.logout_clicked)
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)

        # Color Mode
        self.appearance_mode_label = tk.CTkLabel(self.stud_sidebar_frame, text="Switch Mode", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = tk.CTkSegmentedButton(self.stud_sidebar_frame, values=["Dark", "Light"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))

        # OCCUPATION CHECKER
        self.occupation_name = tk.CTkLabel(self.stud_sidebar_frame)
        self.occupation_name.place(x=10, y=450)
        self.occupation_name.lower()
    # ========= END =========

    # ========= PROFESSOR SIDE PANEL =========
    def prof_default_main(self):
        # Window configuration
        self.title("Real-time Eye Gaze and Emotion Detection App")
        self.geometry(f"{1100}x{600}")
        self.resizable(0,0)

        # Grid Layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # SIDE PANEL
        self.prof_sidebar_frame = tk.CTkFrame(self, width=180, corner_radius=0)
        self.prof_sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.prof_sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo
        self.logo_label = tk.CTkLabel(self.prof_sidebar_frame, text="CustomLogo", font=tk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Dashboard Button
        self.sidebar_button_1 = tk.CTkButton(self.prof_sidebar_frame, text="Dashboard", command=self.prof_sidebar_dashboard_clicked)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        # Class Link Button
        self.sidebar_button_2 = tk.CTkButton(self.prof_sidebar_frame, text="Class Link", command=self.prof_sidebar_classlink_clicked)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        # Summary Report Button
        self.sidebar_button_3 = tk.CTkButton(self.prof_sidebar_frame, text="Summary Report", command=self.prof_sidebar_report_clicked)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Settings Button
        self.sidebar_button_4 = tk.CTkButton(self.prof_sidebar_frame, text="Settings", command=self.prof_sidebar_settings_clicked)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        # Logout Button
        self.sidebar_button_5 = tk.CTkButton(self.prof_sidebar_frame, text="Log Out", command=self.logout_clicked)
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)

        # Color Mode
        self.appearance_mode_label = tk.CTkLabel(self.prof_sidebar_frame, text="Switch Mode", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = tk.CTkSegmentedButton(self.prof_sidebar_frame, values=["Dark", "Light"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))

        # OCCUPATION CHECKER
        self.occupation_name = tk.CTkLabel(self.prof_sidebar_frame)
        self.occupation_name.place(x=10, y=450)
        self.occupation_name.lower()
    # ========= END =========

    # ========= ADMIN SIDE PANEL =========
    def admin_default_main(self):
        # Window configuration
        self.title("Real-time Eye Gaze and Emotion Detection App")
        self.geometry(f"{1100}x{600}")
        self.resizable(0,0)

        # Grid Layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # SIDE PANEL
        self.admin_sidebar_frame = tk.CTkFrame(self, width=180, corner_radius=0)
        self.admin_sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.admin_sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo
        self.logo_label = tk.CTkLabel(self.admin_sidebar_frame, text="CustomLogo", font=tk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Dashboard Button
        self.sidebar_button_1 = tk.CTkButton(self.admin_sidebar_frame, text="Dashboard", command=self.admin_sidebar_dashboard_clicked)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        # Audit Trail Button
        self.sidebar_button_2 = tk.CTkButton(self.admin_sidebar_frame, text="Audit Trail", command=self.admin_audittrail_clicked)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        # Manage Users Button
        self.sidebar_button_3 = tk.CTkButton(self.admin_sidebar_frame, text="Manage Users", command=self.admin_manageusers_clicked)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Settings Button
        self.sidebar_button_4 = tk.CTkButton(self.admin_sidebar_frame, text="Settings", command=self.admin_sidebar_settings_clicked)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        # Logout Button
        self.sidebar_button_5 = tk.CTkButton(self.admin_sidebar_frame, text="Log Out", command=self.logout_clicked)
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)

        # Color Mode
        self.appearance_mode_label = tk.CTkLabel(self.admin_sidebar_frame, text="Switch Mode", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = tk.CTkSegmentedButton(self.admin_sidebar_frame, values=["Dark", "Light"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))

        # OCCUPATION CHECKER
        self.occupation_name = tk.CTkLabel(self.admin_sidebar_frame)
        self.occupation_name.place(x=10, y=450)
        self.occupation_name.lower()
    # ========= END =========

    # ========== MAIN PANELS =============
    # Open STUDENT DASHBOARD PANEL
    def stud_sidebar_dashboard_clicked(self):
        # MAIN DASHBOARD PANEL
        self.main_frame_dashboard_STUD = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_dashboard_STUD.place(x=180, y=0)

        student_firstname = queries.get_stud_name(self.username_entry.get())
        text = f"Welcome, {student_firstname}!"

        self.dashboard_welcome_stud = tk.CTkLabel(self.main_frame_dashboard_STUD, text=text)
        self.dashboard_welcome_stud.place(x=100, y=100)

        # self.console_msg = tk.CTkTextbox(self.main_frame_dashboard_STUD, height=100, width=500)
        # self.console_msg.place(x=100, y=150)

        # self.stud_bio_textbox.insert("1.0", sys.stdout.readline)
        # self.stud_bio_textbox.configure(state="disabled")

    # Open PROFESSOR DASHBOARD PANEL
    def prof_sidebar_dashboard_clicked(self):
        # MAIN DASHBOARD PANEL
        self.main_frame_dashboard_PROF = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_dashboard_PROF.place(x=180, y=0)

        professor_firstname = queries.get_prof_name(self.username_entry.get())
        text = f"Welcome, {professor_firstname}!"

        self.dashboard_welcome_stud = tk.CTkLabel(self.main_frame_dashboard_PROF, text=text)
        self.dashboard_welcome_stud.place(x=100, y=100)

    # Open ADMIN DASHBOARD PANEL
    def admin_sidebar_dashboard_clicked(self):
        # MAIN DASHBOARD PANEL
        self.main_frame_dashboard_ADMIN = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_dashboard_ADMIN.place(x=180, y=0)

        admin_firstname = queries.get_admin_name(self.username_entry.get())
        text = f"Welcome, {admin_firstname}!"

        self.dashboard_welcome_stud = tk.CTkLabel(self.main_frame_dashboard_ADMIN, text=text)
        self.dashboard_welcome_stud.place(x=100, y=100)

    # Open ADMIN AUDIT TRAIL PANEL
    def admin_audittrail_clicked(self):
        # MAIN AUDIT TRAIL PANEL
        self.main_frame_audittrail = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_audittrail.place(x=180, y=0)

        self.audittrail_tabview = tk.CTkTabview(self.main_frame_audittrail, width=700, height=500)
        self.audittrail_tabview.place(x=110, y=30)
        self.audittrail_tabview.add("Students")
        self.audittrail_tabview.add("Professors")
        self.audittrail_tabview.add("Admins")

        # TABLE FOR STUDENT AUDIT TRAIL
        self.stud_audit_table = ttk.Treeview(self.audittrail_tabview.tab("Students"), columns=('number', 'name', 'date', 'time', 'status'), show="headings")
        self.stud_audit_table.place(x=10, y=60)

        self.stud_audit_table.heading('number', text="No.")
        self.stud_audit_table.heading('name', text="Student Name")
        self.stud_audit_table.heading('date', text="Date")
        self.stud_audit_table.heading('time', text="Time")
        self.stud_audit_table.heading('status', text="Status")

        self.stud_audit_table.column('number', anchor="center")
        self.stud_audit_table.column('name', anchor="center")
        self.stud_audit_table.column('date', anchor="center")
        self.stud_audit_table.column('time', anchor="center")
        self.stud_audit_table.column('status', anchor="center")

        # Fetch student audit trail from database then input to CSV
        queries.fetch_stud_audittrail()

        # Open CSV then display to table
        with open(r'csv/stud_logsheet.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                student_name = row['student_FullName']
                datelog = row['stud_audit_date_log']
                timelog = row['stud_audit_time_log']
                logstatus = row['stud_log_status']
                self.stud_audit_table.insert("", "end", values=(count, student_name, datelog, timelog, logstatus))
                count = count+1

        # TABLE FOR PROFESSOR AUDIT TRAIL
        self.prof_audit_table = ttk.Treeview(self.audittrail_tabview.tab("Professors"), columns=('number', 'name', 'date', 'time', 'status'), show="headings")
        self.prof_audit_table.place(x=10, y=60)

        self.prof_audit_table.heading('number', text="No.")
        self.prof_audit_table.heading('name', text="Professor Name")
        self.prof_audit_table.heading('date', text="Date")
        self.prof_audit_table.heading('time', text="Time")
        self.prof_audit_table.heading('status', text="Status")

        self.prof_audit_table.column('number', anchor="center")
        self.prof_audit_table.column('name', anchor="center")
        self.prof_audit_table.column('date', anchor="center")
        self.prof_audit_table.column('time', anchor="center")
        self.prof_audit_table.column('status', anchor="center")

        # Fetch professor audit trail from database then input to CSV
        queries.fetch_prof_audittrail()

        # Open CSV then display to table
        with open(r'csv/prof_logsheet.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                professor_name = row['professor_FullName']
                datelog = row['prof_audit_date_log']
                timelog = row['prof_audit_time_log']
                logstatus = row['prof_log_status']
                self.prof_audit_table.insert("", "end", values=(count, professor_name, datelog, timelog, logstatus))
                count = count+1

        # TABLE FOR ADMIN AUDIT TRAIL
        self.admin_audit_table = ttk.Treeview(self.audittrail_tabview.tab("Admins"), columns=('number', 'name', 'date', 'time', 'status'), show="headings")
        self.admin_audit_table.place(x=10, y=60)

        self.admin_audit_table.heading('number', text="No.")
        self.admin_audit_table.heading('name', text="Admin Name")
        self.admin_audit_table.heading('date', text="Date")
        self.admin_audit_table.heading('time', text="Time")
        self.admin_audit_table.heading('status', text="Status")

        self.admin_audit_table.column('number', anchor="center")
        self.admin_audit_table.column('name', anchor="center")
        self.admin_audit_table.column('date', anchor="center")
        self.admin_audit_table.column('time', anchor="center")
        self.admin_audit_table.column('status', anchor="center")

        # Fetch admin audit trail from database then input to CSV
        queries.fetch_admin_audittrail()

        # Open CSV then display to table
        with open(r'csv/admin_logsheet.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                admin_name = row['admin_FullName']
                datelog = row['admin_audit_date_log']
                timelog = row['admin_audit_time_log']
                logstatus = row['admin_log_status']
                self.admin_audit_table.insert("", "end", values=(count, admin_name, datelog, timelog, logstatus))
                count = count+1

        # Modern look for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=50, fieldbackground="#343638", bordercolor="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=(None, 14))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

    # GET STUDENT LOGIN INFO FOR AUDIT TRAIL THEN STORE TO DATABASE
    def get_student_login_info(self):
        email = self.username_entry.get()
        student_ID = queries.get_stud_ID(email)
        logdate = date.today()
        logtime = datetime.now().strftime("%H:%M:%S")
        logstatus = "LOGGED IN"

        queries.add_record_stud_audittrail(student_ID, logdate, logtime, logstatus)

    # GET STUDENT LOGOUT INFO FOR AUDIT TRAIL THEN STORE TO DATABASE
    def get_student_logout_info(self):
        email = self.username_entry.get()
        student_ID = queries.get_stud_ID(email)
        logdate = date.today()
        logtime = datetime.now().strftime("%H:%M:%S")
        logstatus = "LOGGED OUT"

        queries.add_record_stud_audittrail(student_ID, logdate, logtime, logstatus)

    # GET PROFESSOR LOGIN INFO FOR AUDIT TRAIL THEN STORE TO DATABASE
    def get_professor_login_info(self):
        email = self.username_entry.get()
        professor_ID = queries.get_prof_ID(email)
        logdate = date.today()
        logtime = datetime.now().strftime("%H:%M:%S")
        logstatus = "LOGGED IN"

        queries.add_record_prof_audittrail(professor_ID, logdate, logtime, logstatus)

    # GET PROFESSOR LOGOUT INFO FOR AUDIT TRAIL THEN STORE TO DATABASE
    def get_professor_logout_info(self):
        email = self.username_entry.get()
        professor_ID = queries.get_prof_ID(email)
        logdate = date.today()
        logtime = datetime.now().strftime("%H:%M:%S")
        logstatus = "LOGGED OUT"

        queries.add_record_prof_audittrail(professor_ID, logdate, logtime, logstatus)

    # GET ADMIN LOGIN INFO FOR AUDIT TRAIL THEN STORE TO DATABASE
    def get_admin_login_info(self):
        email = self.username_entry.get()
        admin_ID = queries.get_admin_ID(email)
        logdate = date.today()
        logtime = datetime.now().strftime("%H:%M:%S")
        logstatus = "LOGGED IN"

        queries.add_record_admin_audittrail(admin_ID, logdate, logtime, logstatus)

    # GET ADMIN LOGOUT INFO FOR AUDIT TRAIL THEN STORE TO DATABASE
    def get_admin_logout_info(self):
        email = self.username_entry.get()
        admin_ID = queries.get_admin_ID(email)
        logdate = date.today()
        logtime = datetime.now().strftime("%H:%M:%S")
        logstatus = "LOGGED OUT"

        queries.add_record_admin_audittrail(admin_ID, logdate, logtime, logstatus)

    # Open ADMIN MANAGE USERS PANEL
    def admin_manageusers_clicked(self):
        # MAIN MANAGE USERS PANEL
        self.main_frame_manageusers = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_manageusers.place(x=180, y=0)

        self.manageusers_tabview = tk.CTkTabview(self.main_frame_manageusers, width=700, height=500)
        self.manageusers_tabview.place(x=110, y=30)
        self.manageusers_tabview.add("Students")
        self.manageusers_tabview.add("Professors")
        self.manageusers_tabview.add("Admins")

        # TABLE FOR STUDENT MANAGE USERS
        self.stud_manage_users = ttk.Treeview(self.manageusers_tabview.tab("Students"), columns=('number', 'lastname', 'firstname', 'email', 'password'), show="headings")
        self.stud_manage_users.place(x=10, y=60)

        self.stud_manage_users.heading('number', text="No.")
        self.stud_manage_users.heading('lastname', text="Last Name")
        self.stud_manage_users.heading('firstname', text="First Name")
        self.stud_manage_users.heading('email', text="Email")
        self.stud_manage_users.heading('password', text="Password")

        self.stud_manage_users.column('number', anchor="center")
        self.stud_manage_users.column('lastname', anchor="center")
        self.stud_manage_users.column('firstname', anchor="center")
        self.stud_manage_users.column('email', anchor="center")
        self.stud_manage_users.column('password', anchor="center")

        # Modern look for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=50, fieldbackground="#343638", bordercolor="#343638", borderwidth=0, font=(None, 14))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=(None, 14))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # Fetch student table from database then input to CSV
        queries.fetch_student_table()

        # Open CSV then display to table
        with open(r'csv/all_students.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                lastname = row['stud_LastName']
                firstname = row['stud_FirstName']
                email = row['stud_Email']
                password = row['stud_Password']
                self.stud_manage_users.insert("", "end", values=(count, lastname, firstname, email, password))
                count = count+1

        # TABLE FOR PROFESSOR MANAGE USERS
        self.prof_manage_users = ttk.Treeview(self.manageusers_tabview.tab("Professors"), columns=('number', 'lastname', 'firstname', 'email', 'password'), show="headings")
        self.prof_manage_users.place(x=10, y=60)

        self.prof_manage_users.heading('number', text="No.")
        self.prof_manage_users.heading('lastname', text="Last Name")
        self.prof_manage_users.heading('firstname', text="First Name")
        self.prof_manage_users.heading('email', text="Email")
        self.prof_manage_users.heading('password', text="Password")

        self.prof_manage_users.column('number', anchor="center")
        self.prof_manage_users.column('lastname', anchor="center")
        self.prof_manage_users.column('firstname', anchor="center")
        self.prof_manage_users.column('email', anchor="center")
        self.prof_manage_users.column('password', anchor="center")

        # Modern look for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=50, fieldbackground="#343638", bordercolor="#343638", borderwidth=0, font=(None, 14))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=(None, 14))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # Fetch student table from database then input to CSV
        queries.fetch_professor_table()

        # Open CSV then display to table
        with open(r'csv/all_professors.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                lastname = row['professor_LastName']
                firstname = row['professor_FirstName']
                email = row['professor_Email']
                password = row['professor_Password']
                self.prof_manage_users.insert("", "end", values=(count, lastname, firstname, email, password))
                count = count+1

        # TABLE FOR ADMIN MANAGE USERS
        self.admin_manage_users = ttk.Treeview(self.manageusers_tabview.tab("Admins"), columns=('number', 'lastname', 'firstname', 'email', 'password'), show="headings")
        self.admin_manage_users.place(x=10, y=60)

        self.admin_manage_users.heading('number', text="No.")
        self.admin_manage_users.heading('lastname', text="Last Name")
        self.admin_manage_users.heading('firstname', text="First Name")
        self.admin_manage_users.heading('email', text="Email")
        self.admin_manage_users.heading('password', text="Password")

        self.admin_manage_users.column('number', anchor="center")
        self.admin_manage_users.column('lastname', anchor="center")
        self.admin_manage_users.column('firstname', anchor="center")
        self.admin_manage_users.column('email', anchor="center")
        self.admin_manage_users.column('password', anchor="center")

        # Modern look for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=50, fieldbackground="#343638", bordercolor="#343638", borderwidth=0, font=(None, 14))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=(None, 14))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # Fetch student table from database then input to CSV
        queries.fetch_admin_table()

        # Open CSV then display to table
        with open(r'csv/all_admins.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                lastname = row['admin_LastName']
                firstname = row['admin_FirstName']
                email = row['admin_Email']
                password = row['admin_Password']
                self.admin_manage_users.insert("", "end", values=(count, lastname, firstname, email, password))
                count = count+1

    # Open CLASS LINK PANEL
    def stud_sidebar_classlink_clicked(self):
        # MAIN CLASS LINK PANEL
        self.main_frame_classlink_STUD = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_classlink_STUD.place(x=180, y=0)

        self.stud_classlink_tabview = tk.CTkTabview(self.main_frame_classlink_STUD, width=700, height=500)
        self.stud_classlink_tabview.place(x=110, y=30)
        self.stud_classlink_tabview.add("Microsoft Teams")
        self.stud_classlink_tabview.add("Zoom")
        self.stud_classlink_tabview.add("Google Meet")

        # ================ TABVIEW FOR MS TEAMS =================
        self.stud_teams_meetlength_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Microsoft Teams"), text="Meeting Length:")
        self.stud_teams_meetlength_label.place(x=100, y=40)

        self.stud_teams_meeting_hour = tk.CTkEntry(self.stud_classlink_tabview.tab("Microsoft Teams"), width=100, placeholder_text="Hours")
        self.stud_teams_meeting_hour.place(x=210, y=40)

        self.stud_teams_meeting_minutes = tk.CTkEntry(self.stud_classlink_tabview.tab("Microsoft Teams"), width=100, placeholder_text="Minutes")
        self.stud_teams_meeting_minutes.place(x=210, y=80)

        self.stud_teams_meetlink_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Microsoft Teams"), text="Paste meeting link below:")
        self.stud_teams_meetlink_label.place(x=100, y=120)

        self.stud_teams_link_textbox = tk.CTkTextbox(self.stud_classlink_tabview.tab("Microsoft Teams"), height=100, width=500)
        self.stud_teams_link_textbox.place(x=100, y=150)

        # Button to link to MS TEAMS
        self.stud_MSTEAMS_button = tk.CTkButton(self.stud_classlink_tabview.tab("Microsoft Teams"), text="Connect to Microsoft Teams", command=self.connect_to_teams)
        self.stud_MSTEAMS_button.place(x=100, y=270)

        self.stud_teams_detection_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Microsoft Teams"), text="Commands for detections: ")
        self.stud_teams_detection_label.place(x=100, y=350)

        self.stud_teams_detect_eyegaze = tk.CTkButton(self.stud_classlink_tabview.tab("Microsoft Teams"), text="Start Eye Gaze Detection", command=self.start_teams_eyegaze_detection)
        self.stud_teams_detect_eyegaze.place(x=270, y=330)

        self.stud_teams_detect_emotion = tk.CTkButton(self.stud_classlink_tabview.tab("Microsoft Teams"), text="Start Emotion Detection", command=self.start_teams_emotion_detection)
        self.stud_teams_detect_emotion.place(x=270, y=370)

        # ================ TABVIEW FOR ZOOM =================
        # self.meetlength_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Zoom"), text="Zoom link is under development...")
        # self.meetlength_label.place(x=100, y=40)

        self.stud_zoom_meetlength_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Zoom"), text="Meeting Length:")
        self.stud_zoom_meetlength_label.place(x=100, y=40)

        self.stud_zoom_meeting_hour = tk.CTkEntry(self.stud_classlink_tabview.tab("Zoom"), width=100, placeholder_text="Hours")
        self.stud_zoom_meeting_hour.place(x=210, y=40)

        self.stud_zoom_meeting_minutes = tk.CTkEntry(self.stud_classlink_tabview.tab("Zoom"), width=100, placeholder_text="Minutes")
        self.stud_zoom_meeting_minutes.place(x=210, y=80)

        self.stud_zoom_meetlink_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Zoom"), text="Paste meeting link below:")
        self.stud_zoom_meetlink_label.place(x=100, y=120)

        self.stud_zoom_link_textbox = tk.CTkTextbox(self.stud_classlink_tabview.tab("Zoom"), height=100, width=500)
        self.stud_zoom_link_textbox.place(x=100, y=150)

        # Button to link to ZOOM
        self.stud_ZOOM_button = tk.CTkButton(self.stud_classlink_tabview.tab("Zoom"), text="Connect to Zoom", command=self.connect_to_zoom)
        self.stud_ZOOM_button.place(x=100, y=270)

        self.stud_zoom_detection_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Zoom"), text="Commands for detections: ")
        self.stud_zoom_detection_label.place(x=100, y=350)

        self.stud_zoom_detect_eyegaze = tk.CTkButton(self.stud_classlink_tabview.tab("Zoom"), text="Start Eye Gaze Detection", command=self.start_zoom_eyegaze_detection)
        self.stud_zoom_detect_eyegaze.place(x=270, y=330)

        self.stud_zoom_detect_emotion = tk.CTkButton(self.stud_classlink_tabview.tab("Zoom"), text="Start Emotion Detection", command=self.start_zoom_emotion_detection)
        self.stud_zoom_detect_emotion.place(x=270, y=370)

        # ================ TABVIEW FOR GOOGLE MEET =================
        # self.meetlength_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Google Meet"), text="Google Meet link is under development...")
        # self.meetlength_label.place(x=100, y=40)

        self.stud_gmeet_meetlength_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Google Meet"), text="Meeting Length:")
        self.stud_gmeet_meetlength_label.place(x=100, y=40)

        self.stud_gmeet_meeting_hour = tk.CTkEntry(self.stud_classlink_tabview.tab("Google Meet"), width=100, placeholder_text="Hours")
        self.stud_gmeet_meeting_hour.place(x=210, y=40)

        self.stud_gmeet_meeting_minutes = tk.CTkEntry(self.stud_classlink_tabview.tab("Google Meet"), width=100, placeholder_text="Minutes")
        self.stud_gmeet_meeting_minutes.place(x=210, y=80)

        self.stud_gmeet_meetlink_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Google Meet"), text="Paste meeting link below:")
        self.stud_gmeet_meetlink_label.place(x=100, y=120)

        self.stud_gmeet_link_textbox = tk.CTkTextbox(self.stud_classlink_tabview.tab("Google Meet"), height=100, width=500)
        self.stud_gmeet_link_textbox.place(x=100, y=150)

        # Button to link to GMEET
        self.stud_GMEET_button = tk.CTkButton(self.stud_classlink_tabview.tab("Google Meet"), text="Connect to Google Meet", command=self.connect_to_gmeet)
        self.stud_GMEET_button.place(x=100, y=270)

        self.stud_gmeet_detection_label = tk.CTkLabel(self.stud_classlink_tabview.tab("Google Meet"), text="Commands for detections: ")
        self.stud_gmeet_detection_label.place(x=100, y=350)

        self.stud_gmeet_detect_eyegaze = tk.CTkButton(self.stud_classlink_tabview.tab("Google Meet"), text="Start Eye Gaze Detection", command=self.start_zoom_eyegaze_detection)
        self.stud_gmeet_detect_eyegaze.place(x=270, y=330)

        self.stud_gmeet_detect_emotion = tk.CTkButton(self.stud_classlink_tabview.tab("Google Meet"), text="Start Emotion Detection", command=self.start_zoom_emotion_detection)
        self.stud_gmeet_detect_emotion.place(x=270, y=370)

    # Functions to run program to detect eyegaze / emotion FOR MS TEAMS
    def start_teams_eyegaze_detection(self):
        email = self.username_entry.get()

        hour = int(self.stud_teams_meeting_hour.get())
        minutes = int(self.stud_teams_meeting_minutes.get())

        converted_hour = (hour * 60) * 60
        converted_minutes = minutes*60

        total_secs = converted_hour + converted_minutes

        # print(total_secs)

        final_eyegazecam_teams.eyegaze_cam(total_secs)
        time.sleep(1)
        queries.eyegaze_summary_report(email)
        queries.delete_previous_eyegaze_records()

    def start_teams_emotion_detection(self):
        email = self.username_entry.get()

        hour = int(self.stud_teams_meeting_hour.get())
        minutes = int(self.stud_teams_meeting_minutes.get())

        converted_hour = (hour * 60) * 60
        converted_minutes = minutes*60

        total_secs = converted_hour + converted_minutes

        print(converted_hour)
        print(converted_minutes)
        print(total_secs)

        final_emotioncam_teams.emotion_cam(total_secs)
        time.sleep(1)
        queries.emotion_summary_report(email)
        queries.delete_previous_emotion_records()

    # Functions to run program to detect eyegaze / emotion FOR ZOOM
    def start_zoom_eyegaze_detection(self):
        email = self.username_entry.get()

        hour = int(self.stud_zoom_meeting_hour.get())
        minutes = int(self.stud_zoom_meeting_minutes.get())

        converted_hour = (hour * 60) * 60
        converted_minutes = minutes*60

        total_secs = converted_hour + converted_minutes

        # print(total_secs)

        final_eyegazecam_teams.eyegaze_cam(total_secs)
        time.sleep(1)
        queries.eyegaze_summary_report(email)
        queries.delete_previous_eyegaze_records()

    def start_zoom_emotion_detection(self):
        email = self.username_entry.get()

        hour = int(self.stud_zoom_meeting_hour.get())
        minutes = int(self.stud_zoom_meeting_minutes.get())

        converted_hour = (hour * 60) * 60
        converted_minutes = minutes*60

        total_secs = converted_hour + converted_minutes

        # print(total_secs)

        final_emotioncam_teams.emotion_cam(total_secs)
        time.sleep(1)
        queries.emotion_summary_report(email)
        queries.delete_previous_emotion_records()

    # Functions to run program to detect eyegaze / emotion FOR GOOGLE MEET
    def start_gmeet_eyegaze_detection(self):
        email = self.username_entry.get()

        hour = int(self.stud_gmeet_meeting_hour.get())
        minutes = int(self.stud_gmeet_meeting_minutes.get())

        converted_hour = (hour * 60) * 60
        converted_minutes = minutes*60

        total_secs = converted_hour + converted_minutes

        # print(total_secs)

        final_eyegazecam_teams.eyegaze_cam(total_secs)
        time.sleep(1)
        queries.eyegaze_summary_report(email)
        queries.delete_previous_eyegaze_records()

    def start_gmeet_emotion_detection(self):
        email = self.username_entry.get()

        hour = int(self.stud_gmeet_meeting_hour.get())
        minutes = int(self.stud_gmeet_meeting_minutes.get())

        converted_hour = (hour * 60) * 60
        converted_minutes = minutes*60

        total_secs = converted_hour + converted_minutes

        # print(total_secs)

        final_emotioncam_teams.emotion_cam(total_secs)
        time.sleep(1)
        queries.emotion_summary_report(email)
        queries.delete_previous_emotion_records()

    # Open CLASS LINK PANEL
    def prof_sidebar_classlink_clicked(self):
        # MAIN CLASS LINK PANEL
        self.main_frame_classlink_PROF = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_classlink_PROF.place(x=180, y=0)

        self.prof_classlink_tabview = tk.CTkTabview(self.main_frame_classlink_PROF, width=700, height=500)
        self.prof_classlink_tabview.place(x=110, y=30)
        self.prof_classlink_tabview.add("Microsoft Teams")
        self.prof_classlink_tabview.add("Zoom")
        self.prof_classlink_tabview.add("Google Meet")

        # ================ TABVIEW FOR MS TEAMS =================
        # self.prof_teams_meetlength_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Microsoft Teams"), text="Meeting Length:")
        # self.prof_teams_meetlength_label.place(x=100, y=40)

        # self.prof_teams_meeting_hour = tk.CTkEntry(self.prof_classlink_tabview.tab("Microsoft Teams"), width=100, placeholder_text="Hours")
        # self.prof_teams_meeting_hour.place(x=210, y=40)

        # self.prof_teams_meeting_minutes = tk.CTkEntry(self.prof_classlink_tabview.tab("Microsoft Teams"), width=100, placeholder_text="Minutes")
        # self.prof_teams_meeting_minutes.place(x=210, y=80)

        self.prof_teams_meetlink_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Microsoft Teams"), text="Paste meeting link below:")
        self.prof_teams_meetlink_label.place(x=100, y=120)

        self.prof_teams_link_textbox = tk.CTkTextbox(self.prof_classlink_tabview.tab("Microsoft Teams"), height=100, width=500)
        self.prof_teams_link_textbox.place(x=100, y=150)

        # Button to link to MS TEAMS
        self.prof_MSTEAMS_button = tk.CTkButton(self.prof_classlink_tabview.tab("Microsoft Teams"), text="Connect to Microsoft Teams", command=self.connect_to_teams)
        self.prof_MSTEAMS_button.place(x=100, y=270)

        # ================ TABVIEW FOR ZOOM =================
        # self.meetlength_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Zoom"), text="Zoom link is under development...")
        # self.meetlength_label.place(x=100, y=40)

        # self.prof_zoom_meetlength_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Zoom"), text="Meeting Length:")
        # self.prof_zoom_meetlength_label.place(x=100, y=40)

        # self.prof_zoom_meeting_hour = tk.CTkEntry(self.prof_classlink_tabview.tab("Zoom"), width=100, placeholder_text="Hours")
        # self.prof_zoom_meeting_hour.place(x=210, y=40)

        # self.prof_zoom_meeting_minutes = tk.CTkEntry(self.prof_classlink_tabview.tab("Zoom"), width=100, placeholder_text="Minutes")
        # self.prof_zoom_meeting_minutes.place(x=210, y=80)

        self.prof_zoom_meetlink_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Zoom"), text="Paste meeting link below:")
        self.prof_zoom_meetlink_label.place(x=100, y=120)

        self.prof_zoom_link_textbox = tk.CTkTextbox(self.prof_classlink_tabview.tab("Zoom"), height=100, width=500)
        self.prof_zoom_link_textbox.place(x=100, y=150)

        # Button to link to ZOOM
        self.prof_ZOOM_button = tk.CTkButton(self.prof_classlink_tabview.tab("Zoom"), text="Connect to Zoom", command=self.connect_to_zoom)
        self.prof_ZOOM_button.place(x=100, y=270)

        # ================ TABVIEW FOR GOOGLE MEET =================
        # self.meetlength_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Google Meet"), text="Google Meet link is under development...")
        # self.meetlength_label.place(x=100, y=40)

        self.prof_gmeet_meetlink_label = tk.CTkLabel(self.prof_classlink_tabview.tab("Google Meet"), text="Paste meeting link below:")
        self.prof_gmeet_meetlink_label.place(x=100, y=120)

        self.prof_gmeet_link_textbox = tk.CTkTextbox(self.prof_classlink_tabview.tab("Google Meet"), height=100, width=500)
        self.prof_gmeet_link_textbox.place(x=100, y=150)

        # Button to link to GMEET
        self.prof_GMEET_button = tk.CTkButton(self.prof_classlink_tabview.tab("Google Meet"), text="Connect to Google Meet", command=self.connect_to_gmeet)
        self.prof_GMEET_button.place(x=100, y=270)

    # Connection to MS TEAMS
    def connect_to_teams(self):
        teams_URL = "https://teams.microsoft.com"
        meet_URL = self.stud_teams_link_textbox.get(0.1, tk.END)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # options.add_experimental_option("prefs", { "profile.default_content_setting_values.geolocation": 2})

        service = Service(executable_path=r"chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(teams_URL)

        time.sleep(4)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        username_field = driver.find_element(By.ID, "i0116")
        username = self.username_entry.get()
        print(username)
        username_field.send_keys(username)

        time.sleep(1)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        next_button = driver.find_element(By.ID, "idSIButton9")
        next_button.click()

        time.sleep(3)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        password_field = driver.find_element(By.ID, "i0118")
        password_field.send_keys(self.password_entry.get())

        signin_button = driver.find_element(By.ID, "idSIButton9")
        signin_button.click()

        time.sleep(1)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        not_stay_logged = driver.find_element(By.ID, "idBtn_Back")
        not_stay_logged.click()

        time.sleep(10)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        driver.get(meet_URL)

    # Connection to ZOOM
    def connect_to_zoom(self):
        zoom_URL = "https://zoom.us/signin#/login"
        meet_URL = self.stud_zoom_link_textbox.get(0.1, tk.END)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # options.add_experimental_option("prefs", { "profile.default_content_setting_values.geolocation": 2})

        service = Service(executable_path=r"chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(zoom_URL)

        time.sleep(10)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        driver.get(meet_URL)

    # Connection to GMEET
    def connect_to_gmeet(self):
        gmeet_URL = "https://meet.google.com/"
        meet_URL = self.stud_gmeet_link_textbox.get(0.1, tk.END)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # options.add_experimental_option("prefs", { "profile.default_content_setting_values.geolocation": 2})

        service = Service(executable_path=r"chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(gmeet_URL)

        time.sleep(10)
        # WebDriverWait(driver, 10).until(EC.alert_is_present())

        driver.get(meet_URL)
    
    # Open STUDENT SUMMARY REPORT PANEL
    def stud_sidebar_report_clicked(self):
        # MAIN SUMMARY REPORT PANEL
        self.main_frame_report_STUD = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_report_STUD.place(x=180, y=0)

        self.print_button = tk.CTkButton(self.main_frame_report_STUD, text="Print Eyegaze Report", command=self.stud_download_eyegaze)
        self.print_button.place(x=50, y=400)

        self.eyegaze_table_frame = tk.CTkFrame(self.main_frame_report_STUD, width=600, height=350)
        self.eyegaze_table_frame.place(x=180, y=100)

        self.eyegaze_table = ttk.Treeview(self.eyegaze_table_frame, columns=('number', 'eyegaze', 'date', 'time'), show="headings")
        # self.eyegaze_table.place(x=280, y=150)
        self.eyegaze_table.place(x=0, y=0)

        self.eyegaze_table.heading('number', text="No.")
        self.eyegaze_table.heading('eyegaze', text="Level of Engagement")
        self.eyegaze_table.heading('date', text="Date Captured")
        self.eyegaze_table.heading('time', text="Time Captured")

        self.eyegaze_table.column('number', anchor="center")
        self.eyegaze_table.column('eyegaze', anchor="center")
        self.eyegaze_table.column('date', anchor="center")
        self.eyegaze_table.column('time', anchor="center")

        # Modern look for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=50, fieldbackground="white", bordercolor="#343638", borderwidth=0, font=(None, 14))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=(None, 14))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # CSV Data holder from database
        queries.fetch_student_eyegaze_table()

        # Open Eye Gaze CSV records then display to table
        with open(r'csv/student_eyegaze_tbl.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            current_email = self.username_entry.get()
            for row in reader:
                email_check = row['stud_Email']
                if current_email == email_check:
                    eyegaze_name = row['eyegaze_name']
                    date_captured = row['eyegaze_date_captured']
                    time_captured = row['eyegaze_time_captured']
                    self.eyegaze_table.insert("", "end", values=(count, eyegaze_name, date_captured, time_captured))
                    count = count+1

    # Function to print eyegaze table from student view
    def print_stud_eyegaze(self):
        df = pd.read_csv(r'csv/student_eyegaze_tbl.csv')
        # # print(df)

        fig, ax = plt.subplots(figsize=(12,4))

        # # hide axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')

        stud_eyegaze_table = ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns, loc='center')

        pp = PdfPages(r"pdfs")

    # Open PROFESSOR SUMMARY REPORT PANEL
    def prof_sidebar_report_clicked(self):
        # MAIN SUMMARY REPORT PANEL
        self.main_frame_report_PROF = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_report_PROF.place(x=180, y=0)

        self.print_button = tk.CTkButton(self.main_frame_report_PROF, text="Print Eyegaze Report", command=self.download_eyegaze)
        self.print_button.place(x=50, y=400)

        self.print_button = tk.CTkButton(self.main_frame_report_PROF, text="Print Emotion Report", command=self.download_emotions)
        self.print_button.place(x=200, y=400)

        self.print_button = tk.CTkButton(self.main_frame_report_PROF, text="Delete Eyegaze Report", command=self.delete_eyegaze_tbl)
        self.print_button.place(x=400, y=400)

        self.print_button = tk.CTkButton(self.main_frame_report_PROF, text="Delete Emotion Report", command=self.delete_emotions_tbl)
        self.print_button.place(x=750, y=400)


        self.report_tabview = tk.CTkTabview(self.main_frame_report_PROF, width=800, height=350)
        self.report_tabview.place(x=110, y=30)
        self.report_tabview.add("Eye Gaze Report")
        self.report_tabview.add("Emotion Report")
        self.sort_order = 'asc'
        # PROFESSOR EMOTION TABLE

        self.emotion_table = ttk.Treeview(self.report_tabview.tab("Emotion Report"), columns=('number', 'emotion', 'date', 'time', 'studname'), show="headings")
        self.emotion_table.place(x=10, y=60)

        self.emotion_table.heading('number', text="No.")
        self.emotion_table.heading('emotion', text="Emotion")
        self.emotion_table.heading('date', text="Date Captured",command=self.sort_emotion_time)
        self.emotion_table.heading('time', text="Time Captured",command=self.sort_emotion_time)
        self.emotion_table.heading('studname', text="Student Name",command=self.sort_emotion_name)

        self.emotion_table.column('number', width=50, anchor="center")
        self.emotion_table.column('emotion', width=150, anchor="center")
        self.emotion_table.column('date', width=150, anchor="center")
        self.emotion_table.column('time', width=150, anchor="center")
        self.emotion_table.column('studname', width=200, anchor="center")  # Adjust the width as needed


        # PROFESSOR EYE GAZE TABLE
        
        self.eyegaze_table = ttk.Treeview(self.report_tabview.tab("Eye Gaze Report"), columns=('number', 'eyegaze', 'date', 'time', 'studname'), show="headings")
        self.eyegaze_table.place(x=0, y=60)

        self.eyegaze_table.heading('number', text="No.")
        self.eyegaze_table.heading('eyegaze', text="Level of Engagement")
        self.eyegaze_table.heading('date', text="Date Captured",command=self.sort_eyegaze_time)
        self.eyegaze_table.heading('time', text="Time Captured", command=self.sort_eyegaze_time)
        self.eyegaze_table.heading('studname', text="Student Name", command=self.sort_eyegaze_name)

        self.eyegaze_table.column('number', width=50, anchor="center")
        self.eyegaze_table.column('eyegaze', width=150, anchor="center")
        self.eyegaze_table.column('date', width=150, anchor="center")
        self.eyegaze_table.column('time', width=150, anchor="center")
        self.eyegaze_table.column('studname', width=200, anchor="center")  # Adjust the width as needed


        # Modern look for table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=50, fieldbackground="#343638", bordercolor="#343638", borderwidth=0, font=(None, 14))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=(None, 14))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.show_eyegaze_table()
        self.show_emotion_table()

    def sort_eyegaze_time(self):
        data = []

        for item in self.eyegaze_table.get_children(''):
            time_value = self.eyegaze_table.item(item, 'values')[2]

            # Check if the time_value contains time information
            if ' ' in time_value:
                format_string = "%Y-%m-%d %H:%M:%S"
            else:
                format_string = "%Y-%m-%d"

            data.append((datetime.strptime(time_value, format_string), item))

        if self.sort_order == 'asc':
            data.sort(key=lambda x: x[0])
            self.sort_order = 'desc'
        else:
            data.sort(key=lambda x: x[0], reverse=True)
            self.sort_order = 'asc'

        for index, (_, item) in enumerate(data, start=1):
            self.eyegaze_table.move(item, '', index)

        # Update the table view
        self.eyegaze_table.update()
    
    def sort_emotion_time(self):
        data = []

        for item in self.emotion_table.get_children(''):
            time_value = self.emotion_table.item(item, 'values')[2]

            # Check if the time_value contains time information
            if ' ' in time_value:
                format_string = "%Y-%m-%d %H:%M:%S"
            else:
                format_string = "%Y-%m-%d"

            data.append((datetime.strptime(time_value, format_string), item))

        if self.sort_order == 'asc':
            data.sort(key=lambda x: x[0])
            self.sort_order = 'desc'
        else:
            data.sort(key=lambda x: x[0], reverse=True)
            self.sort_order = 'asc'

        for index, (_, item) in enumerate(data, start=1):
            self.emotion_table.move(item, '', index)

        # Update the table view
        self.emotion_table.update()
    
    def sort_eyegaze_name(self):
        data = []

        for item in self.eyegaze_table.get_children(''):
            studname_value = self.eyegaze_table.item(item, 'values')[4]
            data.append((studname_value, item))

        if self.sort_order == 'asc':
            data.sort(key=lambda x: x[0])
            self.sort_order = 'desc'
        else:
            data.sort(key=lambda x: x[0], reverse=True)
            self.sort_order = 'asc'

        for index, (_, item) in enumerate(data, start=1):
            self.eyegaze_table.move(item, '', index)

        # Update the table view
        self.eyegaze_table.update()

    def sort_emotion_name(self):
        data = []

        for item in self.emotion_table.get_children(''):
            studname_value = self.emotion_table.item(item, 'values')[4]
            data.append((studname_value, item))

        if self.sort_order == 'asc':
            data.sort(key=lambda x: x[0])
            self.sort_order = 'desc'
        else:
            data.sort(key=lambda x: x[0], reverse=True)
            self.sort_order = 'asc'

        for index, (_, item) in enumerate(data, start=1):
            self.emotion_table.move(item, '', index)

        # Update the table view
        self.emotion_table.update()

    def delete_eyegaze_tbl(self):
        queries.truncate_eyegaze()
        
        self.incorrect_login_frame = tk.CTkFrame(self, width=390, height=150)
        self.incorrect_login_frame.place(x=360, y=200)

        # Confirmation Label
        self.success_signup_label = tk.CTkLabel(self.incorrect_login_frame, text="Eyegaze Report is now Cleared")
        self.success_signup_label.place(x=120, y=30)
        
        self.back_to_login_button = tk.CTkButton(self.incorrect_login_frame, text="OK", width=100, command=self.prof_sidebar_report_clicked)
        self.back_to_login_button.place(x=140, y=70)


    def delete_emotions_tbl(self):
        queries.truncate_emotions()

        self.incorrect_login_frame = tk.CTkFrame(self, width=390, height=150)
        self.incorrect_login_frame.place(x=360, y=200)

        # Confirmation Label
        self.success_signup_label = tk.CTkLabel(self.incorrect_login_frame, text="Emotions Report is now Cleared")
        self.success_signup_label.place(x=120, y=30)
        
        self.back_to_login_button = tk.CTkButton(self.incorrect_login_frame, text="OK", width=100, command=self.prof_sidebar_report_clicked)
        self.back_to_login_button.place(x=140, y=70)


    # DISPLAY EMOTION RECORDS TO TABLE
    def show_emotion_table(self):
        # CSV Data holder from database
        queries.emotion_db_to_csv()

        # Open Emotion CSV records then display to table
        with open(r'csv/emotion_db_to_csv.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                emotion_name = row['emotion_name']
                date_captured = row['emotion_date_captured']
                time_captured = row['emotion_time_captured']
                stud_fullname = row['student_FullName']
                self.emotion_table.insert("", "end", values=(count, emotion_name, date_captured, time_captured, stud_fullname))
                count = count+1

    # DISPLAY EYEGAZE RECORDS TO TABLE
    def show_eyegaze_table(self):
        # CSV Data holder from database
        queries.eyegaze_db_to_csv()
    
        # Open Eye Gaze CSV records then display to table
        with open(r'csv/eyegaze_db_to_csv.csv') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            count = 1
            for row in reader:
                eyegaze_name = row['eyegaze_name']
                date_captured = row['eyegaze_date_captured']
                time_captured = row['eyegaze_time_captured']
                stud_fullname = row['student_FullName']
                self.eyegaze_table.insert("", "end", values=(count, eyegaze_name, date_captured, time_captured, stud_fullname))
                count = count+1

    def download_eyegaze(self):
        # Ask user for the file path to save the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            # Open Eye Gaze CSV records then save to the chosen file path
            with open(r'csv/eyegaze_db_to_csv.csv') as csv_file:
                # Read the content of the CSV file
                csv_content = csv_file.read()

            # Save the content to the chosen file path
            with open(file_path, 'w') as save_file:
                save_file.write(csv_content)

    def download_emotions(self):
        # Ask user for the file path to save the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            # Open Eye Gaze CSV records then save to the chosen file path
            with open(r'csv/emotion_db_to_csv.csv') as csv_file:
                # Read the content of the CSV file
                csv_content = csv_file.read()

            # Save the content to the chosen file path
            with open(file_path, 'w') as save_file:
                save_file.write(csv_content)

    def stud_download_eyegaze(self):
        # Ask user for the file path to save the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            # Open Eye Gaze CSV records then save to the chosen file path
            with open(r'csv/student_eyegaze_tbl.csv') as csv_file:
                # Read the content of the CSV file
                csv_content = csv_file.read()

            # Save the content to the chosen file path
            with open(file_path, 'w') as save_file:
                save_file.write(csv_content)
    


    # Open STUDENT SETTINGS PANEL
    def stud_sidebar_settings_clicked(self):
        # MAIN SETTINGS PANEL
        self.main_frame_settings_STUD = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_settings_STUD.place(x=180, y=0)

        self.settings_tabview = tk.CTkTabview(self.main_frame_settings_STUD, width=700, height=500)
        self.settings_tabview.place(x=110, y=30)
        self.settings_tabview.add("Profile")
        self.settings_tabview.add("Account")
        self.settings_tabview.add("Camera")

        # Column Configuration
        self.settings_tabview.tab("Profile").grid_columnconfigure(0, weight=1)
        self.settings_tabview.tab("Account").grid_columnconfigure(0, weight=1)

        # =================== PROFILE TAB ========================
        #Profile Tab Information
        # First Name
        self.stud_first_name_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="First Name:")
        self.stud_first_name_label.place(x=120, y=30)

        self.stud_first_name_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.stud_first_name_txtfield.place(x=200, y=30)

        # Last Name
        self.stud_last_name_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Last Name:")
        self.stud_last_name_label.place(x=120, y=70)

        self.stud_last_name_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.stud_last_name_txtfield.place(x=200, y=70)

        # User Type
        self.occupation_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Occupation:")
        self.occupation_label.place(x=120, y=110)

        self.occupation_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.occupation_txtfield.place(x=200, y=110)

        # Transferring occupation to textfield
        occupation = self.occupation_name.cget("text")
        self.occupation_txtfield.delete(0, 'end')
        self.occupation_txtfield.insert(0, occupation)
        self.occupation_txtfield.configure(state="disabled")

        # Year Level
        self.stud_year_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Year:")
        self.stud_year_label.place(x=160, y=150)

        self.stud_year = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=110, placeholder_text="Year Level")
        self.stud_year.place(x=200, y=150)

        # Course
        self.stud_course_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Program:")
        self.stud_course_label.place(x=330, y=150)

        self.stud_course = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=110, placeholder_text="Program")
        self.stud_course.place(x=390, y=150)

        # Contact no:
        self.stud_number_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Contact no.:")
        self.stud_number_label.place(x=120, y=190)

        self.stud_contact_number = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300, placeholder_text="Contact Number")
        self.stud_contact_number.place(x=200, y=190)

        # Biography
        self.stud_bio_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Biography:")
        self.stud_bio_label.place(x=130, y=230)

        self.stud_bio_textbox = tk.CTkTextbox(self.settings_tabview.tab("Profile"), height=150, width=300)
        self.stud_bio_textbox.place(x=200, y=230)

        # Edit Button
        self.edit_button_ = tk.CTkButton(self.settings_tabview.tab("Profile"), text="Edit", command=self.edit_stud_profile_settings)
        self.edit_button_.place(x=360, y=400)

        # =================== ACCOUNT TAB ========================
        self.email_label = tk.CTkLabel(self.settings_tabview.tab("Account"), text="Email:")
        self.email_label.place(x=80, y=30)

        self.email_txtfield = tk.CTkEntry(self.settings_tabview.tab("Account"), width=200)
        self.email_txtfield.place(x=160, y=30)
        
        # Transferring input email here...
        email = self.username_entry.get()
        self.email_txtfield.delete(0, 'end')
        self.email_txtfield.insert(0, email)
        self.email_txtfield.configure(state="disabled")

        # Password Textfield...
        self.passW_label = tk.CTkLabel(self.settings_tabview.tab("Account"), text="Password:")
        self.passW_label.place(x=80, y=80)

        self.passW_txtfield = tk.CTkEntry(self.settings_tabview.tab("Account"), width=200)
        self.passW_txtfield.place(x=160, y=80)
        
        # Transferring input password here...
        passW = self.password_entry.get()
        self.passW_txtfield.delete(0, 'end')
        self.passW_txtfield.insert(0, passW)
        self.passW_txtfield.configure(state="disabled",show="*")

        # Edit Button...
        self.edit_button_ = tk.CTkButton(self.settings_tabview.tab("Account"), text="Edit", command=self.edit_stud_account_settings)
        self.edit_button_.place(x=360, y=400)
        
        # =================== CAMERA TAB ========================
        # Button for Emotion
        self.emotioncam_switch = tk.CTkSwitch(self.settings_tabview.tab("Camera"), text="Emotion Detection")
        self.emotioncam_switch.place(x=100, y=5)

        # Button for Eye Gaze
        self.eyegazecam_switch = tk.CTkSwitch(self.settings_tabview.tab("Camera"), text="Eye Gaze Detection")
        self.eyegazecam_switch.place(x=400, y=5)

        # Camera Display box
        self.camera_frame = tk.CTkFrame(self.settings_tabview.tab("Camera"))
        self.camera_frame.place(x=80, y=40)

        # Start Camera Button
        self.start_camera_button = tk.CTkButton(self.camera_frame, text="Start Camera", command=self.start_camera, width=15)
        self.start_camera_button.grid(row=0, column=0, padx=10, pady=10)

        # Stop Camera Button
        self.stop_camera_button = tk.CTkButton(self.camera_frame, text="Stop Camera", command=self.stop_camera, width=15, state="disabled")
        self.stop_camera_button.grid(row=0, column=1, padx=10, pady=10)

        # OpenCV camera
        self.cap = None
        self.camera_running = False

        queries.fetch_student_table()

        with open(r"csv/all_students.csv") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            current_email = self.username_entry.get()
            for row in reader:
                email_check = row['stud_Email']
                if current_email == email_check:
                    firstname = row['stud_FirstName']
                    lastname = row['stud_LastName']
                    yearlevel = row['stud_YearLevel']
                    program = row['stud_Course']
                    contactnum = row['stud_ContactNo']
                    bio = row['stud_Bio']

                    self.stud_first_name_txtfield.delete(0, 'end')
                    self.stud_first_name_txtfield.insert(0, firstname)
                    self.stud_first_name_txtfield.configure(state="disabled")

                    self.stud_last_name_txtfield.delete(0, 'end')
                    self.stud_last_name_txtfield.insert(0, lastname)
                    self.stud_last_name_txtfield.configure(state="disabled")

                    self.stud_year.delete(0, 'end')
                    self.stud_year.insert(0, yearlevel)
                    self.stud_year.configure(state="disabled")

                    self.stud_course.delete(0, 'end')
                    self.stud_course.insert(0, program)
                    self.stud_course.configure(state="disabled")

                    self.stud_contact_number.delete(0, 'end')
                    self.stud_contact_number.insert(0, contactnum)
                    self.stud_contact_number.configure(state="disabled")

                    self.stud_bio_textbox.insert("1.0", bio)
                    self.stud_bio_textbox.configure(state="disabled")

    def start_camera(self):
        if not self.camera_running:
            self.cap = cv2.VideoCapture(0)  # 0 represents the default camera
            self.camera_running = True
            self.start_camera_button.configure(state="disabled")
            self.stop_camera_button.configure(state="normal")

            # Create a label for displaying the camera feed
            self.camera_label = tk.CTkLabel(self.camera_frame, text="", image=None)
            self.camera_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

            # Start a separate thread to continuously update the camera feed
            camera_thread = threading.Thread(target=self.update_camera_feed)
            camera_thread.start()

    def stop_camera(self):
        if self.camera_running:
            self.cap.release()
            self.camera_running = False
            self.start_camera_button.configure(state="normal")
            self.stop_camera_button.configure(state="disabled")

            # Destroy the camera label to remove the last frame
            self.camera_label.destroy()

    def update_camera_feed(self):
        while self.camera_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resized_frame = self.resize_image(frame, width=500, height=400)  # Adjust the size as needed
                photo = ImageTk.PhotoImage(image=PIL.Image.fromarray(resized_frame))
                self.camera_label.configure(image=photo)
                self.camera_label.photo = photo
                self.camera_frame.update_idletasks()  # Force an update
            else:
                break

    def resize_image(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        # Resize the image while maintaining its aspect ratio
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image

        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        resized = cv2.resize(image, dim, interpolation=inter)
        return resized

    def display_camera_frame(self, photo):
        camera_label = tk.CTkLabel(self.camera_frame, text = "" ,image=photo)
        camera_label.photo = photo
        camera_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # Edit student profile contents
    def edit_stud_profile_settings(self):
        self.stud_edit_fields_frame = tk.CTkFrame(self.settings_tabview.tab("Profile"), width=300, height=350)
        self.stud_edit_fields_frame.place(x=150, y=0)

        self.update_stud_firstname = tk.CTkEntry(self.stud_edit_fields_frame, width=200, placeholder_text="First Name")
        self.update_stud_firstname.place(x=50, y=40)

        self.update_stud_lastname = tk.CTkEntry(self.stud_edit_fields_frame, width=200, placeholder_text="Last Name")
        self.update_stud_lastname.place(x=50, y=80)

        self.update_stud_yearlevel = tk.CTkEntry(self.stud_edit_fields_frame, width=200, placeholder_text="Year Level")
        self.update_stud_yearlevel.place(x=50, y=120)

        self.update_stud_course = tk.CTkEntry(self.stud_edit_fields_frame, width=200, placeholder_text="Course")
        self.update_stud_course.place(x=50, y=160)

        self.update_stud_contactno = tk.CTkEntry(self.stud_edit_fields_frame, width=200, placeholder_text="Contact no.")
        self.update_stud_contactno.place(x=50, y=200)

        self.update_stud_bio = tk.CTkEntry(self.stud_edit_fields_frame, width=200, placeholder_text="Bio")
        self.update_stud_bio.place(x=50, y=240)

        # Save Button
        self.save_button_ = tk.CTkButton(self.stud_edit_fields_frame, text="Save", command=self.stud_profile_save_clicked)
        self.save_button_.place(x=80, y=300)

    def edit_stud_account_settings(self):
        self.stud_edit_fields_acctframe = tk.CTkFrame(self.settings_tabview.tab("Account"), width=300, height=350)
        self.stud_edit_fields_acctframe.place(x=150, y=0)

        self.update_stud_password = tk.CTkEntry(self.stud_edit_fields_acctframe, width=200, show="*", placeholder_text="Enter new password")
        self.update_stud_password.place(x=50, y=40)

        self.confirm_password = tk.CTkEntry(self.stud_edit_fields_acctframe, width=200, show="*", placeholder_text="Confirm password")
        self.confirm_password.place(x=50, y=80)

        # Save Button...
        self.acct_save_button_ = tk.CTkButton(self.stud_edit_fields_acctframe, text="Save", command=self.stud_acct_save_clicked)
        self.acct_save_button_.place(x=80, y=300)

    # SAVING CHANGES FUNCTION
    def close_save_changes(self):
        self.save_changes_frame.place_forget()

    # Saving..
    def stud_profile_save_clicked(self):
        # Confirmation Panel
        self.save_changes_frame = tk.CTkFrame(self, width=300, height=150)
        self.save_changes_frame.place(x=450, y=200)

        # Confirmation for Changes in Saving Label
        self.save_changes_label = tk.CTkLabel(self.save_changes_frame, text="Are you sure you want to save changes?")
        self.save_changes_label.place(x=40, y=30)

        # Buttons for Saving
        self.yes_button = tk.CTkButton(self.save_changes_frame, text="Yes", command=self.stud_profile_saved_clicked, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.save_changes_frame, text="No", command=self.close_save_changes, width=100)
        self.no_button.place(x=170, y=90)

    # Saved Function
    def stud_profile_close_saved_info_and_save_changes(self):
        self.saved_info_frame.place_forget()
        self.save_changes_frame.place_forget()
        self.stud_edit_fields_frame.place_forget()

    # Saved
    def stud_profile_saved_clicked(self):
        fname = self.update_stud_firstname.get()
        lname = self.update_stud_lastname.get()
        year = self.update_stud_yearlevel.get()
        prog = self.update_stud_course.get()
        contactnum = self.update_stud_contactno.get()
        bio = self.update_stud_bio.get()
        email = self.username_entry.get()

        checker = queries.update_stud_info(lname, fname, year, prog, contactnum, bio, email)

        if checker == True:
            self.saved_info_frame = tk.CTkFrame(self, width=300, height=150)
            self.saved_info_frame.place(x=450, y=200)

            # Already saved
            self.saved_label = tk.CTkLabel(self.saved_info_frame, text="Saved!")
            self.saved_label.place(x=130, y=30)

            # Buttons for Saved information
            self.ok_button = tk.CTkButton(self.saved_info_frame, text="Ok", command=self.stud_profile_close_saved_info_and_save_changes, width=100)
            self.ok_button.place(x=100, y=90)
        else:
            self.error_saving_frame = tk.CTkFrame(self, width=300, height=150)
            self.error_saving_frame.place(x=450, y=200)

            # Already saved
            self.error_label = tk.CTkLabel(self.error_saving_frame, text="Error updating your info!")
            self.error_label.place(x=130, y=30)

            # Buttons for Saved information
            self.ok_button = tk.CTkButton(self.error_saving_frame, text="Ok", command=self.close_stud_profile_update_errormsg, width=100)
            self.ok_button.place(x=100, y=90)

    def close_stud_profile_update_errormsg(self):
        self.error_saving_frame.place_forget()

    # Saving..
    def stud_acct_save_clicked(self):
        # Confirmation Panel
        self.save_changes_frame = tk.CTkFrame(self, width=300, height=150)
        self.save_changes_frame.place(x=450, y=200)

        # Confirmation for Changes in Saving Label
        self.save_changes_label = tk.CTkLabel(self.save_changes_frame, text="Are you sure you want to save changes?")
        self.save_changes_label.place(x=40, y=30)

        # Buttons for Saving
        self.yes_button = tk.CTkButton(self.save_changes_frame, text="Yes", command=self.stud_acct_saved_clicked, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.save_changes_frame, text="No", command=self.close_save_changes, width=100)
        self.no_button.place(x=170, y=90)

    # Saved Function
    def stud_acct_close_saved_info_and_save_changes(self):
        self.saved_info_frame.place_forget()
        self.save_changes_frame.place_forget()
        self.stud_edit_fields_acctframe.place_forget()

    # Saved
    def stud_acct_saved_clicked(self):
        email = self.username_entry.get()
        password = self.update_stud_password.get()
        confirm_pass = self.confirm_password.get()

        # HASH PASSWORD
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Add the salt to the password and hash it
        hash_object.update(password.encode())
        # Get the hex digest of the hash
        hash_password = hash_object.hexdigest()
        print(hash_password)

        # HASH CONFIRM PASSWORD
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Add the salt to the password and hash it
        hash_object.update(confirm_pass.encode())
        # Get the hex digest of the hash
        hash_confirm_password = hash_object.hexdigest()
        print(hash_confirm_password)

        if hash_password != hash_confirm_password:
            self.notsamepass_frame = tk.CTkFrame(self, width=300, height=150)
            self.notsamepass_frame.place(x=450, y=200)

            # Already saved
            self.notsame_label = tk.CTkLabel(self.notsamepass_frame, text="Password not identical!")
            self.notsame_label.place(x=130, y=30)

            # Buttons for Saved information
            self.ok_button = tk.CTkButton(self.notsamepass_frame, text="Ok", command=self.close_password_check, width=100)
            self.ok_button.place(x=100, y=90)
        else:
            checker = queries.update_stud_password(hash_password, email)

            if checker == True:
                self.saved_info_frame = tk.CTkFrame(self, width=300, height=150)
                self.saved_info_frame.place(x=450, y=200)

                # Already saved
                self.saved_label = tk.CTkLabel(self.saved_info_frame, text="Saved!")
                self.saved_label.place(x=130, y=30)

                # Buttons for Saved information
                self.ok_button = tk.CTkButton(self.saved_info_frame, text="Ok", command=self.stud_acct_close_saved_info_and_save_changes, width=100)
                self.ok_button.place(x=100, y=90)
            else:
                self.error_saving_frame = tk.CTkFrame(self, width=300, height=150)
                self.error_saving_frame.place(x=450, y=200)

                # Already saved
                self.error_label = tk.CTkLabel(self.error_saving_frame, text="Error updating your info!")
                self.error_label.place(x=130, y=30)

                # Buttons for Saved information
                self.ok_button = tk.CTkButton(self.error_saving_frame, text="Ok", command=self.close_stud_account_update_errormsg, width=100)
                self.ok_button.place(x=100, y=90)

    def close_password_check(self):
        self.notsamepass_frame.place_forget()
        self.save_changes_frame.place_forget()

    def close_stud_account_update_errormsg(self):
        self.error_saving_frame.place_forget()

    # ================================== PROFESSOR SETTINGS ==================================
    # Open PROFESSOR SETTINGS PANEL
    def prof_sidebar_settings_clicked(self):
        # MAIN SETTINGS PANEL
        self.main_frame_settings_PROF = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_settings_PROF.place(x=180, y=0)

        self.settings_tabview = tk.CTkTabview(self.main_frame_settings_PROF, width=700, height=500)
        self.settings_tabview.place(x=110, y=30)
        self.settings_tabview.add("Profile")
        self.settings_tabview.add("Account")

        # Column Configuration
        self.settings_tabview.tab("Profile").grid_columnconfigure(0, weight=1)
        self.settings_tabview.tab("Account").grid_columnconfigure(0, weight=1)

        # =================== PROFILE TAB ========================
        #Profile Tab Information
        # First Name
        self.prof_first_name_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="First Name:")
        self.prof_first_name_label.place(x=120, y=30)

        self.prof_first_name_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.prof_first_name_txtfield.place(x=200, y=30)

        # Last Name
        self.prof_last_name_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Last Name:")
        self.prof_last_name_label.place(x=120, y=70)

        self.prof_last_name_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.prof_last_name_txtfield.place(x=200, y=70)

        self.occupation_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Occupation:")
        self.occupation_label.place(x=120, y=110)

        self.occupation_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.occupation_txtfield.place(x=200, y=110)

        # Transferring occupation to textfield
        occupation = self.occupation_name.cget("text")
        self.occupation_txtfield.delete(0, 'end')
        self.occupation_txtfield.insert(0, occupation)
        self.occupation_txtfield.configure(state="disabled")

        # Contact no:
        self.prof_number_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Contact no.:")
        self.prof_number_label.place(x=120, y=150)

        self.prof_contact_number = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300, placeholder_text="Contact Number")
        self.prof_contact_number.place(x=200, y=150)

        # Biography
        self.prof_bio_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Description:")
        self.prof_bio_label.place(x=120, y=190)

        self.prof_bio_textbox = tk.CTkTextbox(self.settings_tabview.tab("Profile"), height=150, width=300)
        self.prof_bio_textbox.place(x=200, y=190)

        # Edit Button
        self.edit_button_ = tk.CTkButton(self.settings_tabview.tab("Profile"), text="Edit", command=self.edit_prof_profile_settings)
        self.edit_button_.place(x=360, y=400)

        # =================== ACCOUNT TAB ========================
        self.email_label = tk.CTkLabel(self.settings_tabview.tab("Account"), text="Email:")
        self.email_label.place(x=80, y=30)

        self.email_txtfield = tk.CTkEntry(self.settings_tabview.tab("Account"), width=200)
        self.email_txtfield.place(x=160, y=30)
        
        # Transferring input email here...
        email = self.username_entry.get()
        self.email_txtfield.delete(0, 'end')
        self.email_txtfield.insert(0, email)
        self.email_txtfield.configure(state="disabled")

        # Password Textfield...
        self.passW_label = tk.CTkLabel(self.settings_tabview.tab("Account"), text="Password:")
        self.passW_label.place(x=80, y=80)

        self.passW_txtfield = tk.CTkEntry(self.settings_tabview.tab("Account"), width=200)
        self.passW_txtfield.place(x=160, y=80)
        
        # Transferring input password here...
        passW = self.password_entry.get()
        self.passW_txtfield.delete(0, 'end')
        self.passW_txtfield.insert(0, passW)
        self.passW_txtfield.configure(state="disabled",show="*")

        # Edit Button...
        self.edit_button_ = tk.CTkButton(self.settings_tabview.tab("Account"), text="Edit", command=self.edit_prof_account_settings)
        self.edit_button_.place(x=360, y=400)

        queries.fetch_professor_table()

        with open(r"csv/all_professors.csv") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            current_email = self.username_entry.get()
            for row in reader:
                email_check = row['professor_Email']
                if current_email == email_check:
                    firstname = row['professor_FirstName']
                    lastname = row['professor_LastName']
                    contactnum = row['professor_ContactNo']
                    desc = row['professor_desc']

                    self.prof_first_name_txtfield.delete(0, 'end')
                    self.prof_first_name_txtfield.insert(0, firstname)
                    self.prof_first_name_txtfield.configure(state="disabled")

                    self.prof_last_name_txtfield.delete(0, 'end')
                    self.prof_last_name_txtfield.insert(0, lastname)
                    self.prof_last_name_txtfield.configure(state="disabled")

                    self.prof_contact_number.delete(0, 'end')
                    self.prof_contact_number.insert(0, contactnum)
                    self.prof_contact_number.configure(state="disabled")

                    self.prof_bio_textbox.insert("1.0", desc)
                    self.prof_bio_textbox.configure(state="disabled")

    # Edit student profile contents
    def edit_prof_profile_settings(self):
        self.prof_edit_fields_frame = tk.CTkFrame(self.settings_tabview.tab("Profile"), width=300, height=350)
        self.prof_edit_fields_frame.place(x=150, y=0)

        self.update_prof_firstname = tk.CTkEntry(self.prof_edit_fields_frame, width=200, placeholder_text="First Name")
        self.update_prof_firstname.place(x=50, y=40)

        self.update_prof_lastname = tk.CTkEntry(self.prof_edit_fields_frame, width=200, placeholder_text="Last Name")
        self.update_prof_lastname.place(x=50, y=80)

        self.update_prof_contactno = tk.CTkEntry(self.prof_edit_fields_frame, width=200, placeholder_text="Contact no.")
        self.update_prof_contactno.place(x=50, y=120)

        self.update_prof_bio = tk.CTkEntry(self.prof_edit_fields_frame, width=200, placeholder_text="Bio")
        self.update_prof_bio.place(x=50, y=160)

        # Save Button
        self.save_button_ = tk.CTkButton(self.prof_edit_fields_frame, text="Save", command=self.prof_profile_save_clicked)
        self.save_button_.place(x=80, y=300)

    def edit_prof_account_settings(self):
        self.prof_edit_fields_acctframe = tk.CTkFrame(self.settings_tabview.tab("Account"), width=300, height=350)
        self.prof_edit_fields_acctframe.place(x=150, y=0)

        self.update_prof_password = tk.CTkEntry(self.prof_edit_fields_acctframe, width=200, show="*", placeholder_text="Enter new password")
        self.update_prof_password.place(x=50, y=40)

        self.confirm_password = tk.CTkEntry(self.prof_edit_fields_acctframe, width=200, show="*", placeholder_text="Confirm password")
        self.confirm_password.place(x=50, y=80)

        # Save Button...
        self.acct_save_button_ = tk.CTkButton(self.prof_edit_fields_acctframe, text="Save", command=self.prof_acct_save_clicked)
        self.acct_save_button_.place(x=80, y=300)

    # SAVING CHANGES FUNCTION
    # def close_save_changes(self):
    #     self.save_changes_frame.place_forget()

    # Saving..
    def prof_profile_save_clicked(self):
        # Confirmation Panel
        self.save_changes_frame = tk.CTkFrame(self, width=300, height=150)
        self.save_changes_frame.place(x=450, y=200)

        # Confirmation for Changes in Saving Label
        self.save_changes_label = tk.CTkLabel(self.save_changes_frame, text="Are you sure you want to save changes?")
        self.save_changes_label.place(x=40, y=30)

        # Buttons for Saving
        self.yes_button = tk.CTkButton(self.save_changes_frame, text="Yes", command=self.prof_profile_saved_clicked, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.save_changes_frame, text="No", command=self.close_save_changes, width=100)
        self.no_button.place(x=170, y=90)

    # Saved Function
    def prof_profile_close_saved_info_and_save_changes(self):
        self.saved_info_frame.place_forget()
        self.save_changes_frame.place_forget()
        self.prof_edit_fields_frame.place_forget()

    # Saved
    def prof_profile_saved_clicked(self):
        fname = self.update_prof_firstname.get()
        lname = self.update_prof_lastname.get()
        contactnum = self.update_prof_contactno.get()
        bio = self.update_prof_bio.get()
        email = self.username_entry.get()

        checker = queries.update_prof_info(lname, fname, contactnum, bio, email)

        if checker == True:
            self.saved_info_frame = tk.CTkFrame(self, width=300, height=150)
            self.saved_info_frame.place(x=450, y=200)

            # Already saved
            self.saved_label = tk.CTkLabel(self.saved_info_frame, text="Saved!")
            self.saved_label.place(x=130, y=30)

            # Buttons for Saved information
            self.ok_button = tk.CTkButton(self.saved_info_frame, text="Ok", command=self.prof_profile_close_saved_info_and_save_changes, width=100)
            self.ok_button.place(x=100, y=90)
        else:
            self.error_saving_frame = tk.CTkFrame(self, width=300, height=150)
            self.error_saving_frame.place(x=450, y=200)

            # Already saved
            self.error_label = tk.CTkLabel(self.error_saving_frame, text="Error updating your info!")
            self.error_label.place(x=130, y=30)

            # Buttons for Saved information
            self.ok_button = tk.CTkButton(self.error_saving_frame, text="Ok", command=self.close_prof_profile_update_errormsg, width=100)
            self.ok_button.place(x=100, y=90)

    def close_prof_profile_update_errormsg(self):
        self.error_saving_frame.place_forget()

    # Saving..
    def prof_acct_save_clicked(self):
        # Confirmation Panel
        self.save_changes_frame = tk.CTkFrame(self, width=300, height=150)
        self.save_changes_frame.place(x=450, y=200)

        # Confirmation for Changes in Saving Label
        self.save_changes_label = tk.CTkLabel(self.save_changes_frame, text="Are you sure you want to save changes?")
        self.save_changes_label.place(x=40, y=30)

        # Buttons for Saving
        self.yes_button = tk.CTkButton(self.save_changes_frame, text="Yes", command=self.prof_acct_saved_clicked, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.save_changes_frame, text="No", command=self.close_save_changes, width=100)
        self.no_button.place(x=170, y=90)

    # Saved Function
    def prof_acct_close_saved_info_and_save_changes(self):
        self.saved_info_frame.place_forget()
        self.save_changes_frame.place_forget()
        self.prof_edit_fields_acctframe.place_forget()

    # Saved
    def prof_acct_saved_clicked(self):
        email = self.username_entry.get()
        password = self.update_prof_password.get()
        confirm_pass = self.confirm_password.get()

        # HASH PASSWORD
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Add the salt to the password and hash it
        hash_object.update(password.encode())
        # Get the hex digest of the hash
        hash_password = hash_object.hexdigest()
        print(hash_password)

        # HASH CONFIRM PASSWORD
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Add the salt to the password and hash it
        hash_object.update(confirm_pass.encode())
        # Get the hex digest of the hash
        hash_confirm_password = hash_object.hexdigest()
        print(hash_confirm_password)

        if hash_password != hash_confirm_password:
            self.notsamepass_frame = tk.CTkFrame(self, width=300, height=150)
            self.notsamepass_frame.place(x=450, y=200)

            # Already saved
            self.notsame_label = tk.CTkLabel(self.notsamepass_frame, text="Password not identical!")
            self.notsame_label.place(x=130, y=30)

            # Buttons for Saved information
            self.ok_button = tk.CTkButton(self.notsamepass_frame, text="Ok", command=self.close_password_check, width=100)
            self.ok_button.place(x=100, y=90)
        else:
            checker = queries.update_prof_password(hash_password, email)

            if checker == True:
                self.saved_info_frame = tk.CTkFrame(self, width=300, height=150)
                self.saved_info_frame.place(x=450, y=200)

                # Already saved
                self.saved_label = tk.CTkLabel(self.saved_info_frame, text="Saved!")
                self.saved_label.place(x=130, y=30)

                # Buttons for Saved information
                self.ok_button = tk.CTkButton(self.saved_info_frame, text="Ok", command=self.prof_acct_close_saved_info_and_save_changes, width=100)
                self.ok_button.place(x=100, y=90)
            else:
                self.error_saving_frame = tk.CTkFrame(self, width=300, height=150)
                self.error_saving_frame.place(x=450, y=200)

                # Already saved
                self.error_label = tk.CTkLabel(self.error_saving_frame, text="Error updating your info!")
                self.error_label.place(x=130, y=30)

                # Buttons for Saved information
                self.ok_button = tk.CTkButton(self.error_saving_frame, text="Ok", command=self.close_prof_account_update_errormsg, width=100)
                self.ok_button.place(x=100, y=90)

    def close_password_check(self):
        self.notsamepass_frame.place_forget()
        self.save_changes_frame.place_forget()

    def close_prof_account_update_errormsg(self):
        self.error_saving_frame.place_forget()

    # Open ADMIN SETTINGS PANEL
    def admin_sidebar_settings_clicked(self):
        # MAIN SETTINGS PANEL
        self.main_frame_settings_ADMIN = tk.CTkFrame(self, width=920, height=600, corner_radius=50)
        self.main_frame_settings_ADMIN.place(x=180, y=0)

        self.settings_tabview = tk.CTkTabview(self.main_frame_settings_ADMIN, width=700, height=500)
        self.settings_tabview.place(x=110, y=30)
        self.settings_tabview.add("Profile")
        self.settings_tabview.add("Account")

        # Column Configuration
        self.settings_tabview.tab("Profile").grid_columnconfigure(0, weight=1)
        self.settings_tabview.tab("Account").grid_columnconfigure(0, weight=1)

        # =================== PROFILE TAB ========================
        #Profile Tab Information
        # First Name
        self.admin_first_name_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="First Name :")
        self.admin_first_name_label.place(x=120, y=30)

        self.admin_first_name_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.admin_first_name_txtfield.place(x=200, y=30)

        # Last Name
        self.admin_last_name_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Last Name :")
        self.admin_last_name_label.place(x=120, y=70)

        self.admin_last_name_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.admin_last_name_txtfield.place(x=200, y=70)

        self.occupation_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Occupation:")
        self.occupation_label.place(x=120, y=110)

        self.occupation_txtfield = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300)
        self.occupation_txtfield.place(x=200, y=110)

        # Transferring occupation to textfield
        occupation = self.occupation_name.cget("text")
        self.occupation_txtfield.delete(0, 'end')
        self.occupation_txtfield.insert(0, occupation)
        self.occupation_txtfield.configure(state="disabled")

        # Contact no:
        self.admin_number_label = tk.CTkLabel(self.settings_tabview.tab("Profile"), text="Contact no.:")
        self.admin_number_label.place(x=120, y=150)

        self.admin_contact_number = tk.CTkEntry(self.settings_tabview.tab("Profile"), width=300, placeholder_text="contact number")
        self.admin_contact_number.place(x=200, y=150)

        # Edit Button
        self.edit_button_ = tk.CTkButton(self.settings_tabview.tab("Profile"), text="Edit", command=self.edit_admin_profile_settings)
        self.edit_button_.place(x=360, y=400)

        # =================== ACCOUNT TAB ========================
        self.email_label = tk.CTkLabel(self.settings_tabview.tab("Account"), text="Email:")
        self.email_label.place(x=80, y=30)

        self.email_txtfield = tk.CTkEntry(self.settings_tabview.tab("Account"), width=200)
        self.email_txtfield.place(x=160, y=30)
        
        # Transferring input email here...
        email = self.username_entry.get()
        self.email_txtfield.delete(0, 'end')
        self.email_txtfield.insert(0, email)
        self.email_txtfield.configure(state="disabled")

        # Password Textfield...
        self.passW_label = tk.CTkLabel(self.settings_tabview.tab("Account"), text="Password:")
        self.passW_label.place(x=80, y=80)

        self.passW_txtfield = tk.CTkEntry(self.settings_tabview.tab("Account"), width=200)
        self.passW_txtfield.place(x=160, y=80)
        
        # Transferring input password here...
        passW = self.password_entry.get()
        self.passW_txtfield.delete(0, 'end')
        self.passW_txtfield.insert(0, passW)
        self.passW_txtfield.configure(state="disabled",show="*")

        # Edit Button...
        self.edit_button_ = tk.CTkButton(self.settings_tabview.tab("Account"), text="Edit", command=self.edit_admin_account_settings)
        self.edit_button_.place(x=360, y=400)

    # Saving..
    def admin_profile_save_clicked(self):
        # Confirmation Panel
        self.save_changes_frame = tk.CTkFrame(self, width=300, height=150)
        self.save_changes_frame.place(x=450, y=200)

        # Confirmation for Changes in Saving Label
        self.save_changes_label = tk.CTkLabel(self.save_changes_frame, text="Are you sure you want to save changes?")
        self.save_changes_label.place(x=40, y=30)

        # Buttons for Saving
        self.yes_button = tk.CTkButton(self.save_changes_frame, text="Yes", command=self.admin_profile_saved_clicked, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.save_changes_frame, text="No", command=self.close_save_changes, width=100)
        self.no_button.place(x=170, y=90)

    # Edit student profile contents
    def edit_admin_profile_settings(self):
        self.admin_edit_fields_frame = tk.CTkFrame(self.settings_tabview.tab("Profile"), width=300, height=350)
        self.admin_edit_fields_frame.place(x=150, y=0)

        self.update_admin_firstname = tk.CTkEntry(self.admin_edit_fields_frame, width=200, placeholder_text="First Name")
        self.update_admin_firstname.place(x=50, y=40)

        self.update_admin_lastname = tk.CTkEntry(self.admin_edit_fields_frame, width=200, placeholder_text="Last Name")
        self.update_admin_lastname.place(x=50, y=80)

        self.update_admin_contactno = tk.CTkEntry(self.admin_edit_fields_frame, width=200, placeholder_text="Contact no.")
        self.update_admin_contactno.place(x=50, y=120)

        # Save Button
        self.save_button_ = tk.CTkButton(self.admin_edit_fields_frame, text="Save", command=self.admin_profile_save_clicked)
        self.save_button_.place(x=80, y=300)

    def edit_admin_account_settings(self):
        self.admin_edit_fields_acctframe = tk.CTkFrame(self.settings_tabview.tab("Account"), width=300, height=350)
        self.admin_edit_fields_acctframe.place(x=150, y=0)

        self.update_admin_password = tk.CTkEntry(self.admin_edit_fields_acctframe, width=200, show="*", placeholder_text="Enter new password")
        self.update_admin_password.place(x=50, y=40)

        self.confirm_password = tk.CTkEntry(self.admin_edit_fields_acctframe, width=200, show="*", placeholder_text="Confirm password")
        self.confirm_password.place(x=50, y=80)

        # Save Button...
        self.acct_save_button_ = tk.CTkButton(self.admin_edit_fields_acctframe, text="Save", command=self.admin_acct_save_clicked)
        self.acct_save_button_.place(x=80, y=300)

    # Saved Function
    def admin_profile_close_saved_info_and_save_changes(self):
        self.saved_info_frame.place_forget()
        self.save_changes_frame.place_forget()
        self.admin_edit_fields_frame.place_forget()

    # Saved
    def admin_profile_saved_clicked(self):
        self.saved_info_frame = tk.CTkFrame(self, width=300, height=150)
        self.saved_info_frame.place(x=450, y=200)

        # Already saved
        self.saved_label = tk.CTkLabel(self.saved_info_frame, text="Saved!")
        self.saved_label.place(x=130, y=30)

        # Buttons for Saved information
        self.ok_button = tk.CTkButton(self.saved_info_frame, text="Ok", command=self.admin_profile_close_saved_info_and_save_changes, width=100)
        self.ok_button.place(x=100, y=90)

    # Saving..
    def admin_acct_save_clicked(self):
        # Confirmation Panel
        self.save_changes_frame = tk.CTkFrame(self, width=300, height=150)
        self.save_changes_frame.place(x=450, y=200)

        # Confirmation for Changes in Saving Label
        self.save_changes_label = tk.CTkLabel(self.save_changes_frame, text="Are you sure you want to save changes?")
        self.save_changes_label.place(x=40, y=30)

        # Buttons for Saving
        self.yes_button = tk.CTkButton(self.save_changes_frame, text="Yes", command=self.admin_acct_saved_clicked, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.save_changes_frame, text="No", command=self.close_save_changes, width=100)
        self.no_button.place(x=170, y=90)

    # Saved Function
    def admin_acct_close_saved_info_and_save_changes(self):
        self.saved_info_frame.place_forget()
        self.save_changes_frame.place_forget()
        self.admin_edit_fields_acctframe.place_forget()

    # Saved
    def admin_acct_saved_clicked(self):
        self.saved_info_frame = tk.CTkFrame(self, width=300, height=150)
        self.saved_info_frame.place(x=450, y=200)

        # Already saved
        self.saved_label = tk.CTkLabel(self.saved_info_frame, text="Saved!")
        self.saved_label.place(x=130, y=30)

        # Buttons for Saved information
        self.ok_button = tk.CTkButton(self.saved_info_frame, text="Ok", command=self.admin_acct_close_saved_info_and_save_changes, width=100)
        self.ok_button.place(x=100, y=90)

    # ==================================== OTHER FUNCTIONS ====================================

    # SWITCH MODE
    def change_appearance_mode_event(self, new_appearance_mode: str):
        tk.set_appearance_mode(new_appearance_mode)

# CLICK LOGIN
    def login_event(self):
        # Check if the user is currently locked out
        if self.lockout_timer and time.time() < self.lockout_timer:
            self.incorrect_login_frame = tk.CTkFrame(self, width=390, height=150)
            self.incorrect_login_frame.place(x=360, y=200)

            # Confirmation Label
            self.success_signup_label = tk.CTkLabel(self.incorrect_login_frame, text="Account locked. Try again after 30 minutes.")
            self.success_signup_label.place(x=80, y=30)

            # Button
            self.back_to_login_button = tk.CTkButton(self.incorrect_login_frame, text="OK", width=100, command=self.retry_to_login)
            self.back_to_login_button.place(x=140, y=70)
            return

        email = self.username_entry.get()
        password = self.password_entry.get()

        # HASH PASSWORD
        hash_object = hashlib.sha256()
        hash_object.update(password.encode())
        hash_password = hash_object.hexdigest()
        print(hash_password)

        stud_credential_check = queries.login_student(email, hash_password)
        prof_credential_check = queries.login_professor(email, hash_password)
        admin_credential_check = queries.login_admin(email, password)

        if stud_credential_check or prof_credential_check or admin_credential_check:
            # Reset login attempts on successful login
            self.login_attempts = 0

            if stud_credential_check:
                self.get_student_login_info()
                self.stud_default_main()
                self.occupation_name.configure(text="STUDENT")

            elif prof_credential_check:
                self.get_professor_login_info()
                self.prof_default_main()
                self.occupation_name.configure(text="PROFESSOR")

            elif admin_credential_check:
                self.get_admin_login_info()
                self.admin_default_main()
                self.occupation_name.configure(text="ADMIN")

            # Remove Login Panel
            self.login_frame.place_forget()

        else:
            # Increment login attempts
            self.login_attempts += 1

            # Check if maximum attempts reached
            if self.login_attempts >= 3:
                self.incorrect_login_frame = tk.CTkFrame(self, width=390, height=150)
                self.incorrect_login_frame.place(x=360, y=200)

                # Confirmation Label
                self.success_signup_label = tk.CTkLabel(self.incorrect_login_frame, text="Account locked. Try again after 30 minutes.")
                self.success_signup_label.place(x=80, y=30)

                # Button
                self.back_to_login_button = tk.CTkButton(self.incorrect_login_frame, text="OK", width=100, command=self.retry_to_login)
                self.back_to_login_button.place(x=140, y=70)
                self.lockout_timer = time.time() + 1800
            else:
                # Retry Login
                self.incorrect_credentials()

    # INCORRECT CREDENTIAL NOTIF
    def incorrect_credentials(self):
        # Show panel of incorrect credential
        # Confirmation Panel
        self.incorrect_login_frame = tk.CTkFrame(self, width=390, height=150)
        self.incorrect_login_frame.place(x=360, y=200)

        # Confirmation Label
        self.success_signup_label = tk.CTkLabel(self.incorrect_login_frame, text="Incorrect credentials!")
        self.success_signup_label.place(x=130, y=30)

        # Button
        self.back_to_login_button = tk.CTkButton(self.incorrect_login_frame, text="OK", width=100, command=self.retry_to_login)
        self.back_to_login_button.place(x=140, y=70)

    # TOGGLE PASSWORD
    def toggle_password_visibility(self):
        if self.password == True:
            self.password_entry.configure(show="*")
        else:
            self.password_entry.configure(show="")

    # RETURN TO LOGIN FROM SIGN UP
    def return_to_login(self):
        self.signup_frame.place_forget()
        self.show_login_frame()

    # RETURN TO LOGIN FROM INCORRECT CREDENTIAL CONFIRMATION
    def retry_to_login(self):
        self.incorrect_login_frame.place_forget()
        self.show_login_frame()

    # CLOSE LOGOUT CONFIRMATION
    def close_logout_confirmation(self):
        self.logout_confirmation_frame.place_forget()

    # LOGOUT
    def logout_clicked(self):
        # Confirmation Panel
        self.logout_confirmation_frame = tk.CTkFrame(self, width=300, height=150)
        self.logout_confirmation_frame.place(x=450, y=200)

        # Confirmation Label
        self.confirm_logout_label = tk.CTkLabel(self.logout_confirmation_frame, text="Are you sure you want to log out?")
        self.confirm_logout_label.place(x=50, y=30)

        # Buttons
        self.yes_button = tk.CTkButton(self.logout_confirmation_frame, text="Yes", command=self.record_logout_backtologin, width=100)
        self.yes_button.place(x=30, y=90)

        self.no_button = tk.CTkButton(self.logout_confirmation_frame, text="No", command=self.close_logout_confirmation, width=100)
        self.no_button.place(x=170, y=90)

    # Function to record logout info then back to login frame
    def record_logout_backtologin(self):
        if self.occupation_name.cget("text") == "STUDENT":
            self.get_student_logout_info()
        elif self.occupation_name.cget("text") == "PROFESSOR":
            self.get_professor_logout_info()
        elif self.occupation_name.cget("text") == "ADMIN":
            self.get_admin_logout_info()
        
        self.show_login_frame()

    # CHECK RADIOBUTTON SELECTION
    def check_radio_selection(self):
        choice = str(self.radio_var.get())
        
        if choice == "1":
            selected = "Option 'student' was selected!"
        if choice == "2":
            selected = "Option 'professor' was selected!"
        
        print(selected)

    # SIGN UP SUBMISSION
    def submit_registration(self):
        choice = str(self.radio_var.get())

        email = self.signup_username_entry.get()
        firstname = self.signup_firstname_entry.get()
        lastname = self.signup_lastname_entry.get()
        password = self.signup_password_entry.get()
        confirmpass = self.signup_confirmpassword_entry.get()

        # HASH PASSWORD
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Add the salt to the password and hash it
        hash_object.update(password.encode())
        # Get the hex digest of the hash
        hash_password = hash_object.hexdigest()
        print(hash_password)

        # HASH CONFIRM PASSWORD
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Add the salt to the password and hash it
        hash_object.update(confirmpass.encode())
        # Get the hex digest of the hash
        hash_confirm_password = hash_object.hexdigest()
        print(hash_confirm_password)
        valid_email_formats = ["@gmail.com", "@yahoo.com", "@edu.ph"]

        if email == "" or firstname == "" or lastname == "" or password == "" or confirmpass == "" or choice == "0":
                    self.fillup_info_warning_frame = tk.CTkFrame(self, width=300, height=150)
                    self.fillup_info_warning_frame.place(x=450, y=200)

                    # Already saved
                    self.fillup_info_warning_label = tk.CTkLabel(self.fillup_info_warning_frame, text="Please fill out all fields!")
                    self.fillup_info_warning_label.place(x=100, y=30)

                    # Buttons for Saved information
                    self.ok_button = tk.CTkButton(self.fillup_info_warning_frame, text="Ok", command=self.close_fillup_warning, width=100)
                    self.ok_button.place(x=100, y=90)
        elif not any(format in email for format in valid_email_formats):
                
                    self.invalid_email_frame = tk.CTkFrame(self, width=500, height=150)
                    self.invalid_email_frame.place(x=450, y=200)

                        # Invalid email message
                    self.invalid_email_label = tk.CTkLabel(self.invalid_email_frame, text="Invalid email format. Please use @gmail.com, @yahoo.com, or @edu.ph.")
                    self.invalid_email_label.place(x=50, y=30)

                        # Ok button
                    self.ok_button = tk.CTkButton(self.invalid_email_frame, text="Ok", command=self.close_invalid_email, width=100)
                    self.ok_button.place(x=100, y=90)

        else:

            if hash_password != hash_confirm_password:
                self.notsamepass_frame = tk.CTkFrame(self, width=300, height=150)
                self.notsamepass_frame.place(x=450, y=200)

                # Already saved
                self.notsame_label = tk.CTkLabel(self.notsamepass_frame, text="Password not identical!")
                self.notsame_label.place(x=130, y=30)

                # Buttons for Saved information
                self.ok_button = tk.CTkButton(self.notsamepass_frame, text="Ok", command=self.close_pass_confirm, width=100)
                self.ok_button.place(x=100, y=90)
            else:
                                    
                    if choice == "1":
                        # print("Email: ", email, " First Name: ", firstname, " Last Name: ", lastname, " Password: ", password, " User is a student!")
                        queries.student_signup(lastname, firstname, email, hash_password)

                    if choice == "2":
                        # print("Email: ", email, " First Name: ", firstname, " Last Name: ", lastname, " Password: ", password, " User is a professor!")
                        queries.prof_signup(lastname, firstname, email, hash_password)

                    # Confirmation Panel
                    self.success_registration_frame = tk.CTkFrame(self, width=400, height=150)
                    self.success_registration_frame.place(x=360, y=200)

                    # Confirmation Label
                    self.success_signup_label = tk.CTkLabel(self.success_registration_frame, text="You've successfully registered your account!")
                    self.success_signup_label.place(x=70, y=30)

                    # Button
                    self.back_to_login_button = tk.CTkButton(self.success_registration_frame, text="Back to Login", width=200, command=self.return_to_login)
                    self.back_to_login_button.place(x=100, y=70)

    def close_fillup_warning(self):
        self.fillup_info_warning_frame.place_forget()

    def close_pass_confirm(self):
        self.notsamepass_frame.place_forget()

    def close_invalid_email(self):
        self.invalid_email_frame.destroy()

# ================================= MAIN FUNCTION ====================================

if __name__ == "__main__":
    app = App()
    app.mainloop()