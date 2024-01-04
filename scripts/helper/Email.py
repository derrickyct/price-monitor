import smtplib
from email.mime.text import MIMEText


def send_mail(sender_email, receiver_email, subject, message, password):
    # Create a MIMEText object
    msg = MIMEText(message)
    
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

