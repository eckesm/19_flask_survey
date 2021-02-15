from flask import Flask, request, render_template, redirect, flash, jsonify, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = '0123456789'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


@app.route('/')
def show_select_survey():
    """
    Show start page where user selects the survery they would like to take.  This also resets session data to start a new survey if user has already completed a survey.
    """
    session['survey']=None
    session['questions']=None
    session['responses']=None
    survey_options = surveys.surveys.keys()
    return render_template('select_survey.html', surveys=survey_options)


@app.route('/start')
def show_survey_start():
    """
    Show user information about the survey they have selected and button to take user to the first question.  This process also creates session data for the survey conent and the number of questions.
    """
    session['survey'] = request.args['survey_selection']
    survey = surveys.surveys[session['survey']]
    session['length'] = len(survey.questions)
    title = survey.title
    instructions = survey.instructions
    return render_template('survey_start.html', title=title, instructions=instructions)


@app.route('/set-up', methods=['POST'])
def set_up_survey_session():
    """
    When the user clicks the button to start the survey, this route creates session data keys for questions and responses then redirects to the first question.
    """
    session['questions'] = []
    session['responses'] = []
    return redirect(f"/questions/0")


@app.route('/questions/<int:question_id>')
def show_survey_question(question_id):
    """
    Displays questions and answers to the user.  If the user attempts to access a question out of order or to which they do not have access, the route redirects the user elsewhere.
    """
    question_id = int(question_id)
    
    if session['survey']==None or session['responses']==None:
        flash('There is no active survey.  Select a survey to answer quetions.', 'info')
        return redirect('/')

    if len(session['responses']) == int(session['length']):
        flash('The survey is already complete.', 'info')
        return redirect('/thank-you')

    if question_id != len(session['responses']):
        flash('Please answer this question.', 'error')
        return redirect(f"/questions/{len(session['responses'])}")

    survey = surveys.surveys[session['survey']]

    question = survey.questions[question_id]
    question_number = question_id+1

    session_questions = session['questions']
    session_questions.append(question.question)
    session['questions'] = session_questions

    return render_template('question.html', question=question, number=question_number)


@app.route('/answer', methods=["POST"])
def process_answer():
    """
    When an answer is submitted, this route saves the entry or tells the user if they have made a mistake.
    """
    questions_answered = len(session['responses'])
    answer = request.form.get('answer', None)
    answer_other = request.form.get('answer_other', None)

    if answer == None:
        flash('You must select one option to continue.', 'error')
        return redirect(f"/questions/{questions_answered}")

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

    questions_answered += 1
    if questions_answered == int(session['length']):
        flash('Thank you for completing our survey.', 'success')
        return redirect('/thank-you')
    else:
        return redirect(f"/questions/{questions_answered}")


@app.route('/thank-you')
def show_thank_you():
    """
    Thank the user for completing the survey.
    """
    if len(session['responses']) == int(session['length']):
        return render_template('thank_you.html')
    else:
        flash('The survey is not complete yet.  Please answer this question.', 'error')
        return redirect(f"/questions/{len(session['responses'])}")
