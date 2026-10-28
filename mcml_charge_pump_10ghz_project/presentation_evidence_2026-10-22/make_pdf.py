#!/usr/bin/env python3
"""Assemble captured Virtuoso screenshots into a provenance-labelled PDF."""

from __future__ import annotations

import csv
from datetime import date
import hashlib
import json
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


HERE = Path(__file__).resolve().parent
SHOTS = HERE / "screenshots"
RESULTS = HERE.parent / "mcml_cp_sim/verified_flow/results"
METRICS = json.loads((RESULTS / "metrics.json").read_text())
OUT = HERE / "Virtuoso_ADE_Calculator_Evidence.pdf"
PAGE_W, PAGE_H = landscape(A3)

FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
if FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))
    FONT = "DejaVu"
else:
    FONT = "Helvetica"


def line(c: canvas.Canvas, x: float, y: float, value: str, size: float = 13,
         color=colors.HexColor("#162334")) -> None:
    c.setFillColor(color)
    c.setFont(FONT, size)
    c.drawString(x, y, value)


def footer(c: canvas.Canvas, page: int) -> None:
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(42, 49, PAGE_W - 42, 49)
    line(c, 42, 30, "Virtuoso display; ngspice 45.2 / FreePDK45 nominal VTG numerical results", 10)
    c.setFont(FONT, 10)
    c.drawRightString(PAGE_W - 42, 30, str(page))


def add_image_page(c: canvas.Canvas, page: int, filename: str, title: str,
                   caption: list[str]) -> None:
    path = SHOTS / filename
    assert path.is_file(), path
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        w, h = image.size
    line(c, 42, PAGE_H - 47, title, 18)
    top = PAGE_H - 76
    bottom = 105 + len(caption) * 19
    max_w = PAGE_W - 84
    max_h = top - bottom
    scale = min(max_w / w, max_h / h)
    dw, dh = w * scale, h * scale
    x = (PAGE_W - dw) / 2
    y = bottom + (max_h - dh) / 2
    c.drawImage(str(path), x, y, width=dw, height=dh, preserveAspectRatio=True)
    c.setStrokeColor(colors.HexColor("#94A3B8"))
    c.rect(x, y, dw, dh, stroke=1, fill=0)
    cy = bottom - 23
    for item in caption:
        line(c, 42, cy, item, 11)
        cy -= 19
    footer(c, page)
    c.showPage()


