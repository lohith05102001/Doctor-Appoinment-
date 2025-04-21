import os
import datetime

from bson import ObjectId
from flask import Flask, request, render_template, redirect, session

import pymongo

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT_LAB_TEST = APP_ROOT + "/static/doctor"

app = Flask(__name__)
app.secret_key = "doctor"

Doctor_Appointment = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = Doctor_Appointment["New_Doctor_Appointment"]
admin_collection = my_database["admin"]
hospitals_collection = my_database["hospitals"]
doctor_collection = my_database["doctor"]
time_slots_collection = my_database["slots"]
patient_collection = my_database["patient"]
appointment_collection = my_database["appointment"]
payment_collection = my_database["payment"]
prescription_collection = my_database["prescription"]
diagnostics_report_collection = my_database["diagnostics_report"]

query = {}
count = admin_collection.count_documents({})
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session["admin_id"] = str(admin['_id'])
        session["role"] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/hospital_login")
def hospital_login():
    return render_template("hospital_login.html")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_view_hospitals")
def add_view_hospitals():
    query = {}
    hospitals = hospitals_collection.find(query)
    return render_template("add_view_hospitals.html", hospitals=hospitals)



@app.route("/view_hospitals")
def view_hospitals():
    query = {}
    hospitals = hospitals_collection.find(query)
    return render_template("view_hospitals.html", hospitals=hospitals)


@app.route("/view_doctors")
def view_doctors():
    hospital_id = request.args.get("hospitals_id")
    query = {"hospital_id": ObjectId(hospital_id)}
    doctors = doctor_collection.find(query)
    return render_template("view_book_doctor_appointment.html", doctors=doctors)


@app.route("/add_hospital_action", methods=["post"])
def add_hospital_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    state = request.form.get("state")
    city = request.form.get("city")
    zip_code = request.form.get("zip_code")
    location = request.form.get("location")
    speciality = request.form.get("speciality")
    registered_date = datetime.datetime.now()
    query = {"email": email, "phone": phone}
    count = hospitals_collection.count_documents(query)
    if count == 0:
        query = {"first_name": first_name,"last_name":last_name, "email": email, "phone": phone, "password": password, "state": state, "city": city,"registered_date":registered_date,"is_logged": False,
                 "zip_code": zip_code, "location": location, "speciality": speciality}
        hospitals_collection.insert_one(query)
        return render_template("message_action.html", message="Hospital Details Entered Successfully")
    else:
        return render_template("message_action.html", message="Invalid Login details")


@app.route("/hospital_login_action",methods=['post'])
def hospital_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = hospitals_collection.count_documents(query)
    if count > 0:
        hospital = hospitals_collection.find_one(query)
        if hospital['is_logged']:
            session['hospital_id'] = str(hospital['_id'])
            session['role'] = "hospital"
            return redirect("/hospital_home")
        else :
            session["hospital_id"] = str(hospital['_id'])
            session["role"] = "hospital"
            return redirect("/change_password")
    else:
        return render_template("message.html", message="Invalid Login Details")



@app.route("/change_password")
def change_password():
    return render_template("change_password.html")



@app.route("/change_password_action",methods=['post'])
def change_password_action():
    old_password = request.form.get("old_password")
    password = request.form.get("new_password")
    password2 = request.form.get("confirm_password")
    if old_password == password2:
        return render_template("message_action.html", message="old password and new password  same")
    if password != password2:
        return render_template("message_action.html", message="password and confirm password must be same")
    query ={"$set":{"password":password,"is_logged":True}}
    hospitals_collection.update_one({"_id":ObjectId(session['hospital_id'])},query)
    session['hospital_id'] = str(session['hospital_id'])
    return redirect("/hospital_home")



@app.route("/hospital_home")
def hospital_home():
    return render_template("hospital_home.html")


@app.route("/doctor_login")
def doctor_login():
    hospitals = hospitals_collection.find()
    return render_template("doctor_login.html",hospitals=hospitals)


