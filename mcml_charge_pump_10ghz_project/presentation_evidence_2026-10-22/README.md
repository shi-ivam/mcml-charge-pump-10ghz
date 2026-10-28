# Virtuoso ADE L presentation evidence (22 October 2026)

Open [Virtuoso_ADE_Calculator_Evidence.pdf](Virtuoso_ADE_Calculator_Evidence.pdf).
The `screenshots/` directory contains the 16 unaltered application-window captures
used in the PDF: two schematic views, the loaded ADE state, charging and
discharging ViVA views, and eleven successfully evaluated Calculator fields.
`manifest.json` records SHA-256 hashes for the PDF and each screenshot.

The schematic and ADE/ViVA/Calculator windows are real Virtuoso 6.1.7 windows.
The numerical solver for these results is **ngspice 45.2**, using FreePDK45
nominal VTG models. ADE L uses a local adapter in its `spectre` simulator slot.
The screenshots were framed by capturing the application windows; their contents
were not redrawn or edited. The PDF captions identify the solver and model set.

The transient Calculator fields read the binary PSF result directories written
after the ADE **Netlist and Run** action. The DC mismatch Calculator field does
arithmetic on the measured 0.5 V row of
`../mcml_cp_sim/verified_flow/results/dc_compliance.csv`; the current machine
does not expose this DC sweep as an ADE Calculator result set. The output voltage
swing and the 10% current-compliance dynamic range are distinct measurements.
The former is 993.524 mV; the latter has no valid interval containing 0.5 V.

The original DUT schematic includes printed values from the research paper.
Those design annotations are comparison targets, not the measured values in this
package. The paper also used a 10 pF load and different process models; this
project's testbench uses the DUT's 300 fF internal load.

`capture_calculator.py` documents the GUI actions used to paste and evaluate
the fields. `make_pdf.py` rebuilds the PDF from the PNG captures and current
`metrics.json`/`dc_compliance.csv` data. The capture script depends on the
isolated `:98` Virtuoso session and the local X11 automation binaries in `/tmp`.
