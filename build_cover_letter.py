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
    s.left_margin = s.right_margin = Cm(2.2)

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(10)
st.paragraph_format.space_after = Pt(7)
st.paragraph_format.line_spacing = 1.1


def bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr")
    e = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "6"), ("space", "4"), ("color", "1F5F8B")):
        e.set(qn("w:" + k), v)
    b.append(e)
    pPr.append(b)


def line(text, bold=False, after=0, color=None, size=None, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    if align:
        p.alignment = align
    r = p.add_run(text)
    r.bold = bold
    if color:
        r.font.color.rgb = color
    if size:
        r.font.size = Pt(size)
    return p


# Header (matches CV)
line("Robert Heideman", bold=True, color=ACCENT, size=22, align=WD_ALIGN_PARAGRAPH.CENTER)
line("Bicycle Technician  |  Workshop Lead  |  Skills Mentor", color=GREY, size=11.5, align=WD_ALIGN_PARAGRAPH.CENTER)
p = line("Wishart QLD 4122  •  0402 496 428  •  robert@heideman.com.au", size=10,
         align=WD_ALIGN_PARAGRAPH.CENTER, after=14)
bottom_border(p)

line("26 October 2026", after=10)
line("Sarah White")
line("PUSH! Team Leader")
line("Younity Community Services Ltd")
line("Deception Bay QLD", after=12)
line("Re: Bicycle Technician – PUSH! Program, Deception Bay", bold=True, after=10)

body = [
    "Dear Sarah,",

    "I'm excited to apply for the Bicycle Technician role with PUSH! Bikes have been a big part of my life since I was "
    "two, and so has sharing what I know about them. PUSH!'s results speak for themselves: more than 700 young people "
    "reached, and an independent evaluation showing gains in skills, emotional regulation and positive behaviour. "
    "Leading the technical side of a program where young people learn on the tools and ride away proud of what "
    "they've built is exactly the work I'd love to do.",

    "I've worked as a bike mechanic for more than 15 years, starting in my local bike shop at 14 and then at The Ride "
    "Cycles in Kew. In 2020 I founded Heiden Cycle Works, where I design and build custom frames from carbon tubes and "
    "3D-printed lugs, and build and maintain everything from budget commuters to high-end race bikes. Since 2016 I've "
    "also travelled each year as a tour mechanic with Wide Open Road Cycling in Europe, Japan and Australia, keeping "
    "every bike on tour running from a mobile kit. Wheel truing, brake and gear adjustment, drivetrain servicing, cable "
    "replacement and safety checks are my everyday work. I'm used to running a workshop on my own, fixed or mobile, "
    "with risk assessments, equipment checks and safe work practices built in.",

    "Most recently, as a Senior Orthotist at Ability Made, my work focused on helping young people with disabilities "
    "achieve their goals and greater independence, and I mentored other clinicians. That goal-focused way of working "
    "fits naturally with PUSH!'s strengths-based approach. Ten years in orthotics has taught me to explain technical "
    "things in plain, encouraging language and break big jobs into small steps, adjusting to each person's age and "
    "ability. I also spent eight years as the volunteer mechanic for Warrandyte High School's team on the Great "
    "Victorian Bike Ride. I'm not a youth worker, but I enjoy being around young people, and I'd love to lead the bike "
    "learning alongside your youth workers and cultural mentors, developing the mechanical content for First Gear, "
    "Top Gear, Workshop and Pop-Up sessions.",

    "Running my own businesses has given me the organisational side of the role too: building relationships with "
    "referrers and community partners, managing parts and stock, and keeping accurate records and reports. I'd bring "
    "that to sourcing donor bikes and contributing to program reporting, and I'm always happy to help out at community "
    "events and BBQs.",

    "I hold a current Queensland Blue Card (I've had a Working with Children Check for over 10 years), a current NDIS "
    "Worker Screening Check (Yellow Card) and a current driver licence, and I'm happy to drive the PUSH! van. I'm "
    "looking for a part-time role and can commit three days a week, alongside a small orthotics practice I run one to "
    "two days a week. I could start from 22 November.",

    "Thank you for considering my application. I'd welcome the chance to chat about how I could contribute to PUSH!, "
    "and I'd be happy to bring along one of my frames to show you what I build.",
]
for t in body:
    p = doc.add_paragraph(t)
    p.paragraph_format.space_after = Pt(6)

line("Kind regards,", after=18)
line("Robert Heideman", bold=True)
line("0402 496 428  •  robert@heideman.com.au", size=10, color=GREY)

doc.save(OUT)
print("saved", OUT)
