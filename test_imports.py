# Test imports
try:
    import smtplib
    print("smtplib: OK")
except ImportError as e:
    print(f"smtplib: FAILED - {e}")

try:
    import ssl
    print("ssl: OK")
except ImportError as e:
    print(f"ssl: FAILED - {e}")

try:
    from email.mime.text import MIMEText
    print("MIMEText: OK")
except ImportError as e:
    print(f"MIMEText: FAILED - {e}")

try:
    from email.mime.multipart import MIMEMultipart
    print("MIMEMultipart: OK")
except ImportError as e:
    print(f"MIMEMultipart: FAILED - {e}")

try:
    from zoneinfo import ZoneInfo
    print("ZoneInfo: OK")
except ImportError as e:
    print(f"ZoneInfo: FAILED - {e}")

try:
    import mysql.connector
    print("mysql.connector: OK")
except ImportError as e:
    print(f"mysql.connector: FAILED - {e}")

try:
    from flask import Flask
    print("Flask: OK")
except ImportError as e:
    print(f"Flask: FAILED - {e}")

print("All tests complete")