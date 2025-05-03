# app/utils.py
from faker import Faker
import random
import string
import pandas as pd
from io import BytesIO
from datetime import datetime

# Dictionary mapping countries to Faker locales
COUNTRY_TO_LOCALE = {
    'USA': 'en_US',
    'UK': 'en_GB',
    'Canada': 'en_CA',
    'Australia': 'en_AU',
    'Germany': 'de_DE',
    'France': 'fr_FR',
    'Spain': 'es_ES',
    'Italy': 'it_IT',
    'Russia': 'ru_RU',
    'China': 'zh_CN',
    'Japan': 'ja_JP',
    'South Korea': 'ko_KR',
    'Brazil': 'pt_BR',
    'Mexico': 'es_MX',
    'India': 'en_IN',
    'Slovakia': 'sk_SK',
    'Czech Republic': 'cs_CZ',
    'Georgia': 'ka_GE',
    'Bulgaria': 'bg_BG'
}

def transliterate_russian(text):
    """
    Transliterate Russian Cyrillic text to Latin alphabet.
    This follows common transliteration rules for Russian names.
    """
    char_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    result = []
    for char in text:
        result.append(char_map.get(char, char))
    
    return ''.join(result)

def generate_name_for_country(country):
    """Generate a random first and last name appropriate for the specified country."""
    locale = COUNTRY_TO_LOCALE.get(country, 'en_US')
    fake = Faker(locale)
    
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # For Russia, transliterate the Cyrillic names to Latin
    if country == 'Russia':
        first_name = transliterate_russian(first_name)
        last_name = transliterate_russian(last_name)
    
    return first_name, last_name

def generate_email(first_name, last_name):
    """Generate a random email based on first and last name."""
    fake = Faker()
    
    # Create normalized versions of names for email
    fname = first_name.lower().replace(' ', '')
    lname = last_name.lower().replace(' ', '')
    
    # Remove any special characters that might appear in transliterated names
    fname = ''.join(c for c in fname if c.isalnum())
    lname = ''.join(c for c in lname if c.isalnum())
    
    # Generate a few different email patterns
    patterns = [
        f"{fname}.{lname}@{fake.free_email_domain()}",
        f"{fname}{random.randint(10, 999)}@{fake.free_email_domain()}",
        f"{fname[0]}{lname}@{fake.free_email_domain()}",
        f"{fname}{lname[0]}@{fake.free_email_domain()}"
    ]
    
    return random.choice(patterns)

def generate_password(length=12):
    """Generate a secure random password."""
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    numbers = string.digits
    symbols = "!@#$%^&*()-_=+"
    
    # Ensure at least one character from each set
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(numbers),
        random.choice(symbols)
    ]
    
    # Fill the rest of the password
    remaining_length = length - len(password)
    all_chars = lowercase + uppercase + numbers + symbols
    password.extend(random.choice(all_chars) for _ in range(remaining_length))
    
    # Shuffle the password characters
    random.shuffle(password)
    
    # Convert list to string
    return ''.join(password)

def export_emails_to_excel(emails):
    """Export email accounts to Excel file"""
    # Create a pandas DataFrame from the email accounts
    data = []
    for email in emails:
        data.append({
            'First Name': email.first_name,
            'Last Name': email.last_name,
            'Email': email.email,
            'Password': email.password,
            'Country': email.country,
            'Created Date': email.created_at.strftime('%Y-%m-%d %H:%M'),
            'MEXC Accounts Count': len(email.mexc_accounts)
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Email Accounts')
        
        # Auto-adjust columns' width
        worksheet = writer.sheets['Email Accounts']
        for i, column in enumerate(df.columns):
            column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
            worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    output.seek(0)
    return output

def export_mexc_accounts_to_excel(accounts):
    """Export MEXC accounts to Excel file"""
    # Create a pandas DataFrame from the MEXC accounts
    data = []
    for account in accounts:
        data.append({
            'Username': account.username,
            'Password': account.password,
            'Email': account.email_account.email,
            'Email Password': account.email_account.password,
            'Full Name': f"{account.email_account.first_name} {account.email_account.last_name}",
            'Country': account.email_account.country,
            'Proxy': account.proxy if account.proxy else '',
            'Referral Link': account.referral_link if account.referral_link else '',
            'Referral Count': account.referral_count,
            'Volume Completed': 'Yes' if account.volume_completed else 'No',
            'Created Date': account.created_at.strftime('%Y-%m-%d %H:%M'),
            'Notes': account.notes if account.notes else ''
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"mexc_accounts_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='MEXC Accounts')
        
        # Auto-adjust columns' width
        worksheet = writer.sheets['MEXC Accounts']
        for i, column in enumerate(df.columns):
            column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
            worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    output.seek(0)
    return output