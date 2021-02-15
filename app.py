from flask import Flask, request, render_template, redirect, flash, jsonify, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = '0123456789'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


@app.route('/')
def show_select_survey():
    survey_options = surveys.surveys.keys()
    return render_template('select_survey.html', surveys=survey_options)


@app.route('/start')
def show_survey_start():
    session['survey'] = request.args['survey_selection']
    survey = surveys.surveys[session['survey']]
    session['length'] = len(survey.questions)
    title = survey.title
    instructions = survey.instructions
    return render_template('survey_start.html', title=title, instructions=instructions)


@app.route('/set-up', methods=['POST'])
def set_up_survey_session():
    session['questions'] = []
    session['responses'] = []
    return redirect(f"/questions/0")


@app.route('/questions/<number>')
def show_survey_question(number):

    number = int(number)

    if len(session['responses']) == int(session['length']):
        flash('The survey is already complete.', 'info')
        return redirect('/thank-you')

    if number != len(session['responses']):
        flash('Please answer this question.', 'error')
        return redirect(f"/questions/{len(session['responses'])}")

    survey = surveys.surveys[session['survey']]

    question = survey.questions[number]
    question_number = number+1
    question_question = question.question

    questions = session['questions']
    questions.append(question_question)
    session['questions'] = questions

    question_choices = question.choices
    question_allow_text = question.allow_text

    return render_template('question.html', number=question_number, question=question_question, choices=question_choices, allow_text=question_allow_text)


@app.route('/answer', methods=["POST"])
def process_answer():
    number = len(session['responses'])
    answer = request.form.get('answer', None)
    answer_other = request.form.get('answer_other', None)

    if answer == None:
        flash('You must select one option to continue.', 'error')
        return redirect(f"/questions/{number}")

    # if answer == 'other' and answer_other == '':
    #     flash('If you select "other" you must also enter something in the text box to continue.', 'error')
    #     return redirect(f"/questions/{number}")

    responses = session['responses']
    if answer == None:
        responses.append(answer_other)
    elif answer_other == None:
        responses.append(answer)
    else:
        if answer_other == '':
            responses.append(answer)
        else:
            responses.append(f"{answer}: {answer_other}")

    session['responses'] = responses

    number += 1
    if number == int(session['length']):
        flash('Thank you for completing our survey.', 'success')
        return redirect('/thank-you')
    else:
        return redirect(f"/questions/{number}")


@app.route('/thank-you')
def show_thank_you():
    if len(session['responses']) == int(session['length']):
        return render_template('thank_you.html')
    else:
        flash('The survey is not complete yet.  Please answer this question.', 'error')
        return redirect(f"/questions/{len(session['responses'])}")
