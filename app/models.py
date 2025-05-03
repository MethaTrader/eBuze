from datetime import datetime
from app import db

class EmailAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    mexc_accounts = db.relationship('MexcAccount', backref='email_account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Email {self.email}>'

class MexcAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email_id = db.Column(db.Integer, db.ForeignKey('email_account.id'), nullable=False)
    referrer_id = db.Column(db.Integer, db.ForeignKey('mexc_account.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    proxy = db.Column(db.String(120), nullable=True)
    referral_link = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    volume_completed = db.Column(db.Boolean, default=False)
    
    # Self-referential relationship to track referrals
    referrals = db.relationship(
        'MexcAccount', 
        backref=db.backref('referrer', remote_side=[id]),
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<MEXC Account {self.username}>'
    
    @property
    def referral_count(self):
        return self.referrals.count()