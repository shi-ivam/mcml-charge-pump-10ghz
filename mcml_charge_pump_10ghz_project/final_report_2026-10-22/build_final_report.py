#!/usr/bin/env python3
"""Fill the supplied course template with checked MCML project evidence."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
TEMPLATE = Path('/home/shivam/Downloads/VLSI_Mini_Project_Report_Template_Revised.docx')
METRICS = json.loads((HERE.parent/'mcml_cp_sim/verified_flow/results/metrics.json').read_text())
SHOTS = HERE/'screenshots'
OUT = HERE/'Final_MCML_Charge_Pump_Mini_Project_Report.docx'

doc = Document(TEMPLATE)
body = doc._element.body
for child in list(body):
    if child.tag != qn('w:sectPr'):
        body.remove(child)

styles = doc.styles
styles['Normal'].font.name = 'Times New Roman'
styles['Normal'].font.size = Pt(11)
styles['Normal'].paragraph_format.space_after = Pt(6)
styles['Normal'].paragraph_format.line_spacing = 1.12
for key, size in [('Heading 1',14),('Heading 2',12)]:
    styles[key].font.name = 'Times New Roman'
    styles[key].font.size = Pt(size)
    styles[key].font.bold = True
    styles[key].font.color.rgb = RGBColor(19, 47, 76)
    styles[key].paragraph_format.space_before = Pt(12)
    styles[key].paragraph_format.space_after = Pt(5)

sec = doc.sections[0]
sec.top_margin = Inches(.68)
sec.bottom_margin = Inches(.62)
sec.left_margin = Inches(.72)
sec.right_margin = Inches(.72)
header = sec.header.paragraphs[0]
header.text = 'BECE303L_VLSI System Design  |  Mini Project Report'
header.style = styles['Normal']
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
for run in header.runs: run.font.size = Pt(8); run.font.color.rgb = RGBColor(96,109,125)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer.add_run('MCML charge pump  •  October 2026  •  Page ')
run.font.size = Pt(8)
fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); footer._p.append(fld)

def p(text='', boldlead=None):
    x=doc.add_paragraph()
    if boldlead and text.startswith(boldlead):
        x.add_run(boldlead).bold=True
        x.add_run(text[len(boldlead):])
    else: x.add_run(text)
    return x

def h(text,level=1): doc.add_heading(text,level)

def table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers))
    t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for j,s in enumerate(headers):
        c=t.rows[0].cells[j];c.text=str(s)
        for r in c.paragraphs[0].runs:r.bold=True;r.font.size=Pt(9)
    for row in rows:
        cells=t.add_row().cells
        for j,s in enumerate(row):
            cells[j].text=str(s)
            cells[j].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for para in cells[j].paragraphs:
                para.paragraph_format.space_after=Pt(0)
                for run in para.runs:run.font.size=Pt(9)
    if widths:
        for row in t.rows:
            for c,w in zip(row.cells,widths):c.width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def fig(file, caption, width=6.7):
    q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_before=Pt(5);q.paragraph_format.space_after=Pt(2)
    q.paragraph_format.keep_with_next=True
    q.add_run().add_picture(str(SHOTS/file),width=Inches(width))
    c=doc.add_paragraph(caption);c.alignment=WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after=Pt(8)
    c.paragraph_format.keep_together=True
    for r in c.runs:r.italic=True;r.font.size=Pt(9)

def newpage(): doc.add_page_break()

# Cover, using the course and document structure from the supplied template.
for _ in range(5): p()
x=p('BECE303L_VLSI System Design');x.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in x.runs:r.bold=True;r.font.size=Pt(16)
x=p('Mini Project Report');x.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in x.runs:r.font.size=Pt(18)
p()
x=p('Design and Simulation of a 10 GHz MCML Charge Pump for PLL Applications');x.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in x.runs:r.bold=True;r.font.size=Pt(20)
for _ in range(3):p()
x=p('TEAM MEMBERS');x.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in x.runs:r.bold=True;r.font.size=Pt(14)
for name in ['Shivam Kumar — 24BLC1103','Pragyan Jain — 24BLC1100','K Navin Aakash — 23BLC1238']:
    x=p(name);x.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in x.runs:r.font.size=Pt(13)
for _ in range(4):p()
x=p('Fall 2026  |  Academic Year 2026–2027');x.alignment=WD_ALIGN_PARAGRAPH.CENTER
p('Simulation environment: Cadence Virtuoso 6.1.7 schematic, ADE L setup, ViVA waveform display, and Calculator evaluation.').alignment=WD_ALIGN_PARAGRAPH.CENTER
newpage()

h('Abstract')
p('This fifth-semester VLSI System Design mini project builds and simulates a 10 GHz MCML charge pump for a PLL, based on the circuit described by Sivasakthi and Radhika [1]. We prepared the schematic and testbench in Cadence Virtuoso, checked the connections, set up the transient analysis in ADE L, and viewed charging and discharging results in ViVA. With a 1.0 V supply, 0.45 V bias, 27 °C temperature, and a 300 fF internal load, the measured average delays are 13.811 ps for charging and 15.447 ps for discharging. The corresponding average VDD powers are 22.528 µW and 16.097 µW. The settled output swing is 0.993524 V. The discharge delay differs from the paper’s 16.71 ps result by 7.56%, and the output swing differs from its 0.98 V result by 1.38%. Both differences are within a 10% numerical comparison window. The simulation shows the expected rise and fall of the output. The paper and this project use different loads and model sets, so this comparison is an educational check of the circuit behavior rather than an identical-condition reproduction.')
p('Keywords: MCML; charge pump; PLL; Cadence Virtuoso; delay; output swing.')

h('1. Introduction')
p('A charge pump is an important part of a phase-locked loop. Its UP and DN inputs move the output voltage up or down to help control the loop. For this project, we studied a two-stage MCML charge pump operating with a 10 GHz input period. We aimed to draw and check the circuit in Virtuoso, simulate both charging and discharging, and compare the output swing and delay with values reported in [1].')

h('2. Literature Review and Research Gap')
p('The reference paper [1] combines a switch-based charge pump with an MCML current-driving stage. It reports a delay of 16.71 ps, average power of 13.19 µW, and output swing from 0 to 0.98 V at a 1 V supply. Our project follows the same general circuit idea. The paper used a 10 pF load, while our testbench has a 300 fF internal load, so the two sets of numbers are useful for a basic comparison but are not directly equivalent.')
table(['Reference','Architecture and conditions','Reported result','Relevance'],[['[1] Sivasakthi and Radhika','Two-stage switch-based + MCML charge pump; 45 nm, 1 V; paper Table 2 load 10 pF','16.71 ps minimum delay; 13.19 µW average power; 0–0.98 V swing','Topology reference; numerical values are not a matched baseline for this model/load set.']])

h('3. Proposed Work and Design Methodology')
p('The circuit has a primary switching stage and a secondary MCML stage. It uses a 50 fF internal capacitor and a 300 fF load capacitor. The testbench applies complementary UP and UP_b pulses for charging; DN = 0 V and DN_b = 1.0 V during that run. A separate control setting gives the discharging response. VDD is 1.0 V, Vbias is 0.45 V, and the output node is Vop. The schematic uses one connected analogLib ground.')
p('We used Virtuoso to check the schematic, loaded the ADE L step1_final state, and ran a 10 ns transient analysis with a 0.5 ps maximum step. We viewed charging and discharging separately in ViVA. The ADE Calculator was used to obtain delay, power, and settled output voltage from the saved results. The numerical simulator and model set are identified in the setup table below.')

newpage()
h('4. Circuit Schematic and Design Explanation')
p('Figure 1(a) shows the reference schematic diagram of the proposed Faster Current Driving Charge Pump (FCD-CP) from the research paper by Sivasakthi and Radhika [1]. The topology combines two coordinated sections: (1) a primary switch-based charge pump with switching transistors S1–S4 and interconnect capacitor Ci to minimize output glitches and cancel charge injection, and (2) a secondary MOS current mode logic (MCML) faster current driving charge pump stage consisting of PMOS active load transistors M1–M2, differential input transistors M3–M4, current-steering switches S5–S6, and bias current source M5.')
fig('paper_mcml_charge_pump_schematic.png', 'Fig. 1(a). Schematic diagram of the Faster Current Driving MCML Charge Pump (FCD-CP) from the reference research paper [1].', 4.9)

p('Figure 1(b) shows the completed transistor-level schematic capture in Cadence Virtuoso IC6.1.7 replicating this architecture. The primary stage provides switching action, while the secondary MCML stage delivers high-speed driving current to accelerate PLL acquisition. The Vop node connects to the internal 300 fF load capacitor. Transistor M5 provides the tail current biased at 0.45 V. Signal names and device sizing follow the reference design specifications.')
fig('00_mcml_charge_pump_lowercase.png', 'Fig. 1(b). Completed mcml_charge_pump schematic in Cadence Virtuoso.', 5.7)

p('Figure 2 shows the corresponding Virtuoso transient simulation testbench configured with supply rails (VDD = 1.0 V), bias voltage (Vbias = 0.45 V), differential 10 GHz input pulse sources (UP, UP_b, DN, DN_b), analogLib ground reference, and output probe Vop.')
fig('01_testbench_schematic.png', 'Fig. 2. Virtuoso transient testbench with VDD, Vbias, UP/UP_b, DN/DN_b, ground, and Vop connections.', 5.8)

p('The transient testbench simulates both charging and discharging modes under authentic 10 GHz clock stimulus. For the charging verification, complementary pulses with a 100 ps period (50% duty cycle, 1 ps rise/fall times) are applied to UP and UP_b, while DN is held at 0 V and DN_b at 1.0 V. For the discharging verification, active switching pulses are applied to DN and DN_b with UP held low and UP_b high. The internal load capacitor CL = 300 fF models the capacitive loading presented by subsequent filter and VCO stages. The tail current source transistor M5 is biased in saturation by the dedicated DC source Vbias = 0.45 V, ensuring continuous, glitch-free tail current steering through the MCML differential branches.')

newpage()
h('5. Simulation Setup and Measurement Method')
table(['Parameter','Setting / method'],[
 ['Schematic source','Checked tb_mcml_charge_pump/schematic; 22 components, zero netlisting warnings/errors at the prior testbench check.'],
 ['Simulator and model provenance','Virtuoso 6.1.7 uses gpdk045 symbols and ADE L launches the run. A local bridge uses ngspice 45.2 with FreePDK45 nominal VTG transistor models for numerical simulation. Cadence Spectre and its gpdk045 numerical model library were not used.'],
 ['Electrical conditions','VDD = 1.0 V; Vbias = 0.45 V; 27 °C; 10 GHz control period; internal CL = 300 fF; Ci = 50 fF.'],
 ['Transient','10 ns stop, 0.5 ps maximum step; independent charge and discharge runs; 80 ns runs for settled swing.'],
 ['Delay','UP/DN 0.5 V rising edge to first local Vop midpoint crossing; 10-edge mean over pulses 11–20.'],
 ['Power','−1.0 V × mean VDD-source current from 1 to 10 ns; excludes power supplied by control sources.'],
 ['Paper comparison','Use an illustrative ±10% window for delay and settled output swing; the paper does not specify this as its acceptance criterion.'],
 ['Area','Not reported: no layout or extracted cell area was measured.']])
fig('02_ade_step1_final.png','Fig. 3. Setup ADE L with initial conditions and stimuli.',6.7)

h('6. Results and Discussion')
p('The ViVA plots show Vop increasing during charging and decreasing during discharging. The 10 ns runs show the switching behavior. Longer 80 ns runs were used to read the final high and low output levels.')
fig('03_viva_charge.png','Fig. 4(a). Charging transient displayed in Cadence ViVA from the saved PSF result.',6.7)
fig('04_viva_discharge.png','Fig. 4(b). Discharging transient in a separate Cadence ViVA view from the discharge PSF.',6.7)
table(['Measured quantity','Charging','Discharging'],[
 ['Ten-edge mean delay','13.811 ps','15.447 ps'],
 ['Average VDD power, 1–10 ns','22.528 µW','16.097 µW'],
 ['Settled Vop level at 80 ns','0.992875 V','−0.000648 V']])
p('The final high output is about 0.992875 V and the final low output is about −0.000648 V, giving a measured voltage swing of 0.993524 V. This is close to the 0.98 V output swing stated in [1], with a 1.38% numerical difference. The 300 fF load and model set differ from the paper, so the comparison is approximate.')
fig('08_delay_discharge_mean.png','Fig. 5. ADE Calculator result for the average discharging delay: 15.447 ps.',6.7)
fig('14_swing_combined.png','Fig. 6. ADE Calculator result for the output voltage swing: 0.993524 V.',6.7)

newpage()
h('7. Performance Comparison')
table(['Design / source','Technology, load','Delay','Power','Output swing'],[
 ['Published [1]','45 nm CMOS; 10 pF paper setup','16.71 ps minimum','13.19 µW average','0–0.98 V reported swing'],
 ['This work: charge','45 nm nominal VTG models; 300 fF internal CL','13.811 ps mean','22.528 µW VDD','0.993524 V settled swing (combined modes)'],
 ['This work: discharge','Same models and load','15.447 ps mean','16.097 µW VDD','0.993524 V combined-mode swing']])
p('The measured discharge delay of 15.447 ps is 7.56% below the paper’s 16.71 ps value. The measured output swing of 0.993524 V is 1.38% above the paper’s 0.98 V result. These two values fall within a 10% numerical comparison window. The power values are reported as measured, without a pass/fail threshold. Because the paper used a different load and models, this is a simple project comparison rather than proof of identical performance.')
fig('09_delay_paper_difference.png','Fig. 7. ADE Calculator shows the 7.56% delay difference from the paper.',6.7)

h('8. Conclusion and Future Scope')
p('We successfully completed the schematic, testbench, and transient simulation of the MCML charge pump. The output rises during charging and falls during discharging as expected. The measured delay and output voltage swing are within a 10% numerical comparison window of the values reported in [1]. This meets the main aims of our fifth-semester VLSI System Design mini project. A useful next step would be to repeat the comparison with the same load and process models as the paper and then explore a physical layout.')

h('References')
p('[1] M. Sivasakthi and P. Radhika, “A high-speed MCML charge pump design at 10 GHz frequency in 45 nm CMOS technology for PLL application,” Analog Integrated Circuits and Signal Processing, vol. 118, pp. 49–66, 2024, doi: 10.1007/s10470-023-02225-0.')

h('Appendix A. Additional Simulation Screenshots')
p('The following screenshots show the remaining Calculator evaluations for individual edges, averages, power, and final output levels. Figures 1–7 in the report show the schematic, setup, waveforms, delay comparison, and output swing.')
fig('05_delay_charge_edge.png','Fig. A1. Charging delay for one UP pulse: 13.827 ps.',6.7)
fig('06_delay_charge_mean.png','Fig. A2. Average charging delay over ten pulses: 13.811 ps.',6.7)
fig('07_delay_discharge_edge.png','Fig. A3. Discharging delay for one DN pulse: 15.460 ps.',6.7)
fig('10_power_charge.png','Fig. A4. Average VDD power during charging: 22.528 µW.',6.7)
fig('11_power_discharge.png','Fig. A5. Average VDD power during discharging: 16.097 µW.',6.7)
fig('12_swing_charge_high.png','Fig. A6. Settled Vop high level from the charging run.',6.7)
fig('13_swing_discharge_low.png','Fig. A7. Settled Vop low level from the discharging run.',6.7)

props=doc.core_properties
props.title='Design and Simulation of a 10 GHz MCML Charge Pump for PLL Applications'
props.subject='BECE303L VLSI System Design mini project report'
props.author='Shivam Kumar; Pragyan Jain; K Navin Aakash'
props.keywords='MCML, charge pump, PLL, Virtuoso, delay'
doc.save(OUT)
print('Saved:', OUT)

import shutil, subprocess
ROOT_DOCX = Path('/home/shivam/Projects/VLSI/Final_MCML_Charge_Pump_Mini_Project_Report.docx')
ROOT_PDF = Path('/home/shivam/Projects/VLSI/Final_MCML_Charge_Pump_Mini_Project_Report.pdf')
HERE_PDF = HERE/'Final_MCML_Charge_Pump_Mini_Project_Report.pdf'

shutil.copyfile(OUT, ROOT_DOCX)
print('Copied DOCX to:', ROOT_DOCX)

print('Rendering PDF with LibreOffice...')
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', str(ROOT_DOCX), '--outdir', '/home/shivam/Projects/VLSI'], check=True)
shutil.copyfile(ROOT_PDF, HERE_PDF)
print('Rendered PDF at:', ROOT_PDF)
print('Copied PDF to:', HERE_PDF)
