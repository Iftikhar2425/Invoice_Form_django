from datetime import datetime
from .models import Invoice

def generate_invoice_number():
    
    count = Invoice.objects.filter(
        created_at__date=datetime.today()
    ).count() + 1
    return f"HHC-{count:04d}"
