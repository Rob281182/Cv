import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = sys.argv[1]
ACCENT = RGBColor(0x1F, 0x5F, 0x8B)
GREY = RGBColor(0x55, 0x55, 0x55)

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(1.3)
    s.left_margin = s.right_margin = Cm(1.9)

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(10)
st.paragraph_format.space_after = Pt(2)
st.paragraph_format.line_spacing = 1.08


def bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr")
    e = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "6"), ("space", "1"), ("color", "1F5F8B")):
        e.set(qn("w:" + k), v)
    b.append(e)
    pPr.append(b)


def heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text.upper())
    r.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = ACCENT
    bottom_border(p)


def para(text, italic=False, size=None, after=2):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Cm(0.6)
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
    p.add_run(text)


def job(title, org, dates, bullets=(), summary=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.tab_stops.add_tab_stop(Cm(17.2), alignment=2)  # right
    r = p.add_run(title)
    r.bold = True
    r = p.add_run("\t" + dates)
    r.font.color.rgb = GREY
    r.font.size = Pt(10)
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    p2.paragraph_format.keep_with_next = bool(bullets or summary)
    r = p2.add_run(org)
    r.italic = True
    r.font.color.rgb = GREY
    if summary:
        para(summary)
    for b in bullets:
        bullet(b)


# ---------- Header ----------
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(0)
r = p.add_run("Robert Heideman")
r.bold = True
r.font.size = Pt(22)
r.font.color.rgb = ACCENT
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(0)
r = p.add_run("Bicycle Technician  |  Workshop Lead  |  Skills Mentor")
r.font.size = Pt(11.5)
r.font.color.rgb = GREY
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Wishart QLD 4122  •  0402 496 428  •  robert@heideman.com.au  •  Current Australian driver licence")
r.font.size = Pt(10)

# ---------- Profile ----------
heading("Profile")
para(
    "Bicycle mechanic with 10 years of hands-on experience, including running my own repair business, "
    "Heiden Cycle Works, since 2020 and working as a mechanic with Wide Open Road Cycling since 2016. "
    "I love bikes and the people who ride them. I also love teaching people how to fix them. "
    "Alongside the bikes, I have a ten-year career as a Prosthetist-Orthotist, "
    "where I've run workshops, built a new department from scratch and mentored junior technicians. "
    "Every day in that job means explaining technical things in plain, encouraging language. "
    "I'm keen to bring my mechanical skills, workshop experience and passion for sharing knowledge "
    "to the PUSH! team and help young people build bikes, skills and confidence.",
    after=4,
)

# ---------- Key skills ----------
heading("Key Skills")
bullet(" full servicing, diagnosis and repair of road, mountain, hybrid, kids' and e-bikes; complete bike builds "
       "from frame up; brakes, gears, drivetrains, wheels, hubs and bearings.", "Bicycle mechanics:")
bullet(" inspecting and refurbishing second-hand bikes so they're safe and roadworthy, and making the most of "
       "donated and recycled parts.", "Safety checks and refurbishment:")
bullet(" setting up and running workshops, including tool and equipment upkeep, parts inventory and ordering, "
       "workflow and workplace safety.", "Workshop management:")
bullet(" mentoring junior and new technicians, and breaking complex tasks into simple, achievable steps. "
       "I'm patient, encouraging and good at building confidence.", "Teaching and mentoring:")
bullet(" friendly, clear communicator. I've worked with clients and families of all ages, "
       "backgrounds and cultures in Australia, Europe and Cambodia.", "Communication:")
bullet(" design, fabrication and problem-solving, including Fusion 360 CAD and 3D printing (FDM, SLA, SLS). "
       "I love inventing, building and improving things.", "Making and fabrication:")

# ---------- Cycling experience ----------
heading("Bicycle Industry Experience")
job("Owner / Bicycle Technician", "Heiden Cycle Works, Brisbane QLD", "2020 – Present", [
    "Run my own bike servicing and repair business, covering everything from quick fixes to full overhauls and custom builds.",
    "Diagnose faults, quote the work and complete repairs to a high safety standard on a wide range of bikes.",
    "Manage every part of the business: customer service, bookings, sourcing and ordering parts, tool upkeep and accounts.",
    "Explain repairs to customers and show them simple maintenance they can do themselves.",
])
job("Bicycle Mechanic", "Wide Open Road Cycling", "2016 – Present", [
    "Mechanic supporting riders, including bike preparation, pre-ride safety checks and on-the-spot repairs.",
    "Fix mechanical problems quickly and calmly, often on the road with a mobile tool kit.",
    "Friendly, helpful point of contact for riders of all abilities, keeping them safe and riding.",
])
job("Volunteer Mechanic – Great Victorian Bike Ride", "Warrandyte High School, VIC", "2008 – 2015", [
    "Registered mechanic for the school's student team over eight years, keeping students' bikes running on a multi-day ride.",
    "Worked alongside students and teachers, keeping young riders safe and on the road.",
])
job("Volunteer Mechanic and Support Crew", "Solo world-record attempt: first and fastest woman to cycle around Australia", "")

# ---------- Professional experience ----------
heading("Professional Experience – Prosthetics and Orthotics")
para("Ten years as a Clinical Prosthetist-Orthotist and technician in Australia, Sweden and Norway, "
     "designing, building and fitting custom devices by hand in hands-on workshop settings.", italic=True, after=3)
job("Senior Prosthetist/Orthotist", "Princess Alexandra Hospital, Woolloongabba QLD", "May 2025 – Present", [
    "Manage complex inpatient and outpatient cases as part of a multidisciplinary team, and lead quality assurance projects.",
])
job("Senior Prosthetist/Orthotist", "Amend Rehab Pty Ltd, Eight Mile Plains QLD", "Apr 2024 – Present", [
    "Set up a new Prosthetics and Orthotics department from scratch, including the workshop, equipment, workflow and digital (CAD/CAM) manufacturing.",
    "Responsible for assessment, manufacturing, fitting, referrals, NDIS funding and client relationships.",
])
job("Senior Orthotic Technician and Head of Digital Design", "Queensland Orthotic Lab, Capalaba QLD", "Jan 2024 – Present", [
    "Hands-on fabrication in a busy production workshop. I mentor and train junior and new technicians.",
    "Introduced 3D scanning, modelling and printing into the lab's manufacturing process.",
])
job("Senior Clinical Orthotist and Technician", "Orthotic Motion Pty Ltd, Geelong VIC", "Oct 2018 – Mar 2023")
job("Prosthetist-Orthotist and Technician", "Drevelin Ortopedi AB, Bergen, Norway", "Aug 2017 – Aug 2018")
job("Prosthetist-Orthotist and Technician", "Optopedia Ortopediteknisk AS, Stockholm, Sweden", "Feb 2016 – Aug 2017")
job("Clinical Placement – Prosthetics", "Veterans International Cambodia, Phnom Penh", "Feb 2015 – Apr 2015", [
    "Built and fitted low-cost prostheses with limited resources, finding practical solutions with whatever was available.",
])

# ---------- Education ----------
heading("Education and Training")
job("Bachelor of Health Science / Master of Clinical Prosthetics and Orthotics", "La Trobe University, Bundoora VIC", "2012 – 2015")
job("Cultural Exchange Program", "Jönköping University, Sweden", "Jan 2014 – Jul 2014")
bullet(" founding member of the Digital Limb Collective; participant at the 2016 ISPO European Congress.", "Professional development:")

# ---------- Community ----------
heading("Community and Volunteering")
bullet("Regular volunteer at Edgar's Mission animal sanctuary, Lancefield VIC.")
bullet("Oxfam Trailwalker, Taupō NZ (2013): our team raised $15,000.")
bullet("Relay For Life participant (2009–2012); Australian Red Cross door-knock appeal volunteer (2009–2013).")

# ---------- Other ----------
heading("Other Information")
bullet(" willing to obtain a Queensland Blue Card (Working with Children Check) straight away.", "Working with Children:")
bullet(" English (native), Swedish and Norwegian (proficient).", "Languages:")
bullet(" Microsoft Word, Excel, Outlook and PowerPoint; Fusion 360; HTML and CSS.", "Computer skills:")
bullet(" road, mountain, track and triathlon cycling. I've completed Ironman Melbourne, the 3 Peaks Challenge "
       "and the Otway Odyssey. I also enjoy surfing, skiing and camping.", "Interests:")

# ---------- References ----------
heading("References")
t = doc.add_table(rows=1, cols=2)
refs = [
    ("Aiden McDade", "Director and Senior Physiotherapist, Amend Rehab Pty Ltd", "0449 734 114  •  Aiden@amendrehab.com.au"),
    ("Liz Heagney", "Office Manager, Queensland Orthotic Lab Pty Ltd", "0405 328 472  •  Lizheagney38@gmail.com"),
]
for cell, (n, role, contact) in zip(t.rows[0].cells, refs):
    p = cell.paragraphs[0]
    r = p.add_run(n)
    r.bold = True
    p2 = cell.add_paragraph(role)
    p2.runs[0].font.size = Pt(10)
    p3 = cell.add_paragraph(contact)
    p3.runs[0].font.size = Pt(10)

doc.save(OUT)
print("saved", OUT)
