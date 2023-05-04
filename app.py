from flask import Flask, render_template, session, redirect, Response
from flask_session import Session
import os
import pandas as pd
import numpy as np

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

@app.route('/')
def index():

    if 'using_rn' in session:
        session['used_q'].append(session.pop('using_rn'))
    
    questions_all = [question[0] for question in get_questions()]

    questions = del_used_questions(questions_all)

    session['used_q'] = list(set(session['used_q']))
    print(session['used_q'])

    ## TESTING
    if len(questions) == 0:
        session['used_q'] = []
    ## TESTING
    
    return render_template('index.html', questions=questions, questions_all=questions_all)

@app.route('/conv<int:number>')
def conversation(number):
    question_all = get_questions()[number]
    question_text = question_all[0]
    question_answer = question_all[1:][~pd.isnull(question_all[1:])]
    session['using_rn'] = number

    return render_template('conversation.html', number=number, question_text=question_text, question_answer=question_answer)

if __name__ == "__main__":
    app.run(debug=True, port=5000)