@app.route("/doctor_registration_action",methods=['post'])
def doctor_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email_1")
    password = request.form.get("password_1")
    phone = request.form.get("phone")
    address = request.form.get("address")
    qualification = request.form.get("qualification")
    hospital_id = request.form.get("hospital_id")
    zip_code = request.form.get("zip_code")
    city = request.form.get("city")
    dob = request.form.get("dob")
    specialization = request.form.get("specialization")
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = doctor_collection.count_documents(query)
    if count == 0:
        query = {"first_name": first_name,"last_name":last_name, "email": email, "password": password, "phone": phone, "address": address,"qualification":qualification,"hospital_id":ObjectId(hospital_id),
                 "specialization":specialization,"status": 'Not Verified',"zip_code":zip_code,"city":city,"dob":dob}
        doctor_collection.insert_one(query)
        return render_template("message.html", message="Doctor Registered Successfully")
    else:
        return render_template("message.html", message="Duplicate Entry")


@app.route("/doctor_login_action",methods=['post'])
def doctor_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = doctor_collection.count_documents(query)
    if count > 0:
        doctor = doctor_collection.find_one(query)
        if doctor["status"] == 'Not Verified':
            return render_template("message.html", message="Your Account Not Verified")
        else:
            session['doctor_id'] = str(doctor['_id'])
            session['role'] = "doctor"
            return redirect("/doctor_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/view_verify_doctors")
def view_verify_doctors():
    hospital_id = session['hospital_id']
    query = {"hospital_id": ObjectId(hospital_id)}
    doctors = doctor_collection.find(query)
    return render_template("view_verify_doctors.html",doctors=doctors)


@app.route("/verify_doctor")
def verify_doctor():
    doctor_id = request.args.get("doctor_id")
    query1 = {"_id": ObjectId(doctor_id)}
    query2 = {"$set": {"status": "Verified"}}
    doctor_collection.update_one(query1, query2)
    return redirect("/view_verify_doctors")


@app.route("/de_verify_doctor")
def de_verify_doctor():
    doctor_id = request.args.get("doctor_id")
    query1 = {"_id": ObjectId(doctor_id)}
    query2 = {"$set": {"status": "Not Verified"}}
    doctor_collection.update_one(query1, query2)
    return redirect("/view_verify_doctors")


@app.route("/doctor_home")
def doctor_home():
    return render_template("doctor_home.html")


@app.route("/add_view_doctor_timings")
def add_view_doctor_timings():
    doctors = doctor_collection.find()
    return render_template("add_view_doctor_timings.html",doctors=doctors,formate_time=formate_time,formate_time2=formate_time2)


@app.route("/add_view_doctor_timings_action",methods=['post'])
def add_view_doctor_timings_action():
    doctor_id = session["doctor_id"]
    from_time = request.form.get("from_time")
    from_time2 = datetime.datetime.strptime(from_time, "%H:%M")
    to_time = request.form.get("to_time")
    to_time2 = datetime.datetime.strptime(to_time, "%H:%M")
    doctor = doctor_collection.find_one({})
    doctor_collection.count_documents(doctor)
    day = request.form.get("day")
    query = {"_id": ObjectId(doctor_id), "timings.day": day}
    count = doctor_collection.count_documents(query)
    if count > 0:
        query1 = {"_id": ObjectId(doctor_id)}
        query2 = {"$pull": {"timings": {"day": day}}}
        doctor_collection.update_one(query1, query2)
        # query3 = {"doctor_id": ObjectId(doctor_id)}
        # time_slots_collection.delete_many(query3)

    query = {"$push": {"timings": {"from_time": from_time, "to_time": to_time, "day": day}}}
    doctor_collection.update_one({"_id": ObjectId(doctor_id)}, query)
    doctor_id = ObjectId(session['doctor_id'])
    query = {"doctor_id": ObjectId(doctor_id), "day": day}
    count = time_slots_collection.count_documents(query)
    if count > 0:
        query2 = {"doctor_id": ObjectId(doctor_id), "day": day}
        time_slots_collection.delete_many(query2)
    slot_number = 0
    while from_time2 < to_time2:
        slot_from_time = from_time2
        slot_from_time = slot_from_time.strftime("%H:%M")
        from_time2 = from_time2 + datetime.timedelta(minutes=15)
        slot_to_time = from_time2
        slot_to_time = slot_to_time.strftime("%H:%M")
        slot_number = slot_number + 1
        slot = {"slot_from_time": slot_from_time, "slot_to_time": slot_to_time, "slot_number": slot_number,
                "doctor_id": doctor_id, "day": day}

        time_slots_collection.insert_one(slot)

        next_slot_to_time = from_time2 + datetime.timedelta(minutes=15)
        if next_slot_to_time > to_time2:
            break
    return redirect("/add_view_doctor_timings")


