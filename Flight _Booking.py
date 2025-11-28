import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import csv
import os
from datetime import datetime, timedelta

#--------------Aligning  contents in csv File--------------------
def align_csv(file_path):                                       
    try:
        with open(file_path, "r") as f:
            rows = list(csv.reader(f))
        if not rows:
            return

        # Calculate max width for each column
        col_widths = [max(len(str(cell).strip()) for cell in col) for col in zip(*rows)]

        with open(file_path, "w", newline="") as f:
            for row in rows:
                aligned = []
                for i, cell in enumerate(row):
                    clean = str(cell).strip()
                    padded = clean.ljust(col_widths[i])
                    aligned.append(padded)
                line = ', '.join(aligned)  # comma + one space
                f.write(line + '\n')
    except Exception as e:
        print(f"Error aligning CSV: {e}")

# -------------------- File Paths --------------------
LOGIN_FILE = "Login.csv"
USER_FILE = "User_Details.csv"
BOOKING_FILE = "Current_Booking.csv"
PREVIOUS_BOOKING_FILE = "Previous_Booking.csv"
FLIGHT_FILE = "Flights.csv"
PASSENGER_FILE = "Passenger_Details.csv"
airports = ["Bengaluru", "Chennai", "Hyderabad", "Delhi", "Kolkata"]
logged_in_user = {"Username": "", "password": "","userID":"","Name":""}
selected_flight = None
passenger_entries = []
passenger_count = 0
current_passenger_index = 0
is_editing = False
backtracking = False
pending_booking_data = []
selected_passengers = []
selected_passenger_ids = set()

