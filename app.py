from flask import Flask, render_template, session, redirect, Response, make_response, request
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

        if remaining_time.total_seconds() < 0:
            session['endtime'] = True
            minutes = 00
            seconds = 00
        
        else:
            minutes = (remaining_time.seconds % 3600) // 60
            seconds = remaining_time.seconds % 60

        remaining_time = minutes, seconds
        return remaining_time

def check_if_over():
    if (session['end_time'] - datetime.now()).total_seconds() < 0:
        session['used_q'] = range(0, 17)
        return True
    else:
        return False

@app.route('/<string:variant>')
def variant(variant):
    if 'variant' in session:
        return redirect('/')
    else:
        session['variant'] = variant
        return redirect('/')
    
    
@app.route('/')
def index():
    print(session)
    if 'loaded' in session:
        if session['first_open'] is True:
            session['end_time'] = datetime.now() + timedelta(minutes=15)
            session['first_open'] = False

        if 'using_rn' in session:
            session['used_q'].append(session.pop('using_rn'))
        
        questions_all = [question[0] for question in get_questions()]

        questions = del_used_questions(questions_all)

        session['used_q'] = list(set(session['used_q']))

        session.pop('page_reloaded', None)
        print(session)

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
    session['used_q'].append(session.pop('using_rn'))
    return render_template('conversation.html', number=number, question_text=question_text, question_answer=question_answer, remaining_time=calculate_remaining_time())

@app.route('/leave')
def leave():

    if 'endtime' in session:
        endtime = True
    else:
        endtime = False

    min, sec = calculate_remaining_time()
    code = f'{min + 12}x{len(session["used_q"])}{session["variant"]}y{sec + 13}'
    if session['variant'] == 'r':
        link = 'https://ipsuj.qualtrics.com/jfe/form/SV_20uCWlOx3R5KeiO'
    elif session['variant'] == 'h':
        link = 'https://ipsuj.qualtrics.com/jfe/form/SV_8e9J8IiSn8pnFc2'
    elif session['variant'] == 't':
        link = 'https://ipsuj.qualtrics.com/jfe/form/SV_20uCWlOx3R5KeiO'
    elif session['variant'] == 'p':
        link = 'https://ipsuj.qualtrics.com/jfe/form/SV_ahpQgPXnWS87ZfE?fbclid=IwAR1MdL_QbpRSWiTx65svCUb3bgIeocC2RODIKoBg41HlpPJJmlU1IH9BVQs'

    return render_template('leavepage.html', code=code, link=link, endtime=endtime)

if __name__ == "__main__":
    # app.run(debug=True, port='3000')
    app.run(debug=False, port='0.0.0.0')