def formate_time(time):
    print(time)
    date = datetime.datetime.strptime(str(datetime.datetime.now().date())+" "+time,"%Y-%m-%d %H:%M")
    time = str(date.strftime("%I"))+":"+str(date.strftime("%M"))+" "+str(date.strftime("%p"))
    return time

def formate_time2(time):
    date = datetime.datetime.strptime(str(datetime.datetime.now().date())+" "+time,"%Y-%m-%d %H:%M")
    time = str(date.strftime("%I"))+":"+str(date.strftime("%M"))+" "+str(date.strftime("%p"))
    return time


@app.route("/consultant_fee_action")
def consultant_fee_action():
    consultant_fee = request.args.get("consultant_fee")
    doctor_id = request.args.get("doctor_id")
    print(consultant_fee)
    query = {"$set": {"consultant_fee":consultant_fee}}
    doctor_collection.update_one({"_id": ObjectId(doctor_id)}, query)
    return redirect("/view_verify_doctors")


@app.route("/patient_login")
def patient_login():
    return render_template("patient_login.html")


@app.route("/patient_login_action", methods=['post'])
def patient_login_action():
    user_login = request.form.get("user_login")
    password = request.form.get("password")
    query = {"$or":[{"email": user_login}, {"name": user_login}], "password": password}
    count = patient_collection.count_documents(query)
    if count > 0:
        patient = patient_collection.find_one(query)
        session['patient_id'] = str(patient['_id'])
        session['role'] = "patient"
        return redirect("/patient_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/patient_registration_action", methods=['post'])
def patient_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email_1")
    phone = request.form.get("phone")
    address = request.form.get("address")
    zip_code = request.form.get("zip_code")
    gender = request.form.get("gender")
    dob = request.form.get("dob")
    insurance = request.form.get("insurance")
    password = request.form.get("password_1")
    password2 = request.form.get("confirm_password")
    if password != password2:
        return render_template("message_action.html", message="password and confirm password must be same")
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = patient_collection.count_documents(query)
    if count == 0:
        query = {"first_name":first_name,"last_name":last_name,"email": email, "password": password, "phone": phone,"address":address,"zip_code":zip_code,"gender":gender,"dob":dob,"insurance":insurance}
        patient_collection.insert_one(query)
        return render_template("message.html", message="Patient Registered Successfully")
    else:
        return render_template("message.html", message="Duplicate Entry")


@app.route("/patient_home")
def patient_home():
    return render_template("patient_home.html")


@app.route("/view_book_doctor_appointment")
def view_book_doctor_appointment():
    doctors= doctor_collection.find()
    return render_template("view_book_doctor_appointment.html",doctors=doctors)


