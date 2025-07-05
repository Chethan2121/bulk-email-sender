import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_bulk_emails(sender_email, sender_password, subject, body, recipient_list):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        for recipient in recipient_list:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server.sendmail(sender_email, recipient, msg.as_string())
            st.success(f"✅ Email sent to: {recipient}")

        server.quit()
        st.info("✅ All emails sent successfully!")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Streamlit UI
st.set_page_config(page_title="Bulk Email Sender", layout="centered")
st.title("📧 Bulk Email Sender (via Gmail)")

with st.expander("ℹ️ Where to Get Your Gmail App Password?", expanded=False):
    st.markdown("""
    **📌 Gmail App Password Instructions:**

    1. Go to [Google My Account - Security](https://myaccount.google.com/security).
    2. Enable **2-Step Verification** if not already enabled.
    3. After that, go to [App Passwords](https://myaccount.google.com/apppasswords).
    4. Select "Mail" as the app and "Other" or your device.
    5. Generate and copy the 16-character password.
    6. Use your full Gmail address and this App Password here.

    🔒 This is more secure than using your regular password.
    """)

with st.form("email_form"):
    st.subheader("🔐 Gmail Credentials")
    sender_email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    sender_password = st.text_input("App Password", type="password")

    st.subheader("✉️ Email Content")
    subject = st.text_input("Subject", placeholder="Enter the subject")
    message_body = st.text_area("Message", placeholder="Type your email message here...")

    st.subheader("📬 Recipients")
    recipients_input = st.text_area("Recipient Emails (comma-separated)", placeholder="user1@example.com, user2@example.com")

    submitted = st.form_submit_button("🚀 Send Emails")

    if submitted:
        recipients = [email.strip() for email in recipients_input.split(',') if email.strip()]
        if sender_email and sender_password and subject and message_body and recipients:
            send_bulk_emails(sender_email, sender_password, subject, message_body, recipients)
        else:
            st.warning("⚠️ Please fill in all fields before sending.")