# -------------------- User Management --------------------
def read_users():
    if not os.path.exists(LOGIN_FILE):
        return []
    with open(LOGIN_FILE, mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        return [row for row in reader if row]

def write_user(Username, password,userID):
    if not os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE,mode="w",newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Password", "UserID"])
    with open(LOGIN_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([Username, password, userID])
    align_csv(LOGIN_FILE)

def read_user_details():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        return [row for row in reader if row]

def write_user_details(userID,User_details):
    if not os.path.exists(USER_FILE):
        with open(USER_FILE,mode="w",newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["UserID","Name","DOB","Email","Gender","Phone","Nationality"])
    with open(USER_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([userID]+User_details)
    align_csv(USER_FILE)

def read_passenger_details():
    if not os.path.exists(PASSENGER_FILE):
        return []
    with open(PASSENGER_FILE, mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        passenger = []
        for row in reader:
            if row[0].strip()==logged_in_user["userID"].strip():
                passenger += [row]
        return passenger

def write_passenger_details(userID,passengerID,passenger_details):
    if not os.path.exists(PASSENGER_FILE):
        with open(PASSENGER_FILE,mode="w",newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["UserID","PassengerID","Name","DOB","Email","Gender","Phone"])
    with open(PASSENGER_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([userID,passengerID]+passenger_details)
    align_csv(PASSENGER_FILE)

def generate_userID():
    users = read_users()
    if not users:
        return "U001"
    
    userID = 'U' + str(int(users[len(users)-1][2].strip()[1::])+1).zfill(3)
    return userID

def generate_passengerID():
    passengers = read_passenger_details()
    if not passengers:
        return logged_in_user["userID"].strip()+"P001"
    
    passengerID = logged_in_user["userID"].strip() + 'P' + str(int(passengers[-1][1].strip()[5::])+1).zfill(3)
    return passengerID

def create_account(prefill_user="", prefill_pass=""):
    center_window(300, 380)
    login_frame.pack_forget()
    account_frame.pack(fill="both", expand=True)

    for widget in account_frame.winfo_children():
        widget.destroy()

    box = tk.Frame(account_frame, bg="#e3f2fd", bd=2, relief="groove")
    box.place(relx=0.5, rely=0.5, anchor="center", width=300, height=380)

    tk.Label(box, text="🆕 Create Account", font=("Helvetica", 14, "bold"), bg="#e3f2fd").pack(pady=(15, 10))

    tk.Label(box, text="Choose a Username", font=("Helvetica", 12), bg="#e3f2fd").pack(pady=5)
    entry_user = tk.Entry(box, font=("Helvetica", 11), justify="center")
    entry_user.insert(0, prefill_user)
    entry_user.pack(pady=5)

    tk.Label(box, text="Set a Password", font=("Helvetica", 12), bg="#e3f2fd").pack(pady=5)
    entry_pass = tk.Entry(box, show="*", font=("Helvetica", 11), justify="center")
    entry_pass.insert(0, prefill_pass)
    entry_pass.pack(pady=5)

    def proceed_to_confirm():
        Username = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not Username or not password:
            messagebox.showerror("🚫 Error", "Username and password cannot be empty.")
            return
        if ' '  in Username:
            messagebox.showerror("🚫 Error","No Spaces allowed in Username")
            return
        if Username[0]  not in [chr(i) for i in range(ord('A'),ord('['))]+[chr(i) for i in range(ord('a'), ord('{') )]:
            messagebox.showerror("🚫 Error", "Username cannot start with special character.")
            return
        for i in Username:
            if i not in [chr(i) for i in range(ord('A'),ord('['))]+[chr(i) for i in range(ord('a'), ord('{') )]+['@','_']+[str(i) for i in range(10)]:
                messagebox.showerror("🚫 Error", "Username cannot have special character except '@' and '_'.")
                return
        if len(Username)< 8 or len(Username)>12:
            messagebox.showerror("🚫 Error", "Username should be atleast 8 characters and less than 12")
            return
        if len(password)< 6 or len(password)>10:
            messagebox.showerror("🚫 Error","Password should be atleast 6 characters and less than 15")
            return
        
        users = read_users()
        usernames = [u[0].strip() for u in users]

        if Username in usernames:
            messagebox.showerror("🚫 Error", "Account already exists.")
            return

        userID = generate_userID()
        confirm_password(Username, password,userID)

    tk.Button(box, text="Next ➡️", command=proceed_to_confirm,
              bg="#4CAF50", fg="white", font=("Helvetica", 11)).pack(pady=(10, 5))

    tk.Button(box, text="⬅️ Back", command=lambda: [account_frame.pack_forget(), center_window(800, 600), login_frame.pack(pady=10)],
              bg="#604745", fg="white", font=("Helvetica", 11)).pack()

def confirm_password(Username, password,userID):
    center_window(300, 250)
    for widget in account_frame.winfo_children():
        widget.destroy()

    account_frame.configure(bg="#f5f5f5")
    account_frame.pack(fill="both", expand=True)

    box = tk.Frame(account_frame, bg="#e3f2fd", bd=2, relief="groove")
    box.place(relx=0.5, rely=0.5, anchor="center", width=300, height=250)

    tk.Label(box, text=f"Confirm password for '{Username}'", font=("Helvetica", 12), bg="#e3f2fd", fg="#000000").pack(pady=5)
    entry_confirm = tk.Entry(box, show="*", font=("Helvetica", 11), justify="center")
    entry_confirm.pack(pady=5)

    def submit():
        confirm = entry_confirm.get()
        if confirm == password:
            account_frame.pack_forget()
            center_window(400, 500)
            account_frame.pack(fill="both", expand=True)
            user_details(Username, password, userID)
        else:
            messagebox.showerror("❌ Error", "Passwords do not match.")

    tk.Button(box, text="Create Account", command=submit, bg="#2196F3", fg="white", font=("Helvetica", 11)).pack(pady=10)
    tk.Button(box, text="⬅️ Back", command=lambda: [account_frame.pack_forget(),center_window(300, 380),create_account(prefill_user=Username, prefill_pass=password)], 
                bg="#604745", fg="white", font=("Helvetica", 11)).pack(pady=5)

def user_details(Username, password, userID):
    account_frame.configure(bg="#f5f5f5")
    account_frame.pack(fill="both", expand=True)

    for widget in account_frame.winfo_children():
        widget.destroy()

    box = tk.Frame(account_frame, bg="#e3f2fd", bd=2, relief="groove")
    box.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)

    tk.Label(box, text="👤 Enter Your Details", font=("Helvetica", 14, "bold"), bg="#e3f2fd").pack(pady=(15, 10))

    # Name
    tk.Label(box, text="Full Name", font=("Helvetica", 12,"bold"), bg="#e3f2fd").pack(pady=5)
    name_entry = tk.Entry(box, font=("Helvetica", 11), justify="center")
    name_entry.pack()

    # DOB
    tk.Label(box, text="Date of Birth", font=("Helvetica", 12,"bold"), bg="#e3f2fd").pack(pady=5)
    dob_mindate = datetime(1900, 1, 1)
    dob_maxdate = datetime.today().replace(year=datetime.today().year - 18)

    dob_picker = DateEntry(
        box,
        width=12,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        mindate=dob_mindate,
        maxdate=dob_maxdate,
        year=dob_maxdate.year,
        month=dob_maxdate.month,
        day=dob_maxdate.day,
        date_pattern='dd-mm-yyyy',
        state="readonly"
    )
    dob_picker.pack()

    # Email
    tk.Label(box, text="Email Address", font=("Helvetica", 12,"bold"), bg="#e3f2fd").pack(pady=5)
    email_entry = tk.Entry(box, font=("Helvetica", 11), justify="center")
    email_entry.pack()

    # Gender
    tk.Label(box, text="Gender", font=("Helvetica", 12,"bold"), bg="#e3f2fd").pack(pady=5)
    gender_var = tk.StringVar(value="Male")
    gender_frame = tk.Frame(box, bg="#e3f2fd")
    gender_frame.pack()
    ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left", padx=10)
    ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left", padx=10)
    ttk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other").pack(side="left", padx=10)

    # Phone
    tk.Label(box, text="Phone Number", font=("Helvetica", 12,"bold"), bg="#e3f2fd").pack(pady=5)
    phone_entry = tk.Entry(box, font=("Helvetica", 11), justify="center")
    phone_entry.pack()

    # Nationality
    tk.Label(box, text="Nationality", font=("Helvetica", 12,"bold"), bg="#e3f2fd").pack(pady=5)
    countries = ["India", "USA", "UK", "Canada", "Australia", "Germany", "France", "Japan", "Singapore"]
    nationality_cb = ttk.Combobox(box, values=countries, state="readonly", justify="center")
    nationality_cb.pack()

    def finalize_account():
        name = name_entry.get().strip()
        dob = dob_picker.get_date().strftime("%d-%m-%y")
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        nationality = nationality_cb.get().strip()
        gender = gender_var.get()

        if not name.replace(" ", "").isalpha():
            messagebox.showerror("❌ Error", "Name must contain only letters and spaces.")
            return
        if '@gmail.com' not in email:
            messagebox.showerror("❌ Error", "Enter a valid email address.")
            return
        if email[0] =="@":
            messagebox.showerror("❌ Error", "Enter a valid email address.")
            return
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("❌ Error", "Phone number must be a 10-digit number.")
            return
        if not nationality:
            messagebox.showerror("❌ Error", "Please select your nationality.")
            return

        write_user(Username, password, userID)
        write_user_details(userID,[name,dob,email,gender,phone,nationality])
        messagebox.showinfo("✅ Success", f"Account created successfully. Welcome {name}!")

        logged_in_user["Username"] = Username
        logged_in_user["password"] = password
        logged_in_user["userID"] = userID
        logged_in_user["Name"] = name
        account_frame.pack_forget()
        center_window(800, 600)
        show_dashboard()

    tk.Button(box, text="Submit ✅", command=finalize_account,
              bg="#4CAF50", fg="white", font=("Helvetica", 11)).pack(pady=15)

    tk.Button(box, text="⬅️ Back", command=lambda: [account_frame.pack_forget(), center_window(300, 250), confirm_password(Username, password, userID)],
              bg="#604745", fg="white", font=("Helvetica", 11)).pack()

def login():
    center_window(300, 380)
    login_frame.pack_forget()
    account_frame.configure(bg="#f5f5f5")
    account_frame.pack(fill="both", expand=True)

    for widget in account_frame.winfo_children():
        widget.destroy()

    box = tk.Frame(account_frame, bg="#e3f2fd", bd=2, relief="groove")
    box.place(relx=0.5, rely=0.5, anchor="center", width=300, height=380)

    tk.Label(box, text="🔑 Login", font=("Helvetica", 14, "bold"), bg="#e3f2fd", fg="#000000").pack(pady=(15, 10))

    tk.Label(box, text="Username", font=("Helvetica", 12), bg="#e3f2fd").pack(pady=5)
    entry_user = tk.Entry(box, font=("Helvetica", 11), justify="center")
    entry_user.pack(pady=5)

    tk.Label(box, text="Password", font=("Helvetica", 12), bg="#e3f2fd").pack(pady=5)
    entry_pass = tk.Entry(box, show="*", font=("Helvetica", 11), justify="center")
    entry_pass.pack(pady=5)

    def submit():
        Username = entry_user.get().strip()
        password = entry_pass.get().strip()
        users = read_users()
        user_detail = read_user_details()
        usernames = [u[0].strip() for u in users]
        user_name = {}
        for u in user_detail:
            user_name.update({u[0].strip():u[1].strip()})

        if Username not in usernames:
            messagebox.showerror("❌ Error", "Username not found.")
            return  # ✅ Stay on login screen

        for u in users:
            if u[0].strip() == Username and u[1].strip() == password:
                logged_in_user["Username"] = Username
                logged_in_user["password"] = password
                logged_in_user["userID"] = u[2]  
                logged_in_user["Name"] = user_name.get(u[2].strip(),"")               
                messagebox.showinfo("🎉 Welcome", f"Login successful. Welcome {logged_in_user['Name']} !")
                account_frame.pack_forget()
                center_window(800, 600)
                show_dashboard()
                return

        messagebox.showerror("❌ Error", "Incorrect password.")
        return  # ✅ Stay on login screen

    tk.Button(box, text="Submit ✅", command=submit, bg="#FF9800", fg="white", font=("Helvetica", 11)).pack(pady=(10, 5))
    tk.Button(box, text="⬅️ Back", command=lambda: [account_frame.pack_forget(),center_window(800, 600),login_frame.pack(pady=10)], 
              bg="#604745", fg="white", font=("Helvetica", 11)).pack(pady=5)
# -------------------- Dashboard --------------------
def show_logged_in_user_details():
    dashboard_frame.pack_forget()  # Hide dashboard

    account_info_frame = tk.Frame(root, bg="#f5f5f5")
    account_info_frame.pack(fill="both", expand=True)

    for widget in account_info_frame.winfo_children():
        widget.destroy()

    tk.Label(account_info_frame, text="👤 Account Information", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

    userID = logged_in_user["userID"].strip()
    user_details = read_user_details()
    user_dict = {row[0].strip(): [cell.strip() for cell in row[1:]] for row in user_details}
    details = user_dict.get(userID)

    if not details:
        tk.Label(account_info_frame, text="❌ No user details found.", font=("Helvetica", 12), bg="#f5f5f5", fg="red").pack(pady=10)
    else:
        card = tk.Frame(account_info_frame, bg="#ffffff", bd=2, relief="groove")
        card.config(width=720, height=300)
        card.pack(pady=10, padx=20)
        card.pack_propagate(False)

        tk.Label(card, text="🪪 Your Profile", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#333").pack(anchor="w", padx=10, pady=(10, 5))

        labels = ["Name", "DOB", "Email", "Gender", "Phone", "Nationality"]
        for label, value in zip(labels, details):
            row = tk.Frame(card, bg="#ffffff")
            row.pack(anchor="w", padx=20, pady=4)
            tk.Label(row, text=f"{label}:", font=("Helvetica", 12, "bold"), bg="#ffffff", width=12, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Helvetica", 12), bg="#ffffff", anchor="w").pack(side="left")

    tk.Button(account_info_frame, text="⬅️ Back to Dashboard",
              command=lambda: [account_info_frame.pack_forget(), dashboard_frame.pack(fill="both",expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 12), width=20).pack(pady=20)

def show_dashboard():
    center_window(800, 600)
    dashboard_frame.pack(fill="both",expand=True)
    account_btn = tk.Button(dashboard_frame,text=f"👤 {logged_in_user['Name']}",command=show_logged_in_user_details,
                            width=15,bg="#FFFFFF",fg="black",font=("Helvetica", 12, "bold"))
    account_btn.place(x=10, y=10, anchor="nw")

def logout():
    global logged_in_user
    logged_in_user = {"Username": "", "password": "","userID":"","Name":""}
    dashboard_frame.pack_forget()
    login_frame.pack(pady=10)

def segregate_bookings():
    now = datetime.now()
    current_file = BOOKING_FILE  # This is "Current_Booking.csv"
    previous_file = "Previous_Booking.csv"

    if not os.path.exists(current_file):
        return

    current_rows = []
    previous_rows = []

    with open(current_file, "r") as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            try:
                flight_id = row[1].strip()
                dep_date = row[2].strip()

                with open(FLIGHT_FILE, "r") as f_file:
                    f_reader = csv.reader(f_file)
                    next(f_reader)
                    for flight_row in f_reader:
                        if flight_row[0].strip() == flight_id:
                            dep_time = flight_row[3].strip()
                            dep_datetime = datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M")
                            if dep_datetime < now:
                                previous_rows.append(row)
                            else:
                                current_rows.append(row)
                            break
            except Exception as e:
                print(f"Error processing booking: {e}")
                continue

    # Write updated current bookings
    with open(current_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(current_rows)

    # Append previous bookings
    write_mode = "a" if os.path.exists(previous_file) else "w"
    with open(previous_file, write_mode, newline="") as file:
        writer = csv.writer(file)
        if write_mode == "w":
            writer.writerow(headers)
        writer.writerows(previous_rows)

    align_csv(current_file)
    align_csv(previous_file)

def show_passenger_details(flight_id, dep_date, parent_frame, booking_source=BOOKING_FILE):
    parent_frame.pack_forget()
    passenger_frame = tk.Frame(root, bg="#f5f5f5")
    passenger_frame.pack(fill="both", expand=True)

    tk.Label(passenger_frame, text=f"👥 Passengers for Flight {flight_id} on {dep_date}", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=10)

    canvas_container = tk.Frame(passenger_frame, bg="#f5f5f5")
    canvas_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(canvas_container, bg="#f5f5f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    found = False
    index = 0

    try:
        dep_date = datetime.strptime(dep_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        pass

    passenger_reference = []
    if os.path.exists(booking_source):
        with open(booking_source, "r") as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if row[0].strip() == logged_in_user["userID"].strip() and row[1].strip() == flight_id and row[2].strip() == dep_date:
                    passenger_reference.append(row)

    passenger_row = read_passenger_details()

    for row in passenger_reference:
        for rows in passenger_row:
            found = True
            if row[4].strip()== rows[1].strip():
                name, dob, gmail, gender, phone = rows[2:]
        if booking_source == BOOKING_FILE:
            try:
                dob_dt = datetime.strptime(dob.strip(), "%Y-%m-%d")
                today = datetime.today()
                age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
                passenger_type = " Adult" if age >= 18 else " Child"
            except:
                age = None
                passenger_type = ""
        else:
            passenger_type = ""
        index += 1

        card = tk.Frame(scrollable_frame, bg="#ffffff", bd=3, relief="ridge", width=760, height=290)
        card.pack(padx=20, pady=15)
        card.pack_propagate(False)

        header = tk.Frame(card, bg="#e3f2fd")
        header.pack(fill="x")
        tk.Label(header, text=f"🧾 Passenger {index}", font=("Helvetica", 14, "bold"), bg="#e3f2fd", fg="#333").pack(side="left", padx=10, pady=5)
        tk.Label(header, text=passenger_type, font=("Helvetica", 12, "italic"), bg="#e3f2fd", fg="#555").pack(side="right", padx=10)

        content = tk.Frame(card, bg="#ffffff")
        content.pack(fill="both", expand=True, padx=25, pady=20)

        def add_info_row(label_text, value_text):
            row = tk.Frame(content, bg="#ffffff")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, font=("Helvetica", 13, "bold"), bg="#ffffff", width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value_text, font=("Helvetica", 13), bg="#ffffff", anchor="w").pack(side="left")

        add_info_row("Name :", name)
        if booking_source == BOOKING_FILE and age is not None:
            add_info_row("Age :", f"{age} years")
        add_info_row("Gmail ID:",gmail)
        add_info_row("Gender :", gender)
        add_info_row("Phone :", phone)

        # ✅ Cancel Passenger Button (right-aligned, only for current bookings)
        if booking_source == BOOKING_FILE:
            def cancel_passenger(row_data=row):
                confirm = messagebox.askyesno("❌ Confirm Cancellation", f"Cancel booking for passenger '{row_data[4].strip()}'?")
                if not confirm:
                    return

                updated_rows = []
                with open(BOOKING_FILE, "r") as file:
                    reader = csv.reader(file)
                    headers = next(reader)
                    for r in reader:
                        if r != row_data:
                            updated_rows.append(r)

                with open(BOOKING_FILE, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(updated_rows)

                align_csv(BOOKING_FILE)
                messagebox.showinfo("✅ Cancelled", f"Passenger '{row_data[4].strip()}' has been removed.")
                passenger_frame.pack_forget()
                show_passenger_details(flight_id, dep_date, parent_frame, booking_source)

            btn_frame = tk.Frame(card, bg="#ffffff")
            btn_frame.pack( fill= "x", padx=10, pady=(0, 10))

            tk.Button(btn_frame, text="❌ Cancel Passenger", command=cancel_passenger,
                        bg="#f44336", fg="white", font=("Helvetica", 12, "bold"), width=18,height=1,padx=12,pady=6).pack(side="right",padx=10,ipady=8)

    if not found:
        tk.Label(scrollable_frame, text="📭 No passengers found for this flight on selected date.", font=("Helvetica", 12), fg="gray", bg="#f5f5f5").pack(pady=10)

    tk.Button(scrollable_frame, text="⬅️ Back", command=lambda: [passenger_frame.pack_forget(), display_user_bookings()],
              bg="#604745", fg="white", font=("Helvetica", 12), padx=20, pady=6).pack(pady=30)
    
def display_user_bookings():
    segregate_bookings()  
    
    dashboard_frame.pack_forget()
    bookings_frame = tk.Frame(root, bg="#f5f5f5")
    bookings_frame.pack(fill="both", expand=True)

    tk.Label(bookings_frame, text="📖 Your Bookings", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    button_frame = tk.Frame(bookings_frame, bg="#f5f5f5")
    button_frame.pack(pady=5)

    result_frame = tk.Frame(bookings_frame, bg="#f5f5f5")
    result_frame.pack(fill="both", expand=True)

    def show_bookings(filter_type):
        for widget in result_frame.winfo_children():
            widget.destroy()

        tk.Label(result_frame, text=f"{filter_type} Bookings", font=("Helvetica", 14, "bold"), bg="#f5f5f5").pack(pady=5)

        canvas = tk.Canvas(result_frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        booking_file = BOOKING_FILE if filter_type == "Current" else PREVIOUS_BOOKING_FILE
        found_flights = {}

        if os.path.exists(booking_file):
            with open(booking_file, "r") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row and row[0].strip() == logged_in_user["userID"].strip():
                        try:
                            flight_id = row[1].strip()
                            dep_date = row[2].strip()
                            arr_date = row[3].strip()

                            with open(FLIGHT_FILE, "r") as f_file:
                                f_reader = csv.reader(f_file)
                                next(f_reader)
                                for flight_row in f_reader:
                                    if flight_row and flight_row[0].strip() == flight_id:
                                        dep_time = flight_row[3].strip()
                                        arr_time = flight_row[4].strip()
                                        flight_data = [
                                            flight_id,
                                            flight_row[1],  # Departure Airport
                                            flight_row[2],  # Arrival Airport
                                            dep_date,
                                            dep_time,
                                            arr_date,
                                            arr_time,
                                            flight_row[5]   # Cost
                                        ]
                                        found_flights[tuple(flight_data)] = flight_id
                                        break
                        except Exception as e:
                            print(f"Error parsing booking or flight data: {e}")
                            continue

        if not found_flights:
            tk.Label(scrollable_frame, text=f"📭 No {filter_type.lower()} bookings found.",
                     font=("Helvetica", 12), fg="gray", bg="#f5f5f5").pack(pady=5)
            return

        for flight_data, flight_id in found_flights.items():
            card = tk.Frame(scrollable_frame, bg="#ffffff", bd=2, relief="raised", width=760, height=200)
            card.pack(padx=20, pady=12)
            card.pack_propagate(False)

            top = tk.Frame(card, bg="#ffffff")
            top.pack(fill="x", padx=10, pady=(12, 6))
            tk.Label(top, text=f"✈️ Flight {flight_data[0]}", font=("Helvetica", 15, "bold"),
                     fg="#333", bg="#ffffff").pack(side="left")

            route = tk.Frame(card, bg="#ffffff")
            route.pack(fill="x", padx=10, pady=6)
            route.columnconfigure(0, weight=1, uniform="route")
            route.columnconfigure(1, weight=1, uniform="route")
            route.columnconfigure(2, weight=1, uniform="route")

            dep = tk.Frame(route, bg="#ffffff")
            dep.grid(row=0, column=0)
            tk.Label(dep, text=flight_data[1], font=("Helvetica", 14, "bold"), fg="#2E8B57", bg="#ffffff").pack()
            tk.Label(dep, text=flight_data[3], font=("Helvetica", 13), fg="#2E8B57", bg="#ffffff").pack()
            tk.Label(dep, text=flight_data[4], font=("Helvetica", 13), fg="#2E8B57", bg="#ffffff").pack()

            tk.Label(route, text="➡️", font=("Helvetica", 30), bg="#ffffff").grid(row=0, column=1)

            arr = tk.Frame(route, bg="#ffffff")
            arr.grid(row=0, column=2)
            tk.Label(arr, text=flight_data[2], font=("Helvetica", 14, "bold"), fg="#1E90FF", bg="#ffffff").pack()
            tk.Label(arr, text=flight_data[5], font=("Helvetica", 13), fg="#1E90FF", bg="#ffffff").pack()
            tk.Label(arr, text=flight_data[6], font=("Helvetica", 13), fg="#1E90FF", bg="#ffffff").pack()

            tk.Button(card, text="View ",
                    command=lambda fid=flight_id, ddate=flight_data[3], source=booking_file: show_passenger_details(fid, ddate, bookings_frame, source),
                    bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"),
                    width=16, padx=12, pady=6).pack(anchor="e", padx=10, pady=10)

    tk.Button(button_frame, text="🟢 Current Bookings", command=lambda: show_bookings("Current"),
              bg="#4CAF50", fg="white", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Button(button_frame, text="🔙 Previous Bookings", command=lambda: show_bookings("Previous"),
              bg="#2196F3", fg="white", font=("Helvetica", 11)).pack(side="left", padx=10)

    tk.Button(bookings_frame, text="⬅️ Back", command=lambda: [bookings_frame.pack_forget(), dashboard_frame.pack(fill="both",expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 12)).pack(pady=10)
# -------------------- Flight Search & Booking --------------------
def open_search_window():
    dashboard_frame.pack_forget()
    search_frame.pack(fill="both", expand=True)

    for widget in search_frame.winfo_children():
        widget.destroy()

    tk.Label(search_frame, text="✈️ Search Flights", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    form_frame = ttk.Frame(search_frame)
    form_frame.pack(pady=10)

    ttk.Label(form_frame, text="Departure:").grid(row=0, column=0, padx=5, pady=5)
    dep_cb = ttk.Combobox(form_frame, values=airports, state="readonly", justify="center")
    dep_cb.grid(row=0, column=1)

    ttk.Label(form_frame, text="Arrival:").grid(row=1, column=0, padx=5, pady=5)
    arr_cb = ttk.Combobox(form_frame, values=airports, state="readonly", justify="center")
    arr_cb.grid(row=1, column=1)

    ttk.Label(form_frame, text="Date:").grid(row=2, column=0, padx=5, pady=5)
    date_pick = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                          borderwidth=2, mindate=datetime.today())
    date_pick.grid(row=2, column=1)

    def search_and_show():
        dep = dep_cb.get().strip()
        arr = arr_cb.get().strip()
        travel_date = date_pick.get_date()
        if dep == arr or not dep or not arr:
            messagebox.showerror("Error", "Please select valid departure and arrival airports.")
            return
        search_frame.pack_forget()
        open_flight_window(dep, arr, travel_date)

    ttk.Button(search_frame, text="Search Flights", command=search_and_show).pack(pady=10)

    tk.Button(search_frame, text="⬅️ Back", command=lambda: [search_frame.pack_forget(), dashboard_frame.pack(fill="both",expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 11)).pack(pady=10)

def open_flight_window(dep, arr, travel_date):
    global selected_flight
    search_frame.pack_forget()
    flight_frame.pack(fill="both", expand=True)

    for widget in flight_frame.winfo_children():
        widget.destroy()

    tk.Label(flight_frame, text="🛫 Available Flights", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    try:
        with open(FLIGHT_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)
            flights = []
            for row in reader:
                row = [cell.strip() for cell in row]
                if row[1].lower() == dep.lower() and row[2].lower() == arr.lower():
                    flights.append(row)
    except FileNotFoundError:
        messagebox.showerror("Error", "Flights.csv not found.")
        return

    valid_today = []
    valid_tomorrow = []
    now = datetime.now()
    tomorrow = travel_date + timedelta(days=1)

    for flight in flights:
        try:
            dep_time = datetime.strptime(flight[3], "%H:%M")
            arr_time = datetime.strptime(flight[4], "%H:%M")

            dep_datetime = datetime.combine(travel_date, dep_time.time())
            bumped = False

            if dep_datetime < now:
                bumped = True
                dep_datetime = datetime.combine(tomorrow, dep_time.time())

            arr_datetime = datetime.combine(dep_datetime.date(), arr_time.time())
            if arr_datetime < dep_datetime:
                arr_datetime += timedelta(days=1)

            dep_date = dep_datetime.strftime("%Y-%m-%d")
            dep_time_str = dep_datetime.strftime("%H:%M")
            arr_date = arr_datetime.strftime("%Y-%m-%d")
            arr_time_str = arr_datetime.strftime("%H:%M")

            flight_data = [
                flight[0], flight[1], flight[2],
                dep_date, dep_time_str,
                arr_date, arr_time_str,
                flight[5]
            ]

            if not bumped and dep_datetime.date() == travel_date:
                valid_today.append(flight_data)
            elif bumped or dep_datetime.date() == tomorrow:
                valid_tomorrow.append(flight_data)

        except Exception as e:
            print(f"Error parsing flight times: {e}")

    canvas = tk.Canvas(flight_frame, bg="#f5f5f5", width=780)
    scrollbar = ttk.Scrollbar(flight_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if not valid_today:
        tk.Label(scrollable_frame, text="📭 No flights available for today.", font=("Helvetica", 12,"bold"), bg="#f5f5f5", fg="gray").pack(pady=10)

    def render_flights(flight_list, label_text):
        if not flight_list:
            return
        tk.Label(scrollable_frame, text=label_text, font=("Helvetica", 14, "bold"), bg="#f5f5f5", fg="#333").pack(pady=(10, 5))
        for flight_data in flight_list:
            card = tk.Frame(scrollable_frame, bg="#ffffff", bd=1, relief="raised", width=760, height=180)
            card.pack(padx=20, pady=12)
            card.pack_propagate(False)

            top_row = tk.Frame(card, bg="#ffffff")
            top_row.pack(fill="x", padx=10, pady=(10, 5))

            tk.Label(top_row, text=f"✈️ Flight {flight_data[0]}", font=("Helvetica", 14, "bold"),
                     fg="#333", bg="#ffffff").pack(side="left")

            tk.Label(top_row, text=f"₹{flight_data[7]}", font=("Helvetica", 14, "bold"),
                     fg="#000000", bg="#ffffff").pack(side="right")

            route_frame = tk.Frame(card, bg="#ffffff")
            route_frame.pack(fill="x", padx=10, pady=5)
            route_frame.columnconfigure(0, weight=1, uniform="route")
            route_frame.columnconfigure(1, weight=1, uniform="route")
            route_frame.columnconfigure(2, weight=1, uniform="route")

            dep_block = tk.Frame(route_frame, bg="#ffffff")
            dep_block.grid(row=0, column=0, sticky="w")
            tk.Label(dep_block, text=flight_data[1], font=("Helvetica", 14, "bold"),
                     fg="#2E8B57", bg="#ffffff").pack(anchor="center")
            tk.Label(dep_block, text=flight_data[3], font=("Helvetica", 13),
                     fg="#2E8B57", bg="#ffffff").pack(anchor="center")
            tk.Label(dep_block, text=flight_data[4], font=("Helvetica", 13),
                     fg="#2E8B57", bg="#ffffff").pack(anchor="center")

            tk.Label(route_frame, text="➡️", font=("Helvetica", 30, "bold"),
                     fg="#555", bg="#ffffff").grid(row=0, column=1, sticky="nsew")

            arr_block = tk.Frame(route_frame, bg="#ffffff")
            arr_block.grid(row=0, column=2, sticky="w")
            tk.Label(arr_block, text=flight_data[2], font=("Helvetica", 14, "bold"),
                     fg="#1E90FF", bg="#ffffff").pack(anchor="center")
            tk.Label(arr_block, text=flight_data[5], font=("Helvetica", 13),
                     fg="#1E90FF", bg="#ffffff").pack(anchor="center")
            tk.Label(arr_block, text=flight_data[6], font=("Helvetica", 13),
                     fg="#1E90FF", bg="#ffffff").pack(anchor="center")

            book_btn = tk.Button(card, text=" Book ", command=lambda f=flight_data: open_passenger_form(f),
                                 bg="#4CAF50", fg="white", font=("Helvetica", 14, "bold"), padx=12, pady=6)
            book_btn.pack(anchor="e", padx=10, pady=10)

    if valid_today:
        render_flights(valid_today, f"🟢 Flights for {travel_date.strftime('%d - %m - %Y')}")
    else:
        render_flights(valid_tomorrow, f"🔄 Flights for {tomorrow.strftime('%d - %m - %Y')}")

    back_btn = tk.Button(scrollable_frame, text="⬅️ Back",
                         command=lambda: [flight_frame.pack_forget(), search_frame.pack(fill="both", expand=True)],
                         bg="#604745", fg="white", font=("Helvetica", 12), padx=20, pady=6)
    back_btn.pack(pady=20)

def open_passenger_form(flight):
    global selected_flight
    selected_flight = flight
    flight_frame.pack_forget()
    passenger_count_frame.pack(fill="both", expand=True)

    for widget in passenger_count_frame.winfo_children():
        widget.destroy()

    tk.Label(passenger_count_frame, text="👥 Passenger Count", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    form = ttk.Frame(passenger_count_frame)
    form.pack(pady=10)

    ttk.Label(form, text="Number of Adults:").grid(row=0, column=0, padx=5, pady=5)
    adult_count_var = tk.StringVar(value=0)
    ttk.Entry(form, textvariable=adult_count_var, justify="center").grid(row=0, column=1)

    ttk.Label(form, text="Number of Children:").grid(row=1, column=0, padx=5, pady=5)
    child_count_var = tk.StringVar(value=0)
    ttk.Entry(form, textvariable=child_count_var, justify="center").grid(row=1, column=1)

    def proceed():
        adults_str = adult_count_var.get().strip()
        children_str = child_count_var.get().strip()

        # ✅ Check if values are integers only
        if not adults_str.isdigit() or not children_str.isdigit():
            messagebox.showerror("❌ Error", "Invalid entries for adults or child")
            return

        adults = int(adults_str)
        children = int(children_str)
        total = adults + children

        if total <= 0:
            messagebox.showerror("❌ Error", "Enter at least one passenger.")
            return

        collect_passenger_info(total, adults, children)

    tk.Button(passenger_count_frame, text="Next ➡️",
              command=proceed,
              bg="#4CAF50", fg="white", font=("Helvetica", 11), width=20).pack(pady=10)

    tk.Button(passenger_count_frame, text="⬅️ Back",
              command=lambda: [passenger_count_frame.pack_forget(), flight_frame.pack(fill="both", expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 11), width=20).pack(pady=10)

def collect_passenger_info(count, adults, children):
    global current_passenger_index, passenger_entries, passenger_count, adult_count, child_count
    passenger_entries = []
    passenger_count = count
    adult_count = adults
    child_count = children
    current_passenger_index = 0
    passenger_count_frame.pack_forget()
    show_passenger_list_window()

def show_passenger_list_window():
    passenger_count_frame.pack_forget()
    passenger_form_frame.pack_forget()

    list_frame = tk.Frame(root, bg="#f5f5f5")
    list_frame.pack(fill="both", expand=True)

    tk.Label(list_frame, text="👥 Select Passengers", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    # Scrollable canvas
    canvas = tk.Canvas(list_frame, bg="#f5f5f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Track passengers; include PassengerID so we can persist selection state
    selected_passengers = []
    passenger_rows = read_passenger_details()

    if passenger_rows:
        adult_rows, child_rows = [], []
        for entry in passenger_rows:
            try:
                dob_dt = datetime.strptime(entry[3].strip(), "%Y-%m-%d")
                today = datetime.today()
                age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
            except:
                age = 0
            if age >= 18:
                adult_rows.append(entry)
            else:
                child_rows.append(entry)

        # Enforce adult/child selection quotas
        def update_selection_limits():
            selected_adults = sum(1 for var, details, cat, cb, pid in selected_passengers if var.get() and cat == "Adult")
            selected_children = sum(1 for var, details, cat, cb, pid in selected_passengers if var.get() and cat == "Child")

            # Adults
            if selected_adults >= adult_count:
                for var, details, cat, cb, pid in selected_passengers:
                    if cat == "Adult" and not var.get():
                        cb.config(state="disabled")
            else:
                for var, details, cat, cb, pid in selected_passengers:
                    if cat == "Adult":
                        cb.config(state="normal")

            # Children
            if selected_children >= child_count:
                for var, details, cat, cb, pid in selected_passengers:
                    if cat == "Child" and not var.get():
                        cb.config(state="disabled")
            else:
                for var, details, cat, cb, pid in selected_passengers:
                    if cat == "Child":
                        cb.config(state="normal")

        # Adults UI
        if adult_count > 0 and adult_rows:
            tk.Label(scrollable_frame, text="Adult", font=("Helvetica", 14, "bold"), bg="#f5f5f5").pack(pady=5)
            for i, entry in enumerate(adult_rows):
                passenger_id = entry[1].strip()   # PassengerID
                details = entry[2:]               # [Name, DOB, Gmail, Gender, Phone]

                card = tk.Frame(scrollable_frame, bg="#ffffff", bd=2, relief="groove")
                card.config(width=720, height=210)
                card.pack(pady=10, padx=20)
                card.pack_propagate(False)

                tk.Label(card, text=f"Adult Passenger {i+1}", font=("Helvetica", 13, "bold"), bg="#ffffff").pack(anchor="w", padx=10, pady=(5, 0))

                labels = ["Name", "DOB", "Gmail", "Gender", "Phone"]
                for lbl, value in zip(labels, details):
                    row = tk.Frame(card, bg="#ffffff")
                    row.pack(anchor="w", padx=20, pady=2)
                    tk.Label(row, text=f"{lbl}:", font=("Helvetica", 11, "bold"), bg="#ffffff", width=10, anchor="w").pack(side="left")
                    tk.Label(row, text=value, font=("Helvetica", 11), bg="#ffffff", anchor="w").pack(side="left")

                # Restore tick if previously selected
                var = tk.BooleanVar(value=(passenger_id in selected_passenger_ids))
                cb = tk.Checkbutton(card, text="Select", variable=var, bg="#ffffff", font=("Helvetica", 11),
                                    command=update_selection_limits)
                cb.pack(anchor="e", padx=10, pady=5)

                selected_passengers.append((var, details, "Adult", cb, passenger_id))

        # Children UI
        if child_count > 0 and child_rows:
            tk.Label(scrollable_frame, text="Child", font=("Helvetica", 14, "bold"), bg="#f5f5f5").pack(pady=5)
            for i, entry in enumerate(child_rows):
                passenger_id = entry[1].strip()   # PassengerID
                details = entry[2:]               # [Name, DOB, Gmail, Gender, Phone]

                card = tk.Frame(scrollable_frame, bg="#ffffff", bd=2, relief="groove")
                card.config(width=720, height=210)
                card.pack(pady=10, padx=20)
                card.pack_propagate(False)

                tk.Label(card, text=f"Child Passenger {i+1}", font=("Helvetica", 13, "bold"), bg="#ffffff").pack(anchor="w", padx=10, pady=(5, 0))

                labels = ["Name", "DOB", "Gmail", "Gender", "Phone"]
                for lbl, value in zip(labels, details):
                    row = tk.Frame(card, bg="#ffffff")
                    row.pack(anchor="w", padx=20, pady=2)
                    tk.Label(row, text=f"{lbl}:", font=("Helvetica", 11, "bold"), bg="#ffffff", width=10, anchor="w").pack(side="left")
                    tk.Label(row, text=value, font=("Helvetica", 11), bg="#ffffff", anchor="w").pack(side="left")

                # Restore tick if previously selected
                var = tk.BooleanVar(value=(passenger_id in selected_passenger_ids))
                cb = tk.Checkbutton(card, text="Select", variable=var, bg="#ffffff", font=("Helvetica", 11),
                                    command=update_selection_limits)
                cb.pack(anchor="e", padx=10, pady=5)

                selected_passengers.append((var, details, "Child", cb, passenger_id))
    else:
        tk.Label(scrollable_frame, text="📭 No Passenger details found.",
                 font=("Helvetica", 12), fg="gray", bg="#f5f5f5").pack(pady=5)

    # Bottom action buttons
    button_frame = tk.Frame(scrollable_frame, bg="#f5f5f5")
    button_frame.pack(pady=20)

    def proceed_next():
        list_frame.pack_forget()

        global passenger_entries, current_passenger_index, selected_adults, selected_children, selected_passenger_ids
        passenger_entries = []
        selected_adults = 0
        selected_children = 0

        # Rebuild persisted selection set with the latest choices
        selected_passenger_ids = set()

        for var, details, cat, cb, passenger_id in selected_passengers:
            if var.get():
                name, dob, gmail, gender, phone = details
                try:
                    dob_dt = datetime.strptime(dob.strip(), "%Y-%m-%d")
                    today = datetime.today()
                    age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
                except:
                    age = ""

                passenger_entries.append((name, dob, str(age), gmail, gender, phone))
                selected_passenger_ids.add(passenger_id)  # persist selected

                if age != "" and int(age) >= 18:
                    selected_adults += 1
                else:
                    selected_children += 1

        remaining_adults = adult_count - selected_adults
        remaining_children = child_count - selected_children

        if remaining_adults < 0 or remaining_children < 0:
            messagebox.showerror("❌ Error", "Selection does not match required adult/child count.")
            show_passenger_list_window()
            return

        if remaining_adults + remaining_children > 0:
            current_passenger_index = len(passenger_entries)
            open_individual_passenger_form()
        else:
            show_passenger_summary()

    tk.Button(button_frame, text="⬅️ Back",
              command=lambda: [list_frame.pack_forget(), passenger_count_frame.pack(fill="both", expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 12), width=20).pack(side="left", padx=10)

    tk.Button(button_frame, text="➡️ Next",
              command=proceed_next,
              bg="#2196F3", fg="white", font=("Helvetica", 12), width=20).pack(side="left", padx=10)


def open_individual_passenger_form(prefill=None):
    global current_passenger_index, passenger_entries, adult_count, child_count, passenger_count

    if current_passenger_index >= passenger_count:
        show_passenger_summary()
        return

    passenger_form_frame.pack(fill="both", expand=True)
    for widget in passenger_form_frame.winfo_children():
        widget.destroy()

    # ✅ Decide if this remaining passenger is adult or child
    entered_adults = sum(1 for e in passenger_entries if e[2] != "" and int(e[2]) >= 18)
    entered_children = sum(1 for e in passenger_entries if e[2] != "" and int(e[2]) < 18)

    if entered_adults < adult_count:
        label = f"Adult {entered_adults + 1}"
        dob_mindate = datetime(1900, 1, 1)
        dob_maxdate = datetime.today().replace(year=datetime.today().year - 18)
    else:
        label = f"Child {entered_children + 1}"
        dob_mindate = datetime.today().replace(year=datetime.today().year - 18)
        dob_maxdate = datetime.today()

    tk.Label(passenger_form_frame, text=f"{label} Details", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)
    progress_text = f"Remaining Passenger {current_passenger_index + 1} of {passenger_count}"
    tk.Label(passenger_form_frame, text=progress_text, font=("Helvetica", 12, "italic"), bg="#f5f5f5", fg="#555").pack(pady=(0, 10))

    # Prefill values
    name_var = tk.StringVar(value=prefill[0] if prefill else "")
    age_var = tk.StringVar()
    phone_var = tk.StringVar(value=prefill[5] if prefill else "")
    gmail_var = tk.StringVar(value=prefill[3] if prefill else "")
    gender_var = tk.StringVar(value=prefill[4] if prefill else "Male")

    ttk.Label(passenger_form_frame, text="Name:").pack(pady=5)
    name_entry = ttk.Entry(passenger_form_frame, textvariable=name_var, justify="center")
    name_entry.pack()

    ttk.Label(passenger_form_frame, text="Date of Birth:").pack(pady=5)
    dob_value = datetime.today().replace(year=datetime.today().year - 18)
    if prefill:
        try:
            dob_value = datetime.strptime(prefill[1], "%Y-%m-%d")  # ✅ unified format
        except:
            pass

    dob_picker = DateEntry(passenger_form_frame, width=12, background='darkblue', foreground='white',
                           borderwidth=2, mindate=dob_mindate, maxdate=dob_maxdate,
                           year=dob_value.year, month=dob_value.month, day=dob_value.day,
                           date_pattern='dd-mm-yyyy')
    dob_picker.pack()

    def update_age(*args):
        dob = dob_picker.get_date()
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        age_var.set(str(age))

    dob_picker.bind("<<DateEntrySelected>>", update_age)
    update_age()

    ttk.Label(passenger_form_frame, text="Age (auto-calculated):").pack(pady=5)
    age_entry = ttk.Entry(passenger_form_frame, textvariable=age_var, justify="center", state="readonly")
    age_entry.pack()

    ttk.Label(passenger_form_frame, text="Gmail ID:").pack(pady=5)
    gmail_entry = ttk.Entry(passenger_form_frame, textvariable=gmail_var, justify="center")
    gmail_entry.pack()

    ttk.Label(passenger_form_frame, text="Gender:").pack(pady=5)
    gender_frame = ttk.Frame(passenger_form_frame)
    gender_frame.pack()
    ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left", padx=10)
    ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left", padx=10)
    ttk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other").pack(side="left", padx=10)

    ttk.Label(passenger_form_frame, text="Phone No.:").pack(pady=5)
    phone_entry = ttk.Entry(passenger_form_frame, textvariable=phone_var, justify="center")
    phone_entry.pack()

    def submit_and_next():
        update_age()

        name = name_var.get().strip()
        phone = phone_var.get().strip()
        age = age_var.get().strip()
        gmail = gmail_var.get().strip()
        gname = gmail_var.get().strip().split('@')

        if not name.replace(" ", "").isalpha():
            messagebox.showerror("Invalid Name", "Name must contain only letters and spaces.")
            return
        if not gmail or '@gmail.com' not in gmail or not gname[0]:
            messagebox.showerror("Invalid Gmail", "Enter a valid Gmail ID")
            return
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Invalid Phone Number", "Phone number must be a 10-digit number.")
            return
        if label.startswith("Child") and int(age) >= 18:
            messagebox.showerror("Invalid Age", "Child must be under 18 years old.")
            return

        passenger_entries.append((
            name,
            dob_picker.get_date().strftime("%Y-%m-%d"),  # ✅ unified format
            age,
            gmail,
            gender_var.get(),
            phone
        ))

        global current_passenger_index
        current_passenger_index += 1
        if current_passenger_index >= passenger_count:
            show_passenger_summary()
        else:
            open_individual_passenger_form()

    tk.Button(passenger_form_frame, text="Next➡️", command=submit_and_next,
              bg="#4CAF50", fg="white", font=("Helvetica", 11), width=16).pack(pady=10)
    
        # ✅ Back button
    tk.Button(passenger_form_frame, text="⬅️ Back",
              command=go_back_from_passenger_form,
              bg="#795548", fg="white", font=("Helvetica", 11), width=16).pack(pady=5)

def show_passenger_summary():
    passenger_form_frame.pack(fill="both", expand=True)
    for widget in passenger_form_frame.winfo_children():
        widget.destroy()

    # Scrollable canvas setup
    canvas = tk.Canvas(passenger_form_frame, bg="#f5f5f5")
    scrollbar = ttk.Scrollbar(passenger_form_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#f5f5f5")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Header
    tk.Label(scroll_frame, text="📝 Confirm Passenger Details", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    # Passenger cards
    for i, entry in enumerate(passenger_entries):
        card = tk.Frame(scroll_frame, bg="#ffffff", bd=2, relief="groove")
        card.config(width=720, height=240)  # ← Set the size here
        card.pack(pady=10, padx=20)
        card.pack_propagate(False)  # Prevent shrinking to fit content

        tk.Label(card, text=f"Passenger {i + 1}", font=("Helvetica", 13, "bold"), bg="#ffffff", fg="#333").pack(anchor="w", padx=10, pady=(5, 0))

        labels = ["Name", "DOB", "Age","Gmail ID", "Gender", "Phone"]
        for label, value in zip(labels, entry):
            row = tk.Frame(card, bg="#ffffff")
            row.pack(anchor="w", padx=20, pady=2)
            tk.Label(row, text=f"{label}:", font=("Helvetica", 11, "bold"), bg="#ffffff", width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Helvetica", 11), bg="#ffffff", anchor="w").pack(side="left")

        # Edit button
        tk.Button(card, text="✏️ Edit", command=lambda idx=i: edit_passenger(idx),
                  bg="#2196F3", fg="white", font=("Helvetica", 10), width=10).pack(anchor="e", padx=10, pady=5)

    # Action buttons
    button_frame = tk.Frame(scroll_frame, bg="#f5f5f5")
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="✅ Proceed to Payment", command=payment,
          bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20).pack(side="left", padx=10)

    tk.Button(button_frame, text="❌ Cancel", command=cancel_passenger_summary,
              bg="#f44336", fg="white", font=("Helvetica", 12), width=20).pack(side="left", padx=10)
    
def edit_passenger(index):
    global current_passenger_index, is_editing, backtracking
    current_passenger_index = index
    is_editing = True
    backtracking = False
    passenger_data = passenger_entries.pop(index)
    passenger_form_frame.pack_forget()
    open_individual_passenger_form(prefill=passenger_data)

def go_back_from_passenger_form():
    global current_passenger_index, is_editing, backtracking,selected_children,selected_adults

    passenger_form_frame.pack_forget()

    if current_passenger_index == 0 and not passenger_entries:
        show_passenger_list_window()
        return

    if current_passenger_index == selected_adults + selected_children :
        show_passenger_list_window()
        return

    current_passenger_index -= 1
    backtracking = True
    is_editing = False  

    if passenger_entries and current_passenger_index < len(passenger_entries):
        # Pop the last entry so user can re-edit
        passenger_data = passenger_entries.pop(current_passenger_index)
        open_individual_passenger_form(prefill=passenger_data)
    else:
        # If no entries yet, just return to selection window
        show_passenger_list_window()

def cancel_passenger_summary():
    global passenger_entries, current_passenger_index
    passenger_entries = []
    current_passenger_index = 0
    passenger_form_frame.pack_forget()
    passenger_count_frame.pack(fill="both", expand=True)

def set_last_passenger():
    global current_passenger_index
    current_passenger_index = passenger_count - 1
    open_individual_passenger_form()

def payment():
    global payment_method_frame, payment_option_frame
    passenger_form_frame.pack_forget()

    total_passengers = len(passenger_entries)
    cost_per_ticket = int(selected_flight[7])
    total_amount = total_passengers * cost_per_ticket

    method_var = tk.StringVar(value="UPI")

    # Frame 1: Payment Method Selection
    payment_method_frame = tk.Frame(root, bg="#f5f5f5")
    payment_method_frame.pack(fill="both", expand=True)

    tk.Label(payment_method_frame, text="💳 Payment", font=("Helvetica", 20, "bold"), bg="#f5f5f5").pack(pady=20)
    tk.Label(payment_method_frame, text=f"Total Amount: ₹{total_amount}", font=("Helvetica", 16), bg="#f5f5f5").pack(pady=10)
    tk.Label(payment_method_frame, text="Choose Payment Method:", font=("Helvetica", 14, "bold"), bg="#f5f5f5").pack(pady=10)

    method_frame = tk.Frame(payment_method_frame, bg="#f5f5f5")
    method_frame.pack(pady=10)

    for method in ["UPI", "Credit/Debit Card", "Internet Banking"]:
        tk.Radiobutton(method_frame, text=method, variable=method_var, value=method,
                       font=("Helvetica", 13), bg="#f5f5f5", anchor="w").pack(pady=5, anchor="w")

    def go_to_options():
        payment_method_frame.pack_forget()
        show_payment_options(method_var.get())

    tk.Button(payment_method_frame, text="Next ➡️", command=go_to_options,
              bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"), width=20).pack(pady=20)
    
    tk.Button(payment_method_frame, text="⬅️ Back ", 
          command=lambda: [payment_method_frame.pack_forget(), show_passenger_summary()],
          bg="#795548", fg="white", font=("Helvetica", 12,), width=20).pack(pady=20)

    tk.Button(payment_method_frame, text="⬅️ Cancel", command=lambda: [payment_method_frame.pack_forget(), dashboard_frame.pack(fill="both",expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 12), width=20).pack()
    

def show_payment_options(method):
    global payment_option_frame, payment_method_frame

    if payment_method_frame:
        payment_method_frame.pack_forget()

    try:
        payment_option_frame.destroy()
    except:
        pass

    payment_option_frame = tk.Frame(root, bg="#f5f5f5")
    payment_option_frame.pack(fill="both", expand=True)

    tk.Label(payment_option_frame, text=f"{method} Options", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=20)

    options = {
        "UPI": ["GPay", "PhonePe", "Paytm"],
        "Credit/Debit Card": ["Credit Card", "Debit Card"],
        "Internet Banking": ["SBI", "HDFC", "ICICI", "Axis Bank"]
    }

    default_value = options.get(method, [])[0] if options.get(method) else None
    option_var = tk.StringVar(value=default_value)

    opt_frame = tk.Frame(payment_option_frame, bg="#f5f5f5")
    opt_frame.pack()

    for opt in options.get(method, []):
        tk.Radiobutton(opt_frame, text=opt, variable=option_var, value=opt,
                       font=("Helvetica", 13), bg="#f5f5f5", anchor="w").pack(pady=5, anchor="w")

    # Refund policy display
    policy_frame = tk.Frame(payment_option_frame, bg="#f5f5f5")
    policy_frame.pack(pady=10)

    tk.Label(policy_frame, text="📜 Refund Policy", font=("Helvetica", 14, "bold"), bg="#f5f5f5").pack(anchor="w", padx=10)
    refund_text = (
        "• Cancel  1 month before: 75% refund\n"
        "• Cancel  1 week before: 50% refund\n"
        "• Cancel  72 hours before: 25% refund\n"
        "• Cancel  24 hours before: No refund"
    )
    tk.Label(policy_frame, text=refund_text, font=("Helvetica", 11), bg="#f5f5f5", justify="left", anchor="w").pack(anchor="w", padx=20)

    # Refund policy checkbox
    refund_var = tk.BooleanVar(value=False)
    tk.Checkbutton(payment_option_frame, text="I agree to the refund policy",
                   variable=refund_var, font=("Helvetica", 12), bg="#f5f5f5").pack(pady=10)

    # Confirm button (initially disabled)
    confirm_btn = tk.Button(payment_option_frame, text="✅ Confirm Payment",
                            bg="#4CAF50", fg="white", font=("Helvetica", 13, "bold"),
                            width=20, state="disabled")
    confirm_btn.pack(pady=20)

    def update_button_state(*args):
        confirm_btn.config(state="normal" if refund_var.get() else "disabled")

    refund_var.trace_add("write", update_button_state)

    def confirm_payment():
        selected_option = option_var.get()
        if not selected_option:
            messagebox.showerror("❌ Error", "Please select a payment option.")
            return
        messagebox.showinfo("✅ Payment Successful", f"Payment via {method} ({selected_option}) processed successfully.")
        payment_option_frame.pack_forget()
        save_booking()

    confirm_btn.config(command=confirm_payment)

    tk.Button(payment_option_frame, text="⬅️ Back",
              command=lambda: [payment_option_frame.pack_forget(), payment_method_frame.pack(fill="both", expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 12), width=20).pack()

def show_booking_summary():
    summary_frame = tk.Frame(root, bg="#f5f5f5")
    summary_frame.pack(fill="both", expand=True)

    tk.Label(summary_frame, text="✈️ Flight Details", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=(20, 5))
    # Flight Card (styled like search results)
    card = tk.Frame(summary_frame, bg="#ffffff", bd=1, relief="raised", width=780, height=180)
    card.pack(padx=20, pady=20)
    card.pack_propagate(False)

    top_row = tk.Frame(card, bg="#ffffff")
    top_row.pack(fill="x", padx=10, pady=(10, 5))

    tk.Label(top_row, text=f"✈️ Flight {selected_flight[0]}", font=("Helvetica", 14, "bold"),
             fg="#333", bg="#ffffff").pack(side="left")

    tk.Label(top_row, text=f"₹{selected_flight[7]}", font=("Helvetica", 14, "bold"),
             fg="#000000", bg="#ffffff").pack(side="right")

    route_frame = tk.Frame(card, bg="#ffffff")
    route_frame.pack(fill="x", padx=10, pady=5)
    route_frame.columnconfigure(0, weight=1, uniform="route")
    route_frame.columnconfigure(1, weight=1, uniform="route")
    route_frame.columnconfigure(2, weight=1, uniform="route")

    dep_block = tk.Frame(route_frame, bg="#ffffff")
    dep_block.grid(row=0, column=0, sticky="w")
    tk.Label(dep_block, text=selected_flight[1], font=("Helvetica", 14, "bold"),
             fg="#2E8B57", bg="#ffffff").pack(anchor="center")
    tk.Label(dep_block, text=selected_flight[3], font=("Helvetica", 13),
             fg="#2E8B57", bg="#ffffff").pack(anchor="center")
    tk.Label(dep_block, text=selected_flight[4], font=("Helvetica", 13),
             fg="#2E8B57", bg="#ffffff").pack(anchor="center")

    tk.Label(route_frame, text="➡️", font=("Helvetica", 30, "bold"),
             fg="#555", bg="#ffffff").grid(row=0, column=1, sticky="nsew")

    arr_block = tk.Frame(route_frame, bg="#ffffff")
    arr_block.grid(row=0, column=2, sticky="w")
    tk.Label(arr_block, text=selected_flight[2], font=("Helvetica", 14, "bold"),
             fg="#1E90FF", bg="#ffffff").pack(anchor="center")
    tk.Label(arr_block, text=selected_flight[5], font=("Helvetica", 13),
             fg="#1E90FF", bg="#ffffff").pack(anchor="center")
    tk.Label(arr_block, text=selected_flight[6], font=("Helvetica", 13),
             fg="#1E90FF", bg="#ffffff").pack(anchor="center")

    # Passenger Summary Cards
    tk.Label(summary_frame, text="👥 Passenger Details", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    canvas = tk.Canvas(summary_frame, bg="#f5f5f5")
    scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#f5f5f5")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for i, entry in enumerate(passenger_entries):
        entry = list(entry)
        entry.pop(1)
        card = tk.Frame(scroll_frame, bg="#ffffff", bd=2, relief="groove")
        card.config(width=760, height=200)
        card.pack(pady=10, padx=20)
        card.pack_propagate(False)

        tk.Label(card, text=f"Passenger {i + 1}", font=("Helvetica", 13, "bold"), bg="#ffffff", fg="#333").pack(anchor="w", padx=10, pady=(5, 0))

        labels = ["Name", "Age", "Gmail ID", "Gender", "Phone"]
        for label, value in zip(labels, entry):
            row = tk.Frame(card, bg="#ffffff")
            row.pack(anchor="w", padx=20, pady=2)
            tk.Label(row, text=f"{label}:", font=("Helvetica", 11, "bold"), bg="#ffffff", width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Helvetica", 11), bg="#ffffff", anchor="w").pack(side="left")

    # Back to Dashboard Button
    tk.Button(scroll_frame, text="⬅️ Back to Dashboard",
              command=lambda: [summary_frame.pack_forget(), dashboard_frame.pack(fill="both",expand=True)],
              bg="#604745", fg="white", font=("Helvetica", 12), width=20).pack(pady=20)
    
def save_booking():
    global selected_passenger_ids
    try:
        if not passenger_entries:
            messagebox.showerror("❌ Error", "No passenger data to save.")
            return

        flight_id = selected_flight[0]
        dep_date = selected_flight[3]
        arr_date = selected_flight[5]

        for entry in passenger_entries:
            passenger_details = read_passenger_details()
            name, dob,age, gmail, gender, phone = entry
            if not passenger_details:
               passengerID = generate_passengerID()
               write_passenger_details(logged_in_user["userID"],passengerID,[name.strip(),dob.strip(),gmail.strip(),gender.strip(),phone.strip()])
            else:
                for p_row in passenger_details:
                    if [details.strip() for details in p_row[2:]] == [name.strip(),dob.strip(),gmail.strip(),gender.strip(),phone.strip()]:
                        passengerID = p_row[1].strip()
                        break
                else:
                    passengerID = generate_passengerID()
                    write_passenger_details(logged_in_user["userID"],passengerID,[name,dob,gmail,gender,phone])

            if not os.path.exists(BOOKING_FILE):
                with open(BOOKING_FILE,"w",newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["UserID", "FlightID", "DepartureDate", "ArrivalDate","PassengerID"])
            with open(BOOKING_FILE,"a",newline="") as file:
                writer = csv.writer(file)
                writer.writerow([logged_in_user["userID"], flight_id, dep_date, arr_date,passengerID])
            align_csv(BOOKING_FILE)
            
            
        show_booking_summary()
        selected_passenger_ids = set()

    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to save booking: {e}")
    
# -------------------- Main Window Setup --------------------
root = tk.Tk()
def center_window(width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
root.title("Namma Airplane🛫")
center_window(800, 600)
root.configure(bg="#f5f5f5")

# Login frame
login_frame = tk.Frame(root, bg="#f5f5f5")
login_frame.pack(pady=10)

tk.Label(login_frame, text="Welcome to Namma Airplane", font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="#333").pack(pady=10)
tk.Button(login_frame, text="Create Account", command=create_account, width=20, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=5)
tk.Button(login_frame, text="Login", command=login, width=20, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)

dashboard_frame = tk.Frame(root, bg="#ffffff")

# 🧭 Dashboard title and buttons
tk.Label(dashboard_frame, text="🧭 Dashboard", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=40)
tk.Button(dashboard_frame, text="🔍 Book Flights", command=open_search_window,
          width=20, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)
tk.Button(dashboard_frame, text="📖 See Bookings", command=display_user_bookings,
          width=20, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=5)
tk.Button(dashboard_frame, text="🚪 Logout", command=logout,
          width=20, bg="#604745", fg="white", font=("Helvetica", 12)).pack(pady=5)

account_frame = tk.Frame(root, bg="#FFFFFF")

search_frame = tk.Frame(root, bg="#f5f5f5")

flight_frame = tk.Frame(root, bg="#f5f5f5")

passenger_count_frame = tk.Frame(root, bg="#f5f5f5")

passenger_form_frame = tk.Frame(root, bg="#f5f5f5")

payment_frame = tk.Frame(root)

# Run the application
root.mainloop()