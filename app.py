from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    questions = ['Yay', 'yooo', 'yupiyay', 'eyoo', 'ayayaya']
    return render_template('index.html', questions=questions)

@app.route('/conv<number>')
def conversation(number):
    return render_template('conversation.html', number=number)

if __name__ == "__main__":
    app.run(debug=True, port=3000)