@app.route("/doctor_slots")
def doctor_slots():
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    doctor_id = request.args.get("doctor_id")
    query = {"_id": ObjectId(doctor_id)}
    doctor = doctor_collection.find_one(query)
    print(doctor_id)
    appointment_date = request.args.get("appointment_date")
    if appointment_date == None:
        date_time = datetime.datetime.today()
        day = date_time.weekday()
        appointment_date = str(date_time.strftime('%Y-%m-%d'))
        appointment_date2 = datetime.date.today()
    else:
        appointment_date2 = appointment_date
        appointment_date = datetime.datetime.strptime(appointment_date, '%Y-%m-%d')
        day = appointment_date.weekday()
        appointment_date = str(appointment_date)
    day = weekdays[day]
    query = {"day": day,"doctor_id": ObjectId(doctor_id)}
    slots = time_slots_collection.find(query)
    return render_template("doctor_slots.html", doctor=doctor, slots=slots, doctor_id=doctor_id,
                           appointment_date=appointment_date, appointment_date2=appointment_date2,
                           is_slot_booked=is_slot_booked,formate_time=formate_time,formate_time2=formate_time2)


def is_slot_booked(slot_id, appointment_date):
    if " " not in appointment_date:
        appointment_date += " 00:00:00"
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d %H:%M:%S")
    query = {"slot_id": ObjectId(slot_id), "appointment_date": appointment_date, "status": 'Appointment Booked'}
    count = appointment_collection.count_documents(query)
    if count == 0:
        return False
    else:
        return True


@app.route("/description")
def description():
    doctor_id = request.args.get("doctor_id")
    appointment_date = request.args.get("appointment_date")
    slot_id = request.args.get("slot_id")
    return render_template("description.html", doctor_id=doctor_id, appointment_date=appointment_date, slot_id=slot_id)


@app.route("/request_doctor")
def request_doctor():
    doctor_id = request.args.get("doctor_id")
    appointment_date = request.args.get("appointment_date")
    slot_id = request.args.get("slot_id")
    description = request.args.get("description")
    doctor = doctor_collection.find_one()
    patient = patient_collection.find_one({"_id":ObjectId(session['patient_id'])})
    return render_template("payment.html",patient=patient,doctor_id=doctor_id,appointment_date=appointment_date,slot_id=slot_id,description=description,doctor=doctor)



@app.route("/payment_action", methods=['post'])
def payment_action():
    doctor_id = request.form.get("doctor_id")
    appointment_date = request.form.get("appointment_date")
    amount = request.form.get("amount")
    slot_id = request.form.get("slot_id")
    card_type = request.form.get("card_type")
    card_number = request.form.get("card_number")
    name_on_card = request.form.get("name_on_card")
    cvv = request.form.get("cvv")
    description = request.form.get("description")
    expiry_date = request.form.get("expiry_date")
    patient_id = ObjectId(session['patient_id'])
    query = {"doctor_id": ObjectId(doctor_id), "appointment_date": appointment_date, "slot_id": ObjectId(slot_id),
             "description": description, "status": 'Appointment Booked', "patient_id": patient_id}
    result =appointment_collection.insert_one(query)
    appointment_id = result.inserted_id
    query2 = {"appointment_id": ObjectId(appointment_id), "patient_id": patient_id, "amount": amount,
             "card_type": card_type, "card_number": card_number, "name_on_card": name_on_card, "cvv": cvv,
             "expiry_date": expiry_date, "status": 'Payment Successfully'}
    payment_collection.insert_one(query2)
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Appointment Booked"}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Payment Successfully")



@app.route("/payment_action2", methods=['post'])
def payment_action2():
    doctor_id = request.form.get("doctor_id")
    appointment_date = request.form.get("appointment_date")
    print(appointment_date)
    amount = request.form.get("amount")
    slot_id = request.form.get("slot_id")
    insurance_number = request.form.get("insurance_number")
    insurance_type = request.form.get("insurance_type")
    insurance_company_name = request.form.get("insurance_company_name")
    description = request.form.get("description")
    patient_id = ObjectId(session['patient_id'])
    query = {"doctor_id": ObjectId(doctor_id), "appointment_date": appointment_date, "slot_id": ObjectId(slot_id),
             "description": description, "status": 'Appointment Booked', "patient_id": patient_id,"insurance_company_name":insurance_company_name,"insurance_type":insurance_type,"insurance_number":insurance_number}
    result =appointment_collection.insert_one(query)
    appointment_id = result.inserted_id
    query2 = {"appointment_id": ObjectId(appointment_id), "patient_id": patient_id, "amount": amount,
             "insurance_number": insurance_number, "status": 'Payment Successfully'}
    payment_collection.insert_one(query2)
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Appointment Booked"}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Payment Successfully")



