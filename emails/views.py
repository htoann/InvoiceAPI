from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, EmailLoginForm
import imaplib
import email

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def email_login(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                mail = imaplib.IMAP4_SSL('imap.gmail.com')
                mail.login(email_address, password)
                request.session['email'] = email_address
                request.session['password'] = password
                return redirect('inbox')
            except imaplib.IMAP4.error:
                form.add_error(None, 'Failed to login to email server. Please check your email and password or use an app-specific password.')
    else:
        form = EmailLoginForm()
    return render(request, 'email_login.html', {'form': form})

def inbox(request):
    email_address = request.session.get('email')
    password = request.session.get('password')
    if not email_address or not password:
        return redirect('email_login')
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_address, password)
    mail.select('inbox')
    result, data = mail.search(None, 'ALL')
    mail_ids = data[0].split()
    emails = []
    for mail_id in mail_ids:
        result, message_data = mail.fetch(mail_id, '(RFC822)')
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)
        emails.append({
            'subject': msg['subject'],
            'from': msg['from'],
            'date': msg['date']
        })
    return render(request, 'inbox.html', {'emails': emails})
