from flask import Flask, render_template, session, redirect, Response
from flask_session import Session
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

KEY = os.urandom(12)
app = Flask(__name__)
app.secret_key = KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def del_used_questions(questions):
    if 'used_q' not in session:
        session['used_q'] = []

    questions = np.delete(questions, session['used_q'], axis=0)

    return questions

def get_questions():
    questions = pd.read_excel('text_data.xlsx')
    questions = questions.values

    return questions

def calculate_remaining_time():
        remaining_time = session['end_time'] - datetime.now()
        minutes = (remaining_time.seconds % 3600) // 60
        seconds = remaining_time.seconds % 60

        remaining_time = minutes, seconds
        return remaining_time

@app.route('/')
def index():

    if 'loaded' in session:
        if session['first_open'] is True:
            session['end_time'] = datetime.now() + timedelta(minutes=15)
            session['first_open'] = False

        if 'using_rn' in session:
            session['used_q'].append(session.pop('using_rn'))
        
        questions_all = [question[0] for question in get_questions()]

        questions = del_used_questions(questions_all)

        session['used_q'] = list(set(session['used_q']))
        print(session['used_q'])

        if len(questions) == 0:
            session['used_q'] = []


        return render_template('index.html', questions=questions, questions_all=questions_all, remaining_time=calculate_remaining_time())

    
    elif not 'loaded' in session:
        session['loaded'] = True
        session['first_open'] = True
        return render_template('loading.html')
        

@app.route('/conv<int:number>')
def conversation(number):
    question_all = get_questions()[number]
    question_text = question_all[0]
    question_answer = question_all[1:][~pd.isnull(question_all[1:])]
    session['using_rn'] = number

    return render_template('conversation.html', number=number, question_text=question_text, question_answer=question_answer, remaining_time=calculate_remaining_time())

if __name__ == "__main__":
    app.run(debug=True, port=5000)