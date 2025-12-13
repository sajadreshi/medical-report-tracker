from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import datetime
import random
import os
import glob
from faker import Faker

# Initialize Faker
fake = Faker()

# Define reference ranges for common lab tests
TEST_REFERENCE_RANGES = {
    "CHOLESTEROL, TOTAL": {"min": 100, "max": 200, "unit": "mg/dL", "format": "float"},
    "HDL CHOLESTEROL": {"min": 40, "max": 100, "unit": "mg/dL", "format": "float", "comparison": ">="},
    "TRIGLYCERIDES": {"min": 50, "max": 150, "unit": "mg/dL", "format": "float"},
    "LDL-CHOLESTEROL": {"min": 70, "max": 100, "unit": "mg/dL", "format": "float"},
    "CHOL/HDLC RATIO": {"min": 3.0, "max": 5.0, "unit": "", "format": "float"},
    "GLUCOSE": {"min": 65, "max": 139, "unit": "mg/dL", "format": "float"},
    "UREA NITROGEN (BUN)": {"min": 7, "max": 25, "unit": "mg/dL", "format": "float"},
    "CREATININE": {"min": 0.60, "max": 1.29, "unit": "mg/dL", "format": "float"},
    "SODIUM": {"min": 135, "max": 146, "unit": "mmol/L", "format": "int"},
    "POTASSIUM": {"min": 3.5, "max": 5.3, "unit": "mmol/L", "format": "float"},
    "WBC COUNT": {"min": 3.8, "max": 10.8, "unit": "Thousand/uL", "format": "float"},
    "RBC COUNT": {"min": 4.20, "max": 5.80, "unit": "Million/uL", "format": "float"},
    "HEMOGLOBIN": {"min": 13.2, "max": 17.1, "unit": "g/dL", "format": "float"},
    "HEMATOCRIT": {"min": 38.5, "max": 50.0, "unit": "%", "format": "float"},
    "PLATELET COUNT": {"min": 140, "max": 400, "unit": "Thousand/uL", "format": "int"},
    "TSH": {"min": 0.40, "max": 4.50, "unit": "mIU/L", "format": "float"},
    "HEMOGLOBIN A1c": {"min": 4.0, "max": 5.7, "unit": "% of total Hgb", "format": "float"},
    "PROTEIN, TOTAL": {"min": 6.1, "max": 8.1, "unit": "g/dL", "format": "float"},
    "AST": {"min": 10, "max": 40, "unit": "U/L", "format": "int"},
    "ALT": {"min": 9, "max": 46, "unit": "U/L", "format": "int"},
}

# Test panel definitions
TEST_PANELS = {
    "Lipid Panel, Standard": [
        "CHOLESTEROL, TOTAL",
        "HDL CHOLESTEROL",
        "TRIGLYCERIDES",
        "LDL-CHOLESTEROL",
        "CHOL/HDLC RATIO",
    ],
    "Comprehensive Metabolic Panel": [
        "GLUCOSE",
        "UREA NITROGEN (BUN)",
        "CREATININE",
        "SODIUM",
        "POTASSIUM",
    ],
    "CBC (Includes Diff/Plt)": [
        "WBC COUNT",
        "RBC COUNT",
        "HEMOGLOBIN",
        "HEMATOCRIT",
    ],
    "Additional Tests": [
        "TSH",
        "HEMOGLOBIN A1c",
    ],
    "Liver Function Panel": [
        "PROTEIN, TOTAL",
        "AST",
        "ALT",
    ],
}


def generate_test_value(test_name, abnormal=False):
    """Generate a test value within or outside the reference range."""
    if test_name not in TEST_REFERENCE_RANGES:
        return "N/A", "N/A"
    
    ref = TEST_REFERENCE_RANGES[test_name]
    min_val = ref["min"]
    max_val = ref["max"]
    fmt = ref["format"]
    
    if abnormal:
        # Generate abnormal value (20% chance)
        if random.random() < 0.5:
            # Low value
            value = random.uniform(min_val * 0.5, min_val * 0.9)
            flag = "L"
        else:
            # High value
            value = random.uniform(max_val * 1.1, max_val * 1.5)
            flag = "H"
    else:
        # Generate normal value (80% chance)
        value = random.uniform(min_val, max_val)
        flag = ""
    
    # Format the value
    if fmt == "int":
        value_str = str(int(round(value)))
    else:
        value_str = f"{value:.2f}".rstrip('0').rstrip('.')
    
    # Format reference range
    if "comparison" in ref and ref["comparison"] == ">=":
        ref_str = f">= {min_val} {ref['unit']}"
    elif "comparison" in ref and ref["comparison"] == "<=":
        ref_str = f"<= {max_val} {ref['unit']}"
    else:
        ref_str = f"{min_val}-{max_val} {ref['unit']}"
    
    # Add flag to result if abnormal
    if flag:
        result_str = f"{value_str} {flag}"
    else:
        result_str = value_str
    
    return result_str, ref_str


def generate_test_results(panels=None, abnormal_ratio=0.2):
    """Generate test results for specified panels with variation.
    
    Args:
        panels: List of panel names to use. If None, selects 2-4 random panels.
        abnormal_ratio: Probability of abnormal result (default 0.2 = 20%)
    
    Returns:
        Dictionary of test sections with results
    """
    if panels is None:
        # Select 2-4 random panels
        available_panels = list(TEST_PANELS.keys())
        num_panels = random.randint(2, min(4, len(available_panels)))
        selected_panels = random.sample(available_panels, num_panels)
    else:
        selected_panels = panels
    
    test_sections = {}
    
    for panel_name in selected_panels:
        if panel_name not in TEST_PANELS:
            continue
        
        results = []
        for test_name in TEST_PANELS[panel_name]:
            # 20% chance of abnormal result
            is_abnormal = random.random() < abnormal_ratio
            result, ref = generate_test_value(test_name, abnormal=is_abnormal)
            results.append((test_name, result, ref))
        
        test_sections[panel_name] = results
    
    return test_sections


def generate_sequential_dates(start_date=None, num_reports=4, interval_months=1):
    """Generate sequential dates for multiple reports.
    
    Args:
        start_date: Starting date (datetime.date). If None, uses a date 6 months ago.
        num_reports: Number of dates to generate
        interval_months: Number of months between reports (default 1 = monthly)
    
    Returns:
        List of date strings in MM/DD/YYYY format
    """
    if start_date is None:
        # Start from 6 months ago
        start_date = fake.date_between(start_date='-6m', end_date='-5m')
    
    dates = []
    current_date = start_date
    
    for _ in range(num_reports):
        dates.append(current_date.strftime("%m/%d/%Y"))
        # Add months to current date
        # Calculate new month and year
        new_month = current_date.month + interval_months
        new_year = current_date.year
        
        while new_month > 12:
            new_month -= 12
            new_year += 1
        
        # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
        try:
            current_date = current_date.replace(year=new_year, month=new_month)
        except ValueError:
            # If day doesn't exist in new month (e.g., Jan 31 -> Feb), use last day of month
            # Get last day by trying days backwards from 31
            for day in range(31, 27, -1):
                try:
                    current_date = current_date.replace(year=new_year, month=new_month, day=day)
                    break
                except ValueError:
                    continue
    
    return dates


def generate_patient_info():
    """Generate realistic patient information using Faker (without date - date generated separately)."""
    sex = random.choice(["Male", "Female"])
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Generate DOB (age between 18-80)
    dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
    dob_str = dob.strftime("%m/%d/%Y")
    
    # Generate patient ID (format: FirstInitialLastInitial + numbers)
    pat_id = f"{first_name[0]}{last_name[0]}{random.randint(100000, 999999)}"
    
    # Generate order ID prefix (format: 2-3 letters) - will be reused with different numbers
    order_prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(2, 3)))
    
    # Generate provider name
    provider = f"Dr. {fake.first_name()} {fake.last_name()}"
    
    return {
        "name": f"{last_name.upper()}, {first_name.upper()}",
        "dob": dob_str,
        "sex": sex,
        "order_prefix": order_prefix,
        "pat_id": pat_id,
        "provider": provider,
    }


def generate_lab_info():
    """Generate realistic laboratory information using Faker."""
    lab_types = [
        "BioLabs", "Diagnostics", "Health Analytics", "Medical Labs",
        "Clinical Laboratories", "Pathology Services", "Lab Solutions",
        "Diagnostic Center", "Health Sciences", "Biomedical Labs"
    ]
    
    company_name = fake.company().split()[0]  # Get first word of company
    lab_type = random.choice(lab_types)
    lab_name = f"{company_name} {lab_type}"
    
    # Generate address
    street = fake.street_address()
    city = fake.city()
    state = fake.state_abbr()
    zipcode = fake.zipcode()
    address = f"{street}, {city}, {state} {zipcode}"
    
    return {
        "name": lab_name,
        "address": address,
    }


def create_lab_report(filename, lab_info, patient_info, test_sections, report_date, order_id):
    """Create a lab report PDF with the given information.
    
    Args:
        filename: Output PDF filename
        lab_info: Laboratory information dictionary
        patient_info: Patient information dictionary (without date/order_id)
        test_sections: Dictionary of test sections and results
        report_date: Report date string (MM/DD/YYYY)
        order_id: Order ID for this specific report
    """
    doc = SimpleDocTemplate(filename, pagesize=LETTER, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=10)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=1, fontSize=10)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=9, leading=11)
    section_style = ParagraphStyle('Section', parent=styles['Heading3'], fontSize=11, spaceBefore=10, spaceAfter=5, textColor=colors.darkblue)
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=7, textColor=colors.grey)
    abnormal_style = ParagraphStyle('Abnormal', parent=styles['Normal'], fontSize=9, textColor=colors.red)

    # 1. Lab Header
    elements.append(Paragraph(lab_info['name'], title_style))
    elements.append(Paragraph(lab_info['address'], subtitle_style))
    elements.append(Spacer(1, 20))

    # 2. Patient Demographics (2-column table)
    p_data = [
        [f"Patient: {patient_info['name']}", f"Order #: {order_id}"],
        [f"DOB: {patient_info['dob']}", f"Patient ID: {patient_info['pat_id']}"],
        [f"Sex: {patient_info['sex']}", f"Report Date: {report_date}"],
        [f"Provider: {patient_info['provider']}", ""]
    ]
    
    t_pat = Table(p_data, colWidths=[3.5*inch, 3.5*inch])
    t_pat.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,3), (1,3), 1, colors.black),
    ]))
    elements.append(t_pat)
    elements.append(Spacer(1, 15))

    # 3. Test Results
    for section_name, results in test_sections.items():
        # Section Header
        elements.append(Paragraph(section_name.upper(), section_style))
        
        # Table Header
        table_data = [['Observations', 'Result', 'Reference/UoM']]
        
        # Track row indices for abnormal results
        abnormal_rows = []
        
        # Fill Rows
        for idx, row in enumerate(results, start=1):
            obs, res, ref = row
            # Check if result is abnormal (contains H or L flag)
            is_abnormal = ' H' in res or ' L' in res
            if is_abnormal:
                abnormal_rows.append(idx)
            
            table_data.append([obs, res, ref])

        # Table Style
        t = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 3.0*inch])
        
        # Build style commands
        style_commands = [
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.white]),
        ]
        
        # Highlight abnormal results in red
        for row_idx in abnormal_rows:
            style_commands.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.red))
            style_commands.append(('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'))
        
        t.setStyle(TableStyle(style_commands))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # 4. Footer / Disclaimer
    elements.append(Spacer(1, 30))
    footer_text = "This report is electronically signed. Reference ranges are based on standard adult populations. " \
                  "Results should be interpreted by a qualified medical professional. " \
                  "Testing performed by CLIA certified laboratory."
    elements.append(Paragraph(footer_text, disclaimer_style))

    # Build PDF
    doc.build(elements)
    print(f"Generated: {filename}")


def main(num_patients=3, reports_per_patient=4, date_interval_months=1):
    """Generate multiple lab reports with consistent patient/lab information.
    
    For each patient/lab combination:
    - Patient name, DOB, ID, and lab info stay the same
    - Only test results and report dates change
    - Dates are sequential (monthly by default)
    - Same test panels are used for all reports per patient
    
    Args:
        num_patients: Number of unique patient/lab combinations
        reports_per_patient: Number of reports per patient (default: 4)
        date_interval_months: Months between reports (default: 1 = monthly)
    """
    # Ensure data directory exists
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Delete previously generated PDFs
    pdf_pattern = os.path.join(data_dir, "LabReport_*.pdf")
    existing_pdfs = glob.glob(pdf_pattern)
    if existing_pdfs:
        print(f"Deleting {len(existing_pdfs)} previously generated PDF(s)...")
        for pdf_file in existing_pdfs:
            try:
                os.remove(pdf_file)
            except OSError as e:
                print(f"Warning: Could not delete {pdf_file}: {e}")
        print(f"Cleaned up {len(existing_pdfs)} old report(s)")
        print("-" * 50)
    
    total_reports = num_patients * reports_per_patient
    print(f"Generating {total_reports} medical lab reports...")
    print(f"  - {num_patients} unique patient/lab combinations")
    print(f"  - {reports_per_patient} reports per patient")
    print(f"  - {date_interval_months} month(s) between reports")
    print("-" * 50)
    
    report_counter = 1
    
    for patient_num in range(1, num_patients + 1):
        # Generate patient and lab info once per patient (stays consistent)
        lab_info = generate_lab_info()
        patient_info = generate_patient_info()
        
        # Select test panels once per patient (same panels for all reports)
        available_panels = list(TEST_PANELS.keys())
        num_panels = random.randint(2, min(4, len(available_panels)))
        selected_panels = random.sample(available_panels, num_panels)
        
        # Generate sequential dates for this patient
        start_date = fake.date_between(start_date='-6m', end_date='-5m')
        report_dates = generate_sequential_dates(
            start_date=start_date,
            num_reports=reports_per_patient,
            interval_months=date_interval_months
        )
        
        patient_last_name = patient_info['name'].split(',')[0]
        print(f"\nPatient {patient_num}: {patient_info['name']} ({lab_info['name']})")
        
        # Generate multiple reports for this patient
        for report_num, report_date in enumerate(report_dates, start=1):
            # Generate new test results (values change, panels stay same)
            test_sections = generate_test_results(panels=selected_panels, abnormal_ratio=0.2)
            
            # Generate unique order ID for this report
            order_id = f"{patient_info['order_prefix']}{random.randint(100000, 999999)}"
            
            # Create filename with patient name and report number
            filename = os.path.join(
                data_dir,
                f"LabReport_{patient_last_name}_Report{report_num}_{report_date.replace('/', '')}.pdf"
            )
            
            # Generate report
            create_lab_report(
                filename, lab_info, patient_info, test_sections,
                report_date, order_id
            )
            report_counter += 1
    
    print("-" * 50)
    print(f"Successfully generated {total_reports} reports in '{data_dir}/' directory")
    print(f"  - {num_patients} patients with {reports_per_patient} reports each")


