from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from app import db, csrf
from app.models import EmailAccount, MexcAccount
from app.forms import EmailAccountForm, MexcAccountForm
from app.utils import (generate_name_for_country, generate_email, generate_password, 
                       export_emails_to_excel, export_mexc_accounts_to_excel)
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    email_count = EmailAccount.query.count()
    mexc_count = MexcAccount.query.count()
    
    # Get accounts with less than 5 referrals for the dashboard
    available_referrers = MexcAccount.query.all()
    available_for_referral = [acc for acc in available_referrers if acc.referral_count < 5]
    
    recent_emails = EmailAccount.query.order_by(EmailAccount.created_at.desc()).limit(5).all()
    recent_mexc = MexcAccount.query.order_by(MexcAccount.created_at.desc()).limit(5).all()
    
    # Add the current year for the footer
    now = datetime.now()
    
    return render_template('index.html', 
                          email_count=email_count,
                          mexc_count=mexc_count,
                          available_for_referral=available_for_referral,
                          recent_emails=recent_emails,
                          recent_mexc=recent_mexc,
                          now=now)

@main_bp.context_processor
def inject_now():
    """Make now variable available to all templates."""
    return {'now': datetime.now()}

@main_bp.route('/emails')
def email_list():
    emails = EmailAccount.query.order_by(EmailAccount.created_at.desc()).all()
    now = datetime.now()
    return render_template('emails.html', emails=emails, now=now)

@main_bp.route('/add-email', methods=['GET', 'POST'])
def add_email():
    form = EmailAccountForm()
    
    # Set a default password if none is provided
    if not form.password.data:
        form.password.data = generate_password()
    
    if form.validate_on_submit():
        if form.generate_name.data:
            first_name, last_name = generate_name_for_country(form.country.data)
            form.first_name.data = first_name
            form.last_name.data = last_name
            
            # Generate email based on the first and last name
            form.email.data = generate_email(first_name, last_name)
                
        email_account = EmailAccount(
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            country=form.country.data
        )
        
        db.session.add(email_account)
        db.session.commit()
        flash('Email account created successfully!', 'success')
        return redirect(url_for('main.email_list'))
    
    return render_template('add_email.html', form=form)

@main_bp.route('/mexc-accounts')
def mexc_list():
    accounts = MexcAccount.query.order_by(MexcAccount.created_at.desc()).all()
    return render_template('mexc_accounts.html', accounts=accounts)


@main_bp.route('/delete/email/<int:id>', methods=['POST'])
def delete_email(id):
    email = EmailAccount.query.get_or_404(id)
    db.session.delete(email)
    db.session.commit()
    flash('Email account deleted successfully!', 'success')
    return redirect(url_for('main.email_list'))

@main_bp.route('/delete/mexc/<int:id>', methods=['POST'])
def delete_mexc(id):
    account = MexcAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    flash('MEXC account deleted successfully!', 'success')
    return redirect(url_for('main.mexc_list'))

@main_bp.route('/add-mexc', methods=['GET', 'POST'])
def add_mexc():
    form = MexcAccountForm()
    
    # Populate the email_id choices
    form.email_id.choices = [(e.id, e.email) for e in EmailAccount.query.all()]
    
    # Populate the referrer_id choices - add a "None" option at the beginning
    referrer_choices = [(0, 'None')]
    
    # Add only accounts with less than 5 referrals
    available_referrers = MexcAccount.query.all()
    
    for acc in available_referrers:
        if acc.referral_count < 5:
            referrer_choices.append((acc.id, acc.username))
    
    form.referrer_id.choices = referrer_choices
    
    # Handle GET parameters for pre-selection
    if request.method == 'GET':
        email_id = request.args.get('email_id', type=int)
        referrer_id = request.args.get('referrer_id', type=int)
        
        if email_id:
            form.email_id.default = email_id
            form.process()
        
        if referrer_id:
            form.referrer_id.default = referrer_id
            form.process()
    
    # Set a default password if none is provided
    if not form.password.data:
        form.password.data = generate_password()
    
    if form.validate_on_submit():
        mexc_account = MexcAccount(
            username=form.username.data,
            password=form.password.data,
            email_id=form.email_id.data,
            proxy=form.proxy.data,
            referral_link=form.referral_link.data,
            notes=form.notes.data,
            volume_completed=form.volume_completed.data
        )
        
        # Handle the referrer relationship
        if form.referrer_id.data and form.referrer_id.data > 0:
            referrer = MexcAccount.query.get(form.referrer_id.data)
            if referrer and referrer.referral_count < 5:
                mexc_account.referrer_id = form.referrer_id.data
            else:
                flash('This referrer already has 5 referrals.', 'warning')
        
        db.session.add(mexc_account)
        db.session.commit()
        flash('MEXC account created successfully!', 'success')
        return redirect(url_for('main.mexc_list'))
    
    return render_template('add_mexc.html', form=form)

@main_bp.route('/account-details/<int:account_id>')
def account_details(account_id):
    account = MexcAccount.query.get_or_404(account_id)
    
    # Get referrals for this account
    referrals = account.referrals.all()
    
    # Get referrer info if available
    referrer = None
    if account.referrer_id:
        referrer = MexcAccount.query.get(account.referrer_id)
    
    return render_template('account_details.html', 
                          account=account, 
                          referrals=referrals,
                          referrer=referrer)

@main_bp.route('/api/generate-name', methods=['POST'])
@csrf.exempt
def api_generate_name():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        country = data.get('country', 'USA')
        
        first_name, last_name = generate_name_for_country(country)
        email = generate_email(first_name, last_name)
        
        return jsonify({
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/export/emails')
def export_emails():
    emails = EmailAccount.query.order_by(EmailAccount.created_at.desc()).all()
    
    if not emails:
        flash('No email accounts to export.', 'warning')
        return redirect(url_for('main.email_list'))
    
    output = export_emails_to_excel(emails)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"email_accounts_{timestamp}.xlsx"
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@main_bp.route('/export/mexc-accounts')
def export_mexc_accounts():
    accounts = MexcAccount.query.order_by(MexcAccount.created_at.desc()).all()
    
    if not accounts:
        flash('No MEXC accounts to export.', 'warning')
        return redirect(url_for('main.mexc_list'))
    
    output = export_mexc_accounts_to_excel(accounts)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"mexc_accounts_{timestamp}.xlsx"
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )