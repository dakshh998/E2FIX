from fpdf import FPDF
from datetime import datetime
import os

def generate_certificate_pdf(industry_name, score, credits, cert_id):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(0.5)
    pdf.rect(12, 12, 273, 186)
    
    # Title
    pdf.set_font("times", "B", 34)
    pdf.set_text_color(21, 128, 61) # Green
    pdf.cell(0, 30, "GREEN CERTIFICATE", align="C", ln=1)
    
    pdf.set_font("times", "I", 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, "This is formally presented to", align="C", ln=1)
    
    # Industry
    pdf.set_font("times", "B", 42)
    pdf.set_text_color(34, 197, 94)
    pdf.cell(0, 25, industry_name, align="C", ln=1)
    
    pdf.set_font("times", "", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, "in recognition of their outstanding commitment to environmental responsibility "
                          "through consistent waste management and sustainable practices.", align="C")
    
    pdf.ln(10)
    
    # Stats
    pdf.set_font("times", "B", 18)
    pdf.cell(140, 10, f"Environmental Score: {score}", align="R")
    pdf.cell(10, 10, " | ", align="C")
    pdf.cell(140, 10, f"Carbon Credits: {credits:.4f}", align="L", ln=1)
    
    pdf.ln(20)
    
    # Footer elements
    today = datetime.now().strftime("%d %B %Y")
    pdf.set_font("times", "", 14)
    
    pdf.cell(80, 10, f"Date: {today}", align="L")
    pdf.cell(110, 10, "", align="C") # Spacer
    pdf.cell(80, 10, "_____________________", align="R", ln=1)
    
    pdf.cell(80, 10, f"Certificate ID: E2FIX-{cert_id}", align="L")
    pdf.cell(110, 10, "", align="C")
    
    # Fake Signature
    pdf.set_font("courier", "I", 12)
    pdf.cell(80, 10, "E2FIX Authority", align="R", ln=1)
    
    out_path = f"E2FIX_Certificate_{cert_id}.pdf"
    try:
        pdf.output(out_path)
    except Exception as e:
        print("Error saving PDF:", e)
    return out_path


def generate_city_report_pdf(city, month, data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Header
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 20, f"{city} Environmental Report", align="C", ln=1)
    
    pdf.set_font("helvetica", "I", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Period: {month}", align="C", ln=1)
    
    pdf.ln(10)
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(0, 0, 0)
    
    for key, val in data.items():
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(80, 10, f"{key}:", border=1)
        pdf.set_font("helvetica", "", 12)
        pdf.cell(110, 10, str(val), border=1, ln=1)
        
    pdf.ln(20)
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, "Generated automatically by E2FIX Engine.", align="C")
    
    out_path = f"E2FIX_{city}_Report.pdf"
    pdf.output(out_path)
    return out_path