@app.route("/view_bookings")
def view_bookings():

    query = {}
    # appointment_date = request.args.get("appointment_date")
    # if appointment_date == None:
    #     appointment_date = datetime.datetime.now()
    #     appointment_date = appointment_date.strftime("%Y-%m-%d")
    if session['role'] == 'patient':
        patient_id = session["patient_id"]
        query = {"patient_id": ObjectId(patient_id)}
    elif session['role'] == 'doctor':
        doctor_id = session["doctor_id"]
        slot_id = request.args.get("slot_id")
        if slot_id == None:
            query = {"doctor_id": ObjectId(doctor_id)}
            slots = time_slots_collection.find(query)
            slot_ds = []
            for slot in slots:
                slot_ds.append({'slot_id':ObjectId(slot['_id'])})
            query = {"$or":slot_ds}
        else:
            query = {"slot_id": ObjectId(slot_id)}
    elif session['role'] == 'admin':
        query = {}
    appointments = appointment_collection.find(query).sort([('appointment_date', pymongo.ASCENDING)])
    return render_template("view_bookings.html", appointments=appointments,
                           get_doctor_by_doctor_id=get_doctor_by_doctor_id,
                           get_patient_by_patient_id=get_patient_by_patient_id, get_slot_by_slot_id=get_slot_by_slot_id,
                           get_payment_by_appointment_id=get_payment_by_appointment_id, formate_time=formate_time)


def get_doctor_by_doctor_id(doctor_id):
    query = {"_id": doctor_id}
    doctor = doctor_collection.find_one(query)
    return doctor


def get_patient_by_patient_id(patient_id):
    query = {"_id": patient_id}
    patient = patient_collection.find_one(query)
    return patient


def get_slot_by_slot_id(slot_id):
    query = {"_id": slot_id}
    slot = time_slots_collection.find_one(query)
    return slot


def get_payment_by_appointment_id(appointment_id):
    query = {"appointment_id": ObjectId(appointment_id)}
    payment = payment_collection.find_one(query)
    return payment


@app.route("/approve")
def approve():
    appointment_id = request.args.get("appointment_id")
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Appointment Approved"}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Request Accepted")


@app.route("/reject")
def reject():
    appointment_id = request.args.get("appointment_id")
    return render_template("reject.html", appointment_id=appointment_id)


@app.route("/send_reason")
def send_reason():
    reason = request.args.get("reason")
    appointment_id = request.args.get("appointment_id")
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": 'Request Rejected', "reason": reason}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Request Rejected")


@app.route("/cancel_appointment")
def cancel_appointment():
    appointment_id = request.args.get("appointment_id")
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": 'Appointment Cancelled'}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Appointment Cancelled")

@app.route("/view_reason")
def view_reason():
    appointment_id = request.args.get("appointment_id")
    appointments = appointment_collection.find()
    return render_template("view_reason.html", appointment_id=appointment_id, appointments=appointments)


@app.route("/prescription")
def prescription():
    appointment_id = request.args.get("appointment_id")
    return render_template("prescription.html", appointment_id=appointment_id)


@app.route("/write_diagnostics")
def write_diagnostics():
    appointment_id = request.args.get("appointment_id")
    return render_template("write_diagnostics.html", appointment_id=appointment_id)

