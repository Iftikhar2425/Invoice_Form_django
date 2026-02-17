from django.db import models
from django.utils import timezone
import uuid

class Invoice(models.Model):
    invoice_no = models.CharField(max_length=30, unique=True, editable=False)
    customer_name = models.CharField(max_length=200)
    address = models.TextField()
    license_no = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = f"INV-{str(uuid.uuid4())[:8].upper()}"  # Auto-generate invoice number
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_no

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    qty = models.IntegerField()
    batch = models.CharField(max_length=50)
    expiry = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
