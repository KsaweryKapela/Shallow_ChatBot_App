from flask import Flask, render_template, session, redirect, Response
from flask_session import Session
import os

KEY = os.urandom(12)
app = Flask(__name__)
app.secret_key = KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def del_used_questions(questions):
    if 'used_q' not in session:
        session['used_q'] = []

    for index in sorted(session['used_q'], reverse=True):
        del questions[index]
        
    return questions

def get_questions():
    questions = ['Yay', 'yooo', 'yupiyay', 'eyoo', 'ayayaya']
    return del_used_questions(questions)

@app.route('/')
def index():
    if len(get_questions()) == 0:
        session['used_q'] = []
    if 'using_rn' in session:
        session['used_q'].append(session.pop('using_rn'))
    
    questions = get_questions()

    if 'redirect' in session:
        del session['redirect']
        return redirect('/')
        
    return render_template('index.html', questions=questions)

@app.route('/conv<int:number>')
def conversation(number):
    question_text = get_questions()[number]
    session['using_rn'] = number
    session['redirect'] = True


    return render_template('conversation.html', number=number, question_text=question_text)

if __name__ == "__main__":
    app.run(debug=True, port=3000)