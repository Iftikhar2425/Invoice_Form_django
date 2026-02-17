from django.shortcuts import render
from django.http import FileResponse
from django.utils import timezone
from decimal import Decimal
from .models import Invoice, InvoiceItem
from .utils import generate_invoice_number
from .pdf_utils import process_invoice


def index(request):
    return render(request, "invoices/index.html")


def generate(request):
    invoice_no = generate_invoice_number()
    date = timezone.now().strftime("%d/%m/%Y")

    items = []
    total = Decimal("0.00")

    names = request.POST.getlist("item_name[]")
    qtys = request.POST.getlist("qty[]")
    prices = request.POST.getlist("price[]")
    discounts = request.POST.getlist("discount[]")
    batches = request.POST.getlist("batch[]")
    expiries = request.POST.getlist("expiry[]")

    for i in range(len(names)):
        amount = (Decimal(prices[i]) - Decimal(prices[i]) * Decimal(discounts[i]) / 100) * Decimal(qtys[i])
        total += amount
        items.append({
            "name": names[i],
            "qty": qtys[i],
            "price": prices[i],
            "discount": discounts[i],
            "batch": batches[i],
            "expiry": expiries[i],
        })

    invoice = Invoice.objects.create(
        invoice_no=invoice_no,
        customer_name=request.POST["customer_name"],
        address=request.POST["address"],
        license_no=request.POST["license_no"],
        total_amount=total
    )

    for item in items:
        InvoiceItem.objects.create(invoice=invoice, **item)

    pdf = process_invoice({
        "invoice_no": invoice_no,
        "date": date,
        "customer_name": invoice.customer_name,
        "address": invoice.address,
        "license_no": invoice.license_no,
        "items": items,
    })

    return FileResponse(open(pdf, "rb"), as_attachment=True)
