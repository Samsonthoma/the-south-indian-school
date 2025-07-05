import os
import sys
import csv
import json
from urllib.parse import quote

# --- Configuration ---
INPUT_FILE = "students.csv"
OUTPUT_DIR = "pay"
UPI_ID     = "8052508895@okbizaxis"
MERCHANT   = "TheSouthIndianSchool"
CURRENCY   = "INR"

# --- Load student records ---
def load_students(path):
    _, ext = os.path.splitext(path.lower())
    with open(path, newline='', encoding='utf-8') as f:
        if ext == ".csv":
            return list(csv.DictReader(f))
        elif ext == ".json":
            return json.load(f)
        else:
            print("Unsupported format:", ext)
            sys.exit(1)

# --- Generate a single HTML redirect page ---
def make_redirect_html(upi_link):
    return f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={upi_link}" />
  </head>
  <body>
    <p>Redirecting to your UPI app…</p>
  </body>
</html>
"""

# --- Main process ---
def main():
    students = load_students(INPUT_FILE)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for student in students:
        sid    = student["id"]
        name   = student["name"]
        amount = student["amount"]
        
        # Build transaction note and encode
        tn = f"Fee {sid} {name}"
        tn_enc = quote(tn)
        
        # Construct UPI link
        upi_link = (
            f"upi://pay?"
            f"pa={UPI_ID}&pn={MERCHANT}"
            f"&am={amount}&tn={tn_enc}"
            f"&cu={CURRENCY}"
        )
        
        # Write HTML file
        filename = os.path.join(OUTPUT_DIR, f"{sid}.html")
        with open(filename, "w", encoding="utf-8") as out:
            out.write(make_redirect_html(upi_link))
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()
