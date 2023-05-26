import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

app = Flask(__name__)
CORS(app)


class EmergencyContact:
    def __init__(self, name, last_name, email, relation, telephone, age):
        self.name = name
        self.last_name = last_name
        self.email = email
        self.relation = relation
        self.telephone = telephone
        self.age = age


class UserInfo:
    def __init__(self, id, name, last_name, email, age, telephone, password, emergency_contact: EmergencyContact):
        self.id = id
        self.name = name
        self.last_name = last_name
        self.email = email
        self.age = age
        self.telephone = telephone
        self.password = password
        self.emergency_contact = emergency_contact


@app.route('/bpms')
def get_bpms():
    data = get_bpm_user_info()
    return jsonify(data)

@app.route('/questions')
def questions_list():
    questions = questions_security()
    return jsonify(questions)

@app.route('/bpm/<id>')
def get_bpm(id):
    data = get_bpm_user_info_individual(id)
    return jsonify(data)


@app.route('/emergency/<email>')
def emergency_id(email):
    emergency(email)
    return jsonify("Tu contacto de emergencia ha sido notificado")


@app.route('/users/login', methods=['POST'])
def log_in_user():
    try:
        data = request.json['user']
        email, password = data['email'], data['password']
        user = log_user(email, password)
        return jsonify(user_info_to_dict(user))
    except Exception as e:
        return jsonify("{}".format(str(e))), 409


@app.route('/users/all')
def users_all():
    return jsonify(all_users())


@app.route('/users/', methods=['POST'])
def sav_user():
    try:
        data = request.json['user']
        emergency_contact = EmergencyContact(
            name=data['emergencyContact']['name'],
            last_name=data['emergencyContact']['lastName'],
            email=data['emergencyContact']['email'],
            relation=data['emergencyContact']['relation'],
            telephone=data['emergencyContact']['telephone'],
            age=data['emergencyContact']['age']
        )
        user_info = UserInfo(
            id=data['id'],
            name=data['name'],
            last_name=data['lastName'],
            email=data['email'],
            age=data['age'],
            telephone=data['telephone'],
            password=data['password'],
            emergency_contact=emergency_contact
        )
        result = save_user(user_info)
        converted = user_info_to_dict(result)
        return jsonify(converted)
    except Exception as e:
        return jsonify("{}".format(str(e))), 409


def user_info_to_dict(user_info: UserInfo):
    return {
        "id": user_info.id,
        "last_name": user_info.last_name,
        "email": user_info.email,
        "age": user_info.age,
        "telephone": user_info.telephone,
        "password": user_info.password,
        "e_name": user_info.emergency_contact.name,
        "e_last_name": user_info.emergency_contact.last_name,
        "e_email": user_info.emergency_contact.email,
        "e_relation": user_info.emergency_contact.relation,
        "e_telephone": user_info.emergency_contact.telephone,
        "e_age": user_info.emergency_contact.age
    }


emergency_contact = EmergencyContact(
    "Valentina", "Villadiego", "valentinavilladiego214@gmail.com", "Relation", "1234567890", 30)
user_info_list = [
    UserInfo(str(uuid.uuid4()), "Brianda", "Díaz", "bri.diaz.5425@gmail.com",
             32, "3214764278", "1234abcd", emergency_contact),
    UserInfo(str(uuid.uuid4()), "Valentina", "Villadiego", "valentinavilladiego214@gmail.com",
             33, "3108803795", "1234abcd", emergency_contact),
    UserInfo(str(uuid.uuid4()), "Gustavo", "Tamara", "gustavoandrestamara@gmail.com",
             34, "3156600573", "1234abcd", emergency_contact),
    UserInfo(str(uuid.uuid4()), "Laura", "Olivella", "olivellaura17@gmail.com",
             34, "3153845242", "1234abcd", emergency_contact)]


def create_user(user_info):
    user_info.id = str(uuid.uuid4())
    user_info_list.append(user_info)
    return user_info


def all_users():
    data = []
    for user in user_info_list:
        data.append({"email": user.email, "password": user.password,
                    "full_name": user.name + " " + user.last_name, "emergency_contact": user.emergency_contact.name + " " + user.emergency_contact.last_name})

    return data


def log_user(email, password):
    if email == None or email == "" or password == None or password == "":
        raise Exception("El email y contraseña son obligatorios")
    user_found_by_email = find_user_by_email(email)
    if user_found_by_email == None:
        raise Exception("Usuario con correo {} no existe".format(email))
    if user_found_by_email.password != password:
        raise Exception("Contraseña es invalida")
    return user_found_by_email