def generate_for_patient(patient_info: dict, reports_count: int = 4, date_interval_months: int = 1) -> list:
    """
    Generate lab reports for a specific patient from the database.
    
    Args:
        patient_info: Dictionary containing patient information:
            - first_name: Patient's first name
            - last_name: Patient's last name
            - patient_id: Unique patient ID
            - date_of_birth: Patient's date of birth
            - sex: Patient's sex (Male/Female/Other)
        reports_count: Number of reports to generate
        date_interval_months: Months between reports
    
    Returns:
        List of dictionaries with report information:
            - filename: Report filename
            - file_path: Full path to the PDF
            - report_date: Date of the report
            - report_number: Report number
    """
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Delete existing reports for this patient
    patient_last_name = patient_info["last_name"].upper()
    existing_pattern = os.path.join(data_dir, f"LabReport_{patient_last_name}_*.pdf")
    existing_pdfs = glob.glob(existing_pattern)
    for pdf_file in existing_pdfs:
        try:
            os.remove(pdf_file)
            print(f"Deleted existing report: {pdf_file}")
        except OSError as e:
            print(f"Warning: Could not delete {pdf_file}: {e}")
    
    # Generate lab info
    lab_info = generate_lab_info()
    
    # Format patient info for report generation
    # Handle date_of_birth which might be a string or date object
    dob = patient_info["date_of_birth"]
    if isinstance(dob, str):
        # Parse string date (YYYY-MM-DD format from database)
        from datetime import datetime as dt
        dob_date = dt.strptime(dob, "%Y-%m-%d").date()
        dob_str = dob_date.strftime("%m/%d/%Y")
    else:
        dob_str = dob.strftime("%m/%d/%Y")
    
    formatted_patient = {
        "name": f"{patient_info['last_name'].upper()}, {patient_info['first_name'].upper()}",
        "dob": dob_str,
        "sex": patient_info["sex"],
        "order_prefix": ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(2, 3))),
        "pat_id": patient_info["patient_id"],
        "provider": f"Dr. {fake.first_name()} {fake.last_name()}",
    }
    
    # Select test panels
    available_panels = list(TEST_PANELS.keys())
    num_panels = random.randint(2, min(4, len(available_panels)))
    selected_panels = random.sample(available_panels, num_panels)
    
    # Generate sequential dates
    start_date = fake.date_between(start_date='-6m', end_date='-5m')
    report_dates = generate_sequential_dates(
        start_date=start_date,
        num_reports=reports_count,
        interval_months=date_interval_months
    )
    
    generated_reports = []
    
    print(f"\nGenerating {reports_count} reports for {formatted_patient['name']}...")
    
    for report_num, report_date_str in enumerate(report_dates, start=1):
        # Generate test results
        test_sections = generate_test_results(panels=selected_panels, abnormal_ratio=0.2)
        
        # Generate unique order ID
        order_id = f"{formatted_patient['order_prefix']}{random.randint(100000, 999999)}"
        
        # Create filename
        filename = f"LabReport_{patient_last_name}_Report{report_num}_{report_date_str.replace('/', '')}.pdf"
        file_path = os.path.join(data_dir, filename)
        
        # Generate report
        create_lab_report(
            file_path, lab_info, formatted_patient, test_sections,
            report_date_str, order_id
        )
        
        # Parse date for database
        from datetime import datetime as dt
        report_date = dt.strptime(report_date_str, "%m/%d/%Y").date()
        
        generated_reports.append({
            "filename": filename,
            "file_path": file_path,
            "report_date": report_date,
            "report_number": report_num
        })
    
    print(f"Generated {len(generated_reports)} reports for {formatted_patient['name']}")
    
    return generated_reports


if __name__ == "__main__":
    # Generate 3 patients with 4 reports each (monthly intervals)
    main(num_patients=3, reports_per_patient=4, date_interval_months=1)
