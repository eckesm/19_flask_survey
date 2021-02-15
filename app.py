from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = '0123456789'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

survey = surveys.satisfaction_survey
responses = []


@app.route('/')
def show_survey_start():
    title = survey.title
    instructions = survey.instructions
    return render_template('survey_start.html', title=title, instructions=instructions)


@app.route('/questions/<number>')
def show_survey_question(number):

    if len(responses) == len(survey.questions):
        flash('The survey is complete.', 'info')
        return redirect('/thank-you')

    number = int(number)
    if number != len(responses):
        flash('Please answer this question.', 'info')
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[number]
    question_number = number+1
    question_question = question.question
    question_choices = question.choices
    return render_template('question.html', number=question_number, question=question_question, choices=question_choices)


@app.route('/answer', methods=["POST"])
def process_answer():
    number = int(request.form['number'])
    answer = request.form.get('answer', None)

    if answer == None:
        flash('You must select one option to continue.', 'error')
        return redirect(f"/questions/{number-1}")

    responses.append(answer)
    survey_len = len(survey.questions)

    if number == survey_len:
        flash('Thank you for completing our survey.', 'success')
        return redirect('/thank-you')
    else:
        return redirect(f"/questions/{number}")


@app.route('/thank-you')
def show_thank_you():
    return render_template('thank_you.html')