def main() -> None:
    m = METRICS
    with (RESULTS / "dc_compliance.csv").open(newline="") as file:
        dc = next(row for row in csv.DictReader(file)
                  if abs(float(row["vop_v"]) - 0.5) < 1e-12)
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("MCML charge pump: Virtuoso ADE and Calculator evidence")
    c.setAuthor("MCML charge pump project")
    line(c, 68, PAGE_H - 105, "MCML charge pump", 30)
    line(c, 68, PAGE_H - 146, "Virtuoso ADE L and Calculator evidence", 22)
    line(c, 68, PAGE_H - 199, f"Captured {date.today().isoformat()} from actual Virtuoso 6.1.7 windows.", 14)
    line(c, 68, PAGE_H - 231, "Numerical solver: ngspice 45.2. Models: FreePDK45 nominal VTG.", 14)
    line(c, 68, PAGE_H - 263, "Source: checked shivam/tb_mcml_charge_pump/schematic Virtuoso netlist.", 14)
    line(c, 68, PAGE_H - 295, "Cadence PSF waveforms are displayed and evaluated in ViVA/Calculator.", 14)
    line(c, 68, PAGE_H - 353, "Measured values", 18)
    key = [
        f"Charge delay (10-edge mean): {m['charging']['delay']['mean_ps']:.3f} ps",
        f"Discharge delay (10-edge mean): {m['discharging']['delay']['mean_ps']:.3f} ps",
        f"Paper comparison: {m['paper_delay_comparison']['absolute_error_pct']:.2f}% difference from 16.71 ps",
        f"Charge VDD power: {m['charging']['power']['power_uw']:.3f} uW; discharge: {m['discharging']['power']['power_uw']:.3f} uW",
        f"Settled output swing at 80 ns: {m['output_swing']['output_swing_v']*1e3:.3f} mV",
        f"DC mismatch at forced Vop=0.5 V: {float(dc['mismatch_pct']):.2f}%",
        "10% current-compliance criterion: no valid interval containing 0.5 V",
    ]
    for index, item in enumerate(key):
        line(c, 68, PAGE_H - 390 - index * 32, item, 13)
    line(c, 68, 104, "The paper used a 10 pF load and different process models; this project has internal CL=300 fF.", 11)
    footer(c, 1)
    c.showPage()

    pages = [
        ("00_dut_schematic.png", "DUT schematic", [
            "Actual shivam/mcml_charge_pump/schematic window. The design annotations quote paper targets, not these measured results.",
            "Internal CL=300 fF; the Vbias net drives the M5 tail gate." ]),
        ("01_testbench_schematic.png", "Transient testbench schematic", [
            "Actual shivam/tb_mcml_charge_pump/schematic window: VDD=1.0 V, Vbias=0.45 V, UP/UP_b pulses, DN=0 V, DN_b=1.0 V.",
            "Vop is the named output; one analogLib/gnd is connected; no external output capacitor." ]),
        ("02_ade_step1_final.png", "ADE L: step1_final state", [
            "The loaded testbench ADE state requests a 10 ns transient at 27 C. Its simulator slot is named spectre by ADE.",
            "The local adapter executes the numerical simulation with ngspice; the solver is identified in the run logs." ]),
        ("03_viva_charge.png", "ViVA: charging transient", [
            "Actual Cadence ViVA display of UP, UP_b, Vop, and VDD source current from the charging PSF data." ]),
        ("04_viva_discharge.png", "ViVA: discharging transient", [
            "Actual Cadence ViVA display of DN, DN_b, Vop, and VDD source current from the separate discharging PSF data." ]),
        ("05_delay_charge_edge.png", "Calculator: charge delay, pulse 16", [
            f"First local midpoint crossing after the UP edge: {m['charging']['delay']['samples'][5]['delay_ps']:.3f} ps (Calculator rounds its display)." ]),
        ("06_delay_charge_mean.png", "Calculator: charge delay, 10-edge mean", [
            f"Mean of pulses 11-20: {m['charging']['delay']['mean_ps']:.3f} ps. The input threshold is 0.5 V." ]),
        ("07_delay_discharge_edge.png", "Calculator: discharge delay, pulse 16", [
            f"First falling Vop midpoint crossing after the DN edge: {m['discharging']['delay']['samples'][5]['delay_ps']:.3f} ps." ]),
        ("08_delay_discharge_mean.png", "Calculator: discharge delay, 10-edge mean", [
            f"Mean of pulses 11-20: {m['discharging']['delay']['mean_ps']:.3f} ps; this is the larger directional mean." ]),
        ("09_delay_paper_difference.png", "Calculator: difference from paper delay", [
            f"Absolute difference from the paper's 16.71 ps TT value: {m['paper_delay_comparison']['absolute_error_pct']:.2f}%.",
            "This is numerical proximity under different load and models, not a matched-condition replication." ]),
        ("10_power_charge.png", "Calculator: charging VDD power", [
            f"-average(I(V_VDD)) x 1.0 V from 1-10 ns = {m['charging']['power']['power_uw']:.3f} uW; control sources are excluded." ]),
        ("11_power_discharge.png", "Calculator: discharging VDD power", [
            f"-average(I(V_VDD)) x 1.0 V from 1-10 ns = {m['discharging']['power']['power_uw']:.3f} uW; control sources are excluded." ]),
        ("12_swing_charge_high.png", "Calculator: settled charging high level", [
            f"Five final quiet-time samples at 80 ns average {m['output_swing']['charging']['mean_v']:.9f} V." ]),
        ("13_swing_discharge_low.png", "Calculator: settled discharging low level", [
            f"Five final quiet-time samples at 80 ns average {m['output_swing']['discharging']['mean_v']:.9f} V." ]),
        ("14_swing_combined.png", "Calculator: settled output voltage swing", [
            f"High minus low = {m['output_swing']['output_swing_v']:.9f} V ({m['output_swing']['output_swing_v']*1e3:.3f} mV).",
            "This is the transient output swing, which is distinct from DC current-compliance range." ]),
        ("15_dc_mismatch_at_0p5v.png", "Calculator: DC charge/discharge current mismatch", [
            f"Calculator arithmetic uses measured DC-sweep currents: {float(dc['i_charge_a'])*1e6:.3f} and {float(dc['i_discharge_a'])*1e6:.3f} uA at Vop=0.5 V.",
            f"Mismatch = 200*abs(Icharge-Idischarge)/(Icharge+Idischarge) = {float(dc['mismatch_pct']):.2f}%.",
            "The 10% criterion fails at its reference voltage; no valid current-compliance interval contains 0.5 V." ]),
    ]
    for number, (filename, title, caption) in enumerate(pages, start=2):
        add_image_page(c, number, filename, title, caption)
    c.save()
    manifest = {
        "pdf": OUT.name,
        "pdf_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "screenshots": {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                        for f in sorted(SHOTS.glob("*.png"))},
        "source_metrics": str(RESULTS / "metrics.json"),
        "source_dc_sweep": str(RESULTS / "dc_compliance.csv"),
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
