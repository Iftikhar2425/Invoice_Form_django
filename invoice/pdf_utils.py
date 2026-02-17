import fitz
import os
from decimal import Decimal
from django.conf import settings

BASE_DIR = settings.BASE_DIR
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
ORIGINAL_PDF = os.path.join(UPLOAD_FOLDER, "original.pdf")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def wipe_rect(page, rect):
    r = fitz.Rect(rect)
    page.add_redact_annot(r, fill=(1, 1, 1))
    page.apply_redactions()


def write_in_rect(page, rect, text, fontsize=8):
    r = fitz.Rect(rect)
    page.insert_text(
        (r.x0 + 1, r.y1 - 2),
        str(text),
        fontsize=fontsize,
        fontname="helv"
    )


HEADER_COORDS = {
    "customer_name": (125.84, 110.15, 272.87, 122.43),
    "address": (125.84, 124.65, 347.06, 134.70),
    "invoice_no": (482.60, 110.13, 524.41, 120.18),
    "date": (479.85, 120.98, 523.99, 131.03),
    "license_no": (75.06, 181.90, 173.89, 191.95),
}

TABLE_COLS = {
    "sr": 54.7,
    "name": 72.1,
    "qty": 208.5,
    "batch": 249.7,
    "expiry": 330.3,
    "price": 388.6,
    "discount": 505.6,
    "amount": 546.0,
}

ROW_START_Y = 221.4
ROW_HEIGHT = 9.5

GROSS_VALUE_RECT = (540.84, 265.34, 567.87, 275.39)
NET_PAYABLE_WIPE_RECT = (530.0, 323.0, 580.0, 340.0)
PAYABLE_RECT = (540.84, 325.49, 567.87, 336.66)
TOTAL_RECT = (539.33, 242.04, 573.66, 252.09)


def process_invoice(data):
    doc = fitz.open(ORIGINAL_PDF)
    page = doc[0]

    for key, rect in HEADER_COORDS.items():
        wipe_rect(page, rect)
        write_in_rect(page, rect, data.get(key, ""), fontsize=8.5)

    table_rect = fitz.Rect(
        50, ROW_START_Y - 2,
        580, ROW_START_Y + len(data["items"]) * ROW_HEIGHT + 2
    )
    wipe_rect(page, table_rect)

    total_net = Decimal("0.00")

    for i, item in enumerate(data["items"]):
        y = ROW_START_Y + i * ROW_HEIGHT
        qty = Decimal(item["qty"])
        price = Decimal(item["price"])
        disc = Decimal(item["discount"])

        amount = (price - price * disc / 100) * qty
        total_net += amount

        page.insert_text((TABLE_COLS["sr"], y + ROW_HEIGHT), str(i + 1), fontsize=8)
        page.insert_text((TABLE_COLS["name"], y + ROW_HEIGHT), item["name"], fontsize=8)
        page.insert_text((TABLE_COLS["qty"], y + ROW_HEIGHT), str(qty), fontsize=8)
        page.insert_text((TABLE_COLS["batch"], y + ROW_HEIGHT), item["batch"], fontsize=8)
        page.insert_text((TABLE_COLS["expiry"], y + ROW_HEIGHT), item["expiry"], fontsize=8)
        page.insert_text((TABLE_COLS["price"], y + ROW_HEIGHT), f"{price:.2f}", fontsize=8)
        page.insert_text((TABLE_COLS["discount"], y + ROW_HEIGHT), f"{disc}%", fontsize=8)
        page.insert_text((TABLE_COLS["amount"], y + ROW_HEIGHT), f"{amount:.2f}", fontsize=8)

    wipe_rect(page, NET_PAYABLE_WIPE_RECT)
    write_in_rect(page, PAYABLE_RECT, f"{total_net:.2f}", fontsize=9)

    wipe_rect(page, TOTAL_RECT)
    write_in_rect(page, TOTAL_RECT, f"{total_net:.2f}", fontsize=9)

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"Invoice_{data['invoice_no']}.pdf"
    )

    doc.save(output_path)
    doc.close()
    return output_path
