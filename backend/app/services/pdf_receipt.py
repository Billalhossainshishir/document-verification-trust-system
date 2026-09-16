import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

def build_receipt_pdf(receipt):
    payload = json.loads(receipt.payload_json)
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    y = A4[1] - 70
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(55, y, "DOCUMENT VERIFICATION RECEIPT")
    y -= 38
    lines = [
        ("Receipt ID", receipt.receipt_id),
        ("Verification ID", payload["verification_id"]),
        ("Document ID", payload["document_id"]),
        ("Document", payload["document"]),
        ("Candidate", payload["candidate_document"]),
        ("Status", payload["status"]),
        ("Registered", payload["registered_at"]),
        ("Verified", payload["verified_at"]),
        ("Hash algorithm", payload["algorithm"]),
        ("Signature", payload["receipt_signature"]),
    ]
    for label, value in lines:
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(55, y, label + ":")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(165, y, str(value)[:85])
        y -= 20
    y -= 8
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(55, y, "Registered SHA-256:")
    y -= 16
    canvas.setFont("Courier", 8)
    canvas.drawString(55, y, payload["registered_sha256"])
    y -= 24
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(55, y, "Candidate SHA-256:")
    y -= 16
    canvas.setFont("Courier", 8)
    canvas.drawString(55, y, payload["candidate_sha256"])
    canvas.save()
    return buffer.getvalue()
