from re import sub
from flask import (
    Blueprint, redirect, url_for, request, render_template, current_app
)

import sendgrid
from sendgrid.helpers.mail import *

from app.db import get_db
bp = Blueprint('mail', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    db, c = get_db()
    palabra_a_buscar= request.args.get('buscar')

    if not palabra_a_buscar:
        c.execute('SELECT * FROM email')

    if palabra_a_buscar:
        c.execute('SELECT * FROM email WHERE content like %s', ('%' + palabra_a_buscar + '%',))
    
    mails = c.fetchall()
    return render_template('mails/index.html', mails=mails)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method=='POST':
        email = request.form.get('email-form')
        subject = request.form.get('subject-form')
        content = request.form.get('content-form')
    
        send(email, subject, content)

        db, c = get_db()
        c.execute(
            'INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)', (email, subject, content)
        )
        db.commit()

        return redirect(url_for('mail.index'))

    return render_template('mails/create.html')


def send(email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_KEY'])
    from_email = Email(current_app.config['FROM_EMAIL'])
    to_email= To(email)
    content= Content("text/plain", content)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