def get_bpm_user_info():
    bpms = [[79, 78, 85, 79, 82, 74, 81, 78, 74, 74, 83, 70, 79, 78, 85, 79, 82, 74], [71, 72, 72, 72, 73, 75, 71, 65, 77, 75, 68, 72, 63, 61, 56, 66, 67, 76, 71, 77, 68, 64, 75, 54, 64, 68, 64, 63, 62, 72, 62, 67, 61, 69, 62, 75, 65, 66, 71, 65, 64, 64, 60, 81, 72, 75, 66, 73, 68, 63, 67, 63, 67, 79, 55, 86, 69, 84, 65, 62, 57, 78, 61, 65, 70, 65, 76, 67, 71, 80, 71, 68, 72, 72, 74, 62, 58, 81, 71, 83, 59, 90, 73, 80, 78, 101, 79, 70, 70, 78, 81, 75, 77, 73, 53, 74, 69, 60, 88, 68, 67, 50],
            [64, 69, 70, 73, 64, 84, 118, 148, 160, 101, 144, 85, 74, 75, 77, 72, 72, 79, 67, 61, 68, 67, 78, 76, 73, 68, 71, 65, 74, 69, 70, 70, 62, 63, 67, 70, 70, 66, 68, 65, 68, 70, 69, 75, 79, 92, 99, 105, 97, 100, 87, 96, 84, 94, 72, 91, 74, 75,
            71, 67, 71, 78, 71, 72, 68, 65, 76, 81, 63, 64, 80, 72, 70, 74, 77, 64, 69, 67, 67, 74, 75, 76, 67, 76, 68, 75, 75, 76, 68, 68, 82, 69, 70, 80, 88, 101, 87, 109, 94, 105, 92, 94, 86, 67, 75, 88, 89, 73, 54, 66, 70, 101, 60, 49, 57, 66],
            [71, 72, 72, 72, 73, 75, 71, 65, 77, 75, 68, 72, 63, 61, 56, 66, 67, 76, 71, 77, 68, 64, 75, 54, 64, 68, 64, 63, 62, 72, 62, 67, 61, 69, 62, 75, 65, 66, 71, 65, 64, 64, 60, 81, 72, 75, 66, 73, 68, 63, 67, 63, 67, 79, 55, 86, 69, 84, 65, 62, 57, 78, 61, 65, 70, 65, 76, 67, 71, 80, 71, 68, 72, 72, 74, 62, 58, 81, 71, 83, 59, 90, 73, 80, 78, 101, 79, 70, 70, 78, 81, 75, 77, 73, 53, 74, 69, 60, 88, 68, 67, 50]]
    contador = 0
    data = []
    # user.id, user.email, bpms[contador]
    for user in user_info_list:
        data.append({"id": user.id, "email": user.email,
                    "bpms": bpms[contador],  "avg": sum(bpms[contador]) / len(bpms[contador])})
        contador = contador + 1
    return data


def get_bpm_user_info_individual(user_id):
    full_data = get_bpm_user_info()
    for bpm in full_data:
        if bpm["email"] == user_id:
            return bpm
    return ""
# create read update and delete storage


def read_all_users():
    return user_info_list


def read_user_by_id(user_id):
    for user_info in user_info_list:
        if user_info.id == user_id:
            return user_info
    return None


def update_user_by_id(user_id, new_user_info: UserInfo):
    for i in range(len(user_info_list)):
        if user_info_list[i].id == user_id:
            user_info_list[i] = new_user_info
            return True
    return False


def delete_user_by_id(user_id):
    for user_info in user_info_list:
        if user_info.id == user_id:
            user_info_list.remove(user_info)
            return True
    return False


def find_user_by_email(email):
    for user_info in user_info_list:
        if user_info.email == email:
            return user_info
    return None


def save_user(user):
    userFound = find_user_by_email(user.email)
    if userFound != None:
        raise Exception(
            "Ya hay un usuario con este correo registrado {}".format(user.email))
    create_user(user)
    return user


def questions_security():
    questions = ["¿Se está realizando alguna actividad física?",
                 "¿Se está en reposo?", "¿Presenta Mareo, Fatiga, Sudoración? "]
    return questions


def emergency(email):
    user = find_user_by_email(email)
    if user == None:
        raise Exception("Usuario con correo {} no existe".format(email))
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'heartguardian0@gmail.com'
    smtp_password = 'saxjvldlciqdyubh'

    sender = 'heartguardian0@gmail.com'
    recipient = user.emergency_contact.email

    subject = 'Alerta Heart Guardian - Notificación de Emergencia'
    message = '{} {} probablemente se encuentra en una emergencia. ¿Podrías asegurarte que esté bien?. Este es su número de teléfono:  {}'.format(
        user.name, user.last_name, user.telephone)

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        print('Email sent successfully!')


if __name__ == "__main__":
    app.run(debug=True)
