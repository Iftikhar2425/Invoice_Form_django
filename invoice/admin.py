from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Number of blank items

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'customer_name', 'date', 'total_amount')
    search_fields = ('invoice_no', 'customer_name', 'license_no')
    list_filter = ('date',)
    readonly_fields = ('invoice_no',)
    inlines = [InvoiceItemInline]  # Show items inline in invoice

admin.site.register(Invoice, InvoiceAdmin)
