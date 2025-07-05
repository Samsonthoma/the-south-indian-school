import os
import csv
import json
import qrcode
from urllib.parse import quote

# Config
INPUT_FILE = "school-payments/students.csv"
OUTPUT_DIR = "school-payments/pay"
QR_DIR = os.path.join(OUTPUT_DIR, "qrs")
UPI_ID = "8052508895@okbizaxis"
MERCHANT_NAME = "The South Indian School"
CURRENCY = "INR"

def load_students(path):
    _, ext = os.path.splitext(path.lower())
    with open(path, newline='', encoding='utf-8-sig') as f:
        if ext == ".csv":
            reader = csv.DictReader(f)
            return [
                {k.strip(): v.strip() for k, v in row.items()}
                for row in reader
                if row.get("id") and row.get("name") and row.get("amount")
            ]
        elif ext == ".json":
            return json.load(f)
        else:
            raise ValueError("Unsupported file format")

def make_qr(upi_link, filename):
    qr = qrcode.make(upi_link)
    qr.save(filename)

def make_html(student_id, student_name, amount, upi_link):
    qr_path = f"qrs/{student_id}.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Pay ₹{amount} | {MERCHANT_NAME}</title>
  <meta http-equiv="refresh" content="0; url={upi_link}" />
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      background-color: #f9f9f9;
      color: #333;
      text-align: center;
      padding: 2rem;
    }}
    .container {{
      background: #fff;
      border-radius: 10px;
      padding: 2rem;
      max-width: 500px;
      margin: auto;
      box-shadow: 0 0 20px rgba(0,0,0,0.1);
    }}
    h1 {{
      color: #0a66c2;
    }}
    .info {{
      margin: 1rem 0;
      font-size: 1.1rem;
    }}
    .link-button {{
      display: inline-block;
      background-color: #0a66c2;
      color: white;
      text-decoration: none;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-weight: bold;
      margin-top: 1rem;
    }}
    img {{
      width: 200px;
      margin-top: 1rem;
      border: 1px solid #ccc;
      border-radius: 10px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>📲 Fee Payment</h1>
    <p class="info">
      Student: <strong>{student_name}</strong><br>
      ID: <strong>{student_id}</strong><br>
      Amount: <strong>₹{amount}</strong>
    </p>
    <a class="link-button" href="{upi_link}">Pay Now via UPI</a>
    <p class="info">or scan this QR code:</p>
    <img src="{qr_path}" alt="QR Code for UPI" />
  </div>
</body>
</html>"""

def main():
    students = load_students(INPUT_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(QR_DIR, exist_ok=True)

    for student in students:
        student_id = student["id"]
        student_name = student["name"]
        amount = student["amount"]

        note = f"Fee {student_id} {student_name}"
        tn = quote(note)
        upi_link = (
            f"upi://pay?pa={UPI_ID}&pn={quote(MERCHANT_NAME)}"
            f"&am={amount}&tn={tn}&cu={CURRENCY}"
        )

        # QR code generation
        qr_file = os.path.join(QR_DIR, f"{student_id}.png")
        make_qr(upi_link, qr_file)

        # HTML generation
        html_file = os.path.join(OUTPUT_DIR, f"{student_id}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(make_html(student_id, student_name, amount, upi_link))

        print(f"✅ Created: {html_file}")

if __name__ == "__main__":
    main()