@app.route("/submit_prescription")
def submit_prescription():
    appointment_id = request.args.get("appointment_id")
    prescription = request.args.get("prescription")
    prescribed_date1: datetime.date = datetime.date.today()
    prescribed_date = datetime.datetime.strptime(str(prescribed_date1), "%Y-%m-%d")
    # prescriptionValidFromDate = datetime.date.today()
    # prescriptionValidToDate = prescriptionValidFromDate + datetime.timedelta(days=15)
    # prescriptionValidFromDate2 = datetime.datetime.strptime(str(prescriptionValidFromDate), "%Y-%m-%d")
    # prescriptionValidToDate2 = datetime.datetime.strptime(str(prescriptionValidToDate), "%Y-%m-%d")
    query = {"appointment_id": ObjectId(appointment_id), "prescription": prescription,"prescribed_date":prescribed_date}
             # "prescriptionValidFromDate": prescriptionValidFromDate2,
             # "prescriptionValidToDate": prescriptionValidToDate2}
    prescription_collection.insert_one(query)
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Prescribed"}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Prescription sent Successfully")



@app.route("/submit_diagnostics_report")
def submit_diagnostics_report():
    appointment_id = request.args.get("appointment_id")
    diagnostics_report = request.args.get("diagnostics_report")
    diagnostics_report_date1: datetime.date = datetime.date.today()
    diagnostics_report_date = datetime.datetime.strptime(str(diagnostics_report_date1), "%Y-%m-%d")
    # prescriptionValidFromDate = datetime.date.today()
    # prescriptionValidToDate = prescriptionValidFromDate + datetime.timedelta(days=15)
    # prescriptionValidFromDate2 = datetime.datetime.strptime(str(prescriptionValidFromDate), "%Y-%m-%d")
    # prescriptionValidToDate2 = datetime.datetime.strptime(str(prescriptionValidToDate), "%Y-%m-%d")
    query = {"appointment_id": ObjectId(appointment_id), "diagnostics_report": diagnostics_report,"diagnostics_report_date":diagnostics_report_date}
             # "prescriptionValidFromDate": prescriptionValidFromDate2,
             # "prescriptionValidToDate": prescriptionValidToDate2}
    diagnostics_report_collection.insert_one(query)
    query1 = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Diagnostic Reported"}}
    appointment_collection.update_one(query1, query2)
    return render_template("message_action.html", message="Prescription sent Successfully")


@app.route("/view_prescription")
def view_prescription():
    appointment_id = request.args.get("appointment_id")
    prescriptions = prescription_collection.find({"appointment_id": ObjectId(appointment_id)})
    return render_template("view_prescription.html", prescriptions=prescriptions)


@app.route("/view_diagnostics_report")
def view_diagnostics_report():
    appointment_id = request.args.get("appointment_id")
    diagnostics_reports = diagnostics_report_collection.find({"appointment_id": ObjectId(appointment_id)})
    return render_template("view_diagnostics_report.html", diagnostics_reports=diagnostics_reports)


@app.route("/payment")
def payment():
    doctor = doctor_collection.find_one()
    appointment_id = request.args.get("appointment_id")
    return render_template("payment.html", appointment_id=appointment_id,doctor=doctor)


#
# @app.route("/payment_action", methods=['post'])
# def payment_action():
#     patient_id = session['patient_id']
#     appointment_id = request.form.get("appointment_id")
#     amount = request.form.get("amount")
#     card_type = request.form.get("card_type")
#     card_number = request.form.get("card_number")
#     name_on_card = request.form.get("name_on_card")
#     cvv = request.form.get("cvv")
#     expiry_date = request.form.get("expiry_date")
#     query = {"appointment_id": ObjectId(appointment_id), "patient_id": ObjectId(patient_id), "amount": amount,
#              "card_type": card_type, "card_number": card_number, "name_on_card": name_on_card, "cvv": cvv,
#              "expiry_date": expiry_date, "status": 'Payment Successfully'}
#     payment_collection.insert_one(query)
#     query1 = {"_id": ObjectId(appointment_id)}
#     query2 = {"$set": {"status": "Appointment Completed"}}
#     appointment_collection.update_one(query1, query2)
#     return render_template("message_action.html", message="Payment Successfully")
#


app.run(debug=True)
