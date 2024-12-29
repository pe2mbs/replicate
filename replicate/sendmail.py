import email.utils
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from replicate.config import ISmtpMail


def send_email( subject: str, text: str, smtp: ISmtpMail, logger ):
    if smtp.port in (465, 587):
        context = ssl.create_default_context()

    else:
        context = None

    try:
        def do_login():
            if hasattr( smtp, 'username' ):
                username = smtp.username
            else:
                username = smtp.sender

            if hasattr( smtp, 'password' ):
                server.login( username, smtp.password )

            return

        message = MIMEMultipart( "alternative" )
        message[ "Subject" ] = subject
        message[ "From" ] = smtp.sender
        message[ "To" ] = smtp.receiver
        message[ 'Date' ] = email.utils.formatdate()
        message[ 'Message-ID' ] = email.utils.make_msgid( domain = '[autodetect_domain]' )
        message.attach( MIMEText( text, "plain" ) )
        html = "<html><body><pre>{}</pre></body></html>".format( '<br>'.join( text.split('\n') ) )
        message.attach( MIMEText( html, "html" ) )
        if smtp.port == 465:
            with smtplib.SMTP_SSL( smtp.host, smtp.port, context = context ) as server:
                do_login()
                server.sendmail( smtp.sender, smtp.receiver, message.as_string() )

        elif smtp.port == 587:
            with smtplib.SMTP( smtp.host, smtp.port ) as server:
                server.ehlo()  # Can be omitted
                server.starttls( context = context )  # Secure the connection
                server.ehlo()  # Can be omitted
                do_login()
                server.sendmail( smtp.sender, smtp.receiver, message.as_string() )

        else:
            # Plain text
            with smtplib.SMTP( smtp.host, smtp.port ) as server:
                server.ehlo()  # Can be omitted
                do_login()
                server.sendmail( smtp.sender, smtp.receiver, message.as_string() )

    except Exception:           # noqa
        logger.exception( "During sending email" )

    return
