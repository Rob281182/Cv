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
    s.top_margin = s.bottom_margin = Cm(1.1)
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
r = p.add_run("Wishart QLD 4122  •  0402 496 428  •  robert@heideman.com.au  •  Driver licence  •  Current Blue Card")
r.font.size = Pt(10)

# ---------- Profile ----------
heading("Profile")
para(
    "I've been riding bikes since I was two, and at 14 I landed my first job building bikes at my local bike shop over the "
    "summer holidays. I've worked as a mechanic ever since, from the end of high school and all through university. When I "
    "started my career as a Prosthetist-Orthotist, I kept the bikes going, working on my own and travelling as a tour mechanic "
    "with Wide Open Road Cycling in Europe, Japan and Australia. In 2020, during COVID, I started my own bike brand, Heiden "
    "Cycle Works, designing and building custom bespoke bikes myself. I've also created and adapted bikes for people with "
    "disabilities. What I enjoy most is passing on what I know, and I'd love to bring that to PUSH!, helping young people "
    "build their own bikes and the confidence that comes with it.",
    after=4,
)

# ---------- Key skills ----------
heading("Key Skills")
bullet(" full servicing, diagnosis and repair of road, mountain, hybrid, kids' and e-bikes; complete bike builds "
       "from the frame up, including custom frame building; brakes, gears, drivetrains, wheels, hubs and bearings.", "Bicycle mechanics:")
bullet(" creating and adapting bikes for people with disabilities, drawing on my orthotics background.", "Adaptive bikes:")
bullet(" inspecting and refurbishing second-hand bikes so they're safe and roadworthy, and making the most of "
       "donated and recycled parts.", "Safety checks and refurbishment:")
bullet(" running workshops, including tool and equipment upkeep, parts inventory and ordering, "
       "workflow and workplace safety.", "Workshop management:")
bullet(" mentoring junior and new technicians, and breaking complex tasks into simple, achievable steps. "
       "I'm patient, encouraging and good at building confidence.", "Teaching and mentoring:")
bullet(" carbon frame building, design and problem-solving, including Fusion 360 CAD and 3D printing (FDM, SLA, SLS). "
       "I love inventing, building and improving things.", "Making and fabrication:")

# ---------- Cycling experience ----------
heading("Bicycle Industry Experience")
job("Founder / Frame Builder and Bicycle Technician", "Heiden Cycle Works, Brisbane QLD", "2020 – Present", [
    "Founded the business. I design and build custom bicycle frames from carbon tubes joined with 3D-printed lugs, which I design myself.",
    "Build, service and repair all kinds of bikes, from entry-level commuters to high-end race bikes.",
    "Diagnose faults, quote the work and complete repairs to a high safety standard.",
    "Run every part of the business, including customer service, sourcing and ordering parts, workshop and tool upkeep, and accounts.",
])
job("Travelling Tour Mechanic", "Wide Open Road Cycling", "2016 – Present (tours each year)", [
    "Travel with multi-day cycling tours in Europe, Japan and Australia each year and maintain every bike on the tour.",
    "Do daily safety checks, servicing and roadside repairs from a mobile workshop, often with limited tools and parts.",
    "Friendly, helpful point of contact for riders of all abilities, keeping them safe and riding.",
])
job("Bicycle Mechanic", "The Ride Cycles, Kew VIC", "2009 – 2015", [
    "Workshop mechanic in a busy retail bike shop: servicing, repairs, new bike builds and customer service.",
])
job("Volunteer Mechanic – Great Victorian Bike Ride", "Warrandyte High School, VIC", "2008 – 2015", [
    "Registered mechanic for the school's student team over eight years, keeping students' bikes running on a multi-day ride.",
    "Worked alongside students and teachers, keeping young riders safe and on the road.",
])
job("Volunteer Mechanic and Support Crew – Lesa Ashford", "Solo world-record attempt: first and fastest woman to cycle around Australia", "2023")

# ---------- Professional experience ----------
heading("Professional Experience – Prosthetics and Orthotics")
para("Ten years as a Prosthetist-Orthotist and technician in Australia, Sweden and Norway, building custom devices by hand.", italic=True, after=3)
job("Sole Owner / Principal Orthotist", "Roam Orthotics", "Oct 2026 – Present")
job("Senior Orthotist", "Ability Made", "Jan 2026 – Sep 2026", [
    "Senior orthotic role delivering custom orthoses made with digital scanning and design.",
])
job("Senior Prosthetist/Orthotist", "Princess Alexandra Hospital, Woolloongabba QLD", "May 2025 – Mar 2026", [
    "Manage complex inpatient and outpatient cases as part of a multidisciplinary team, and lead quality assurance projects.",
])
job("Senior Orthotic Technician and Head of Digital Design", "Queensland Orthotic Lab, Capalaba QLD", "Jan 2024 – Present", [
    "Hands-on fabrication in a busy production workshop. I mentor and train junior and new technicians.",
    "Introduced 3D scanning, modelling and printing into the lab's manufacturing process.",
])
job("Senior Clinical Orthotist and Technician", "Orthotic Motion Pty Ltd, Geelong VIC", "Oct 2018 – Mar 2023")
job("Prosthetist-Orthotist and Technician", "Drevelin Ortopedi AB, Bergen, Norway", "Aug 2017 – Aug 2018")
job("Prosthetist-Orthotist and Technician", "Optopedia Ortopediteknisk AS, Stockholm, Sweden", "Feb 2016 – Aug 2017")

# ---------- Education ----------
heading("Education and Training")
job("Bachelor of Health Science / Master of Clinical Prosthetics and Orthotics", "La Trobe University, Bundoora VIC", "2012 – 2015")
job("Cultural Exchange Program", "Jönköping University, Sweden", "Jan 2014 – Jul 2014")
bullet(" founding member of the Digital Limb Collective; participant at the 2016 ISPO European Congress.", "Professional development:")

# ---------- Community ----------
heading("Community and Volunteering")
bullet("Veterans International Cambodia, Phnom Penh (2015): volunteered building and fitting low-cost prostheses with limited resources.")
bullet("Regular volunteer at Edgar's Mission animal sanctuary, Lancefield VIC.")
bullet("Oxfam Trailwalker, Taupō NZ (2013): our team raised $15,000.")
bullet("Relay For Life participant (2009–2012); Australian Red Cross door-knock appeal volunteer (2009–2013).")

# ---------- Other ----------
heading("Other Information")
bullet(" current Queensland Blue Card (held a Working with Children Check for 10+ years) and current NDIS Worker Screening Check (Yellow Card).", "Screening checks:")
bullet(" English (native), Swedish and Norwegian (proficient).", "Languages:")
bullet(" Microsoft Word, Excel, Outlook and PowerPoint; Fusion 360; HTML and CSS.", "Computer skills:")
bullet(" road, mountain, track and triathlon cycling. I've completed Ironman Melbourne, the 3 Peaks Challenge "
       "and the Otway Odyssey. I also enjoy surfing, skiing and camping.", "Interests:")

# ---------- References ----------
heading("References")
t = doc.add_table(rows=1, cols=2)
refs = [
    ("Clare Holdsworth", "Owner and Tour Operator, Wide Open Road Cycle Tours", "wideopenroadcycletours@gmail.com"),
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
