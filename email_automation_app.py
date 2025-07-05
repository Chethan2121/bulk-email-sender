import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import pandas as pd
import time

# ---------------------- EMAIL SENDER FUNCTION ----------------------
def send_bulk_emails(sender_email, sender_password, subject, body, recipient_list, attachment=None):
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

            if attachment is not None:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{attachment.name}"')
                msg.attach(part)

            server.sendmail(sender_email, recipient, msg.as_string())
            log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.success(f"✅ [{log_time}] Email sent to: {recipient}")

        server.quit()
        st.info("✅ All emails sent successfully!")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ---------------------- STREAMLIT UI ----------------------
st.set_page_config(page_title="📧 Gmail Bulk Email Sender", layout="centered")
st.title("📧 Bulk Email Sender (via Gmail)")

with st.expander("ℹ️ Where to Get Your Gmail App Password?", expanded=False):
    st.markdown("""
    **📌 Steps to Get Gmail App Password:**
    1. Go to [Google Account Security](https://myaccount.google.com/security)
    2. Turn on **2-Step Verification**
    3. Visit [App Passwords](https://myaccount.google.com/apppasswords)
    4. Select **Mail** and name the device (e.g. "Streamlit App")
    5. Copy the **16-character password**
    6. Use it in place of your Gmail password here

    🔐 This is more secure than using your regular password.
    """)

# ---------------------- EMAIL FORM ----------------------
with st.form("email_form"):
    st.subheader("🔐 Gmail Credentials")
    sender_email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    sender_password = st.text_input("App Password", type="password")

    st.subheader("✉️ Email Content")
    subject = st.text_input("Email Subject", placeholder="Enter the subject")
    message_body = st.text_area("Email Message", placeholder="Type your message here...")

    st.subheader("📎 Optional File Attachment")
    attachment = st.file_uploader("Attach a file (PDF, DOCX, etc.)", type=["pdf", "docx", "txt", "jpg", "png", "xlsx"])

    st.subheader("📬 Recipients")
    input_method = st.radio("Select Recipient Input Method", ["Manual Entry", "Upload CSV"])

    # Manual Input Section
    recipients_input = st.text_area("Enter recipient emails (comma-separated)", placeholder="user1@example.com, user2@example.com")

    # CSV Upload Section
    csv_file = st.file_uploader("📁 Upload CSV with `email` column", type=["csv"])
    csv_recipients = []
    if csv_file is not None:
        try:
            df = pd.read_csv(csv_file)
            if 'email' in df.columns:
                csv_recipients = df['email'].dropna().tolist()
                st.success(f"📄 Loaded {len(csv_recipients)} emails from CSV.")
            else:
                st.error("⚠️ CSV must contain a column named 'email'.")
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")

    # Final recipient list decided based on selected method
    recipient_list = []
    if input_method == "Manual Entry":
        recipient_list = [email.strip() for email in recipients_input.split(",") if email.strip()]
    elif input_method == "Upload CSV":
        recipient_list = csv_recipients

    st.subheader("📤 Email Preview")
    if st.checkbox("Show preview before sending"):
        st.markdown(f"**Subject:** {subject}")
        st.markdown(f"**Message:**\n{message_body}")
        st.markdown(f"**Recipients ({len(recipient_list)}):** {recipient_list}")

    st.subheader("⏱️ Schedule Email Delivery")
    schedule_later = st.checkbox("Schedule this email to be sent later?, (Let the website be open)")
    scheduled_datetime = None
    if schedule_later:
        schedule_date = st.date_input("Select a date")
        schedule_time = st.time_input("Select a time")
        scheduled_datetime = datetime.combine(schedule_date, schedule_time)

    submitted = st.form_submit_button("🚀 Send Emails")

# ---------------------- SUBMIT ACTION ----------------------
if submitted:
    if not all([sender_email, sender_password, subject, message_body]) or not recipient_list:
        st.warning("⚠️ Please fill in all required fields and recipient emails.")
    else:
        if scheduled_datetime:
            now = datetime.now()
            delay = (scheduled_datetime - now).total_seconds()
            if delay > 0:
                st.info(f"⏳ Email scheduled. Waiting {int(delay)} seconds...")
                time.sleep(delay)
            elif delay < -60:
                st.error("⚠️ Scheduled time is in the past. Please pick a future time.")
                st.stop()

        send_bulk_emails(sender_email, sender_password, subject, message_body, recipient_list, attachment)
