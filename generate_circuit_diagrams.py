#!/usr/bin/env python3
"""
Generate comprehensive, ultra-high-resolution transistor-level circuit schematics
for the Cadence Virtuoso CMOS Charge Pump presentation using Matplotlib.
Includes:
1. Complete Multi-Stage Cross-Coupled CMOS Charge Pump Transistor Schematic
2. Cross-Coupled Unit Cell Dynamic Latch Detailed Schematic
3. Side-by-Side Architectural Circuit Comparison (Dickson vs Cross-Coupled)
4. Comprehensive 4-Stage Transistor Level Cadence Schematic View
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines

OUTPUT_DIR = "/home/shivam/Projects/VLSI/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Custom Circuit Drawing Helper Functions in pure Matplotlib for 100% precision
def draw_nmos(ax, x, y, label="MN", w_l="(W/L)n", flip_v=False, flip_h=False, scale=1.0, color="#111111", text_color="#1F6C9F"):
    """Draw a standard 4-terminal NMOS symbol with body/bulk connection."""
    s = scale
    dy = -1.0 * s if flip_v else 1.0 * s
    dx = -1.0 * s if flip_h else 1.0 * s
    
    # Gate line
    ax.plot([x - 0.4*s, x - 0.4*s], [y - 0.5*s, y + 0.5*s], color=color, lw=1.8)
    # Gate terminal
    ax.plot([x - 0.8*s, x - 0.4*s], [y, y], color=color, lw=1.5)
    
    # Channel bars (Drain, Source, Body)
    ax.plot([x - 0.2*s, x - 0.2*s], [y + 0.2*s, y + 0.6*s], color=color, lw=2.2) # Drain
    ax.plot([x - 0.2*s, x - 0.2*s], [y - 0.2*s, y + 0.2*s], color=color, lw=2.2) # Body
    ax.plot([x - 0.2*s, x - 0.2*s], [y - 0.6*s, y - 0.2*s], color=color, lw=2.2) # Source
    
    # Drain lead
    ax.plot([x - 0.2*s, x + 0.4*s, x + 0.4*s], [y + 0.4*s, y + 0.4*s, y + 0.8*s], color=color, lw=1.5)
    # Source lead
    ax.plot([x - 0.2*s, x + 0.4*s, x + 0.4*s], [y - 0.4*s, y - 0.4*s, y - 0.8*s], color=color, lw=1.5)
    # Bulk lead & arrow (inward for NMOS)
    ax.plot([x - 0.2*s, x + 0.4*s], [y, y], color=color, lw=1.2, linestyle=':')
    ax.annotate('', xy=(x - 0.18*s, y), xytext=(x + 0.15*s, y),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2, mutation_scale=8))
    
    # Labels
    ax.text(x + 0.55*s, y + 0.2*s, label, fontsize=9.5*s, weight='bold', color=text_color, va='center')
    if w_l:
        ax.text(x + 0.55*s, y - 0.25*s, w_l, fontsize=8*s, color='#555552', va='center', family='monospace')
    
    return {
        'gate': (x - 0.8*s, y),
        'drain': (x + 0.4*s, y + 0.8*s),
        'source': (x + 0.4*s, y - 0.8*s),
        'bulk': (x + 0.4*s, y)
    }

def draw_pmos(ax, x, y, label="MP", w_l="(W/L)p", scale=1.0, color="#111111", text_color="#346538"):
    """Draw a standard 4-terminal PMOS symbol with inversion bubble."""
    s = scale
    
    # Inversion Bubble on Gate
    circle = patches.Circle((x - 0.5*s, y), 0.1*s, fill=False, color=color, lw=1.5)
    ax.add_patch(circle)
    # Gate terminal
    ax.plot([x - 0.9*s, x - 0.6*s], [y, y], color=color, lw=1.5)
    # Gate plate
    ax.plot([x - 0.35*s, x - 0.35*s], [y - 0.5*s, y + 0.5*s], color=color, lw=1.8)
    
    # Channel bars
    ax.plot([x - 0.18*s, x - 0.18*s], [y + 0.2*s, y + 0.6*s], color=color, lw=2.2) # Source
    ax.plot([x - 0.18*s, x - 0.18*s], [y - 0.2*s, y + 0.2*s], color=color, lw=2.2) # Bulk
    ax.plot([x - 0.18*s, x - 0.18*s], [y - 0.6*s, y - 0.2*s], color=color, lw=2.2) # Drain
    
    # Source lead
    ax.plot([x - 0.18*s, x + 0.4*s, x + 0.4*s], [y + 0.4*s, y + 0.4*s, y + 0.8*s], color=color, lw=1.5)
    # Drain lead
    ax.plot([x - 0.18*s, x + 0.4*s, x + 0.4*s], [y - 0.4*s, y - 0.4*s, y - 0.8*s], color=color, lw=1.5)
    # Bulk lead & arrow (outward for PMOS)
    ax.plot([x - 0.18*s, x + 0.4*s], [y, y], color=color, lw=1.2, linestyle=':')
    ax.annotate('', xy=(x + 0.2*s, y), xytext=(x - 0.1*s, y),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2, mutation_scale=8))
    
    # Labels
    ax.text(x + 0.55*s, y + 0.2*s, label, fontsize=9.5*s, weight='bold', color=text_color, va='center')
    if w_l:
        ax.text(x + 0.55*s, y - 0.25*s, w_l, fontsize=8*s, color='#555552', va='center', family='monospace')
        
    return {
        'gate': (x - 0.9*s, y),
        'source': (x + 0.4*s, y + 0.8*s),
        'drain': (x + 0.4*s, y - 0.8*s),
        'bulk': (x + 0.4*s, y)
    }

def draw_cap(ax, x1, y1, x2, y2, label="C", val="", color="#111111"):
    """Draw a parallel plate capacitor between two points."""
    # Midpoint
    mx, my = (x1 + x2)/2, (y1 + y2)/2
    dx, dy = x2 - x1, y2 - y1
    L = np.sqrt(dx**2 + dy**2)
    ux, uy = dx/L, dy/L # unit vector
    px, py = -uy, ux # perpendicular unit vector
    
    gap = 0.12
    plate_w = 0.35
    
    # Lead 1
    ax.plot([x1, mx - ux*gap], [y1, my - uy*gap], color=color, lw=1.5)
    # Plate 1
    ax.plot([mx - ux*gap - px*plate_w, mx - ux*gap + px*plate_w],
            [my - uy*gap - py*plate_w, my - uy*gap + py*plate_w], color=color, lw=2.5)
    
    # Lead 2
    ax.plot([mx + ux*gap, x2], [my + uy*gap, y2], color=color, lw=1.5)
    # Plate 2
    ax.plot([mx + ux*gap - px*plate_w, mx + ux*gap + px*plate_w],
            [my + uy*gap - py*plate_w, my + uy*gap + py*plate_w], color=color, lw=2.5)
    
    # Label
    ax.text(mx + px*0.45, my + py*0.45, label, fontsize=9, weight='bold', color='#111111', ha='center', va='center')
    if val:
        ax.text(mx + px*0.45, my + py*0.45 - 0.25, val, fontsize=7.5, color='#787774', ha='center', va='center', family='monospace')

def draw_dot(ax, x, y, color="#111111", radius=0.07):
    circle = patches.Circle((x, y), radius, facecolor=color, edgecolor=color, zorder=5)
    ax.add_patch(circle)


# ==============================================================================
# CIRCUIT 1: Complete 4-Stage Transistor-Level CMOS Charge Pump Schematic
# ==============================================================================
def generate_full_4stage_cmos_schematic():
    print("Generating Comprehensive 4-Stage CMOS Charge Pump Circuit Diagram...")
    fig, ax = plt.subplots(figsize=(14, 7.2), dpi=300)
    ax.set_xlim(-1, 19)
    ax.set_ylim(-1, 9)
    ax.axis('off')
    
    # Background card box
    rect = patches.FancyBboxPatch((-0.8, -0.8), 19.6, 9.6, boxstyle="round,pad=0.2",
                                  facecolor="#FFFFFF", edgecolor="#D1D1CE", lw=1.2)
    ax.add_patch(rect)
    
    # Title Header
    ax.text(9.0, 8.3, "4-Stage Cross-Coupled CMOS Charge Pump: Full Transistor Schematic",
            fontsize=14, weight='bold', color='#111111', ha='center')
    ax.text(9.0, 7.85, "Cadence Virtuoso Transistor-Level Implementation with Dynamic Latch Cells & Non-Overlapping Clocks",
            fontsize=10, color='#555552', ha='center')
    
    # Input VIN
    ax.text(0.0, 4.0, "VIN\n(1.8V)", fontsize=11, weight='bold', color='#1F6C9F', ha='center', va='center')
    draw_dot(ax, 0.6, 4.0, '#1F6C9F')
    
    stage_x_starts = [1.2, 5.0, 8.8, 12.6]
    
    # Draw connection from VIN into Stage 1
    ax.plot([0.6, stage_x_starts[0]], [4.0, 4.0], color='#111111', lw=1.8)
    
    for i, sx in enumerate(stage_x_starts):
        st_num = i + 1
        
        # Stage boundary dashed box
        stage_box = patches.FancyBboxPatch((sx - 0.2, 0.2), 3.4, 6.8, boxstyle="round,pad=0.1",
                                           facecolor="#FBFBFA", edgecolor="#EAEAEA", lw=1.0, linestyle='--')
        ax.add_patch(stage_box)
        ax.text(sx + 1.5, 6.7, f"STAGE {st_num}", fontsize=10, weight='bold', color='#111111', ha='center')
        
        # Upper branch NMOS (MNa) and PMOS (MPa)
        mna = draw_nmos(ax, sx + 0.8, 4.8, label=f"MN{st_num}A", w_l="24µ/180n", scale=0.75, text_color='#1F6C9F')
        mpa = draw_pmos(ax, sx + 2.2, 4.8, label=f"MP{st_num}A", w_l="48µ/180n", scale=0.75, text_color='#346538')
        
        # Lower branch NMOS (MNb) and PMOS (MPb)
        mnb = draw_nmos(ax, sx + 0.8, 2.2, label=f"MN{st_num}B", w_l="24µ/180n", scale=0.75, text_color='#1F6C9F')
        mpb = draw_pmos(ax, sx + 2.2, 2.2, label=f"MP{st_num}B", w_l="48µ/180n", scale=0.75, text_color='#346538')
        
        # Intermediate Nodes A and B
        node_a = (sx + 1.5, 4.8)
        node_b = (sx + 1.5, 2.2)
        draw_dot(ax, node_a[0], node_a[1], '#956400')
        draw_dot(ax, node_b[0], node_b[1], '#956400')
        ax.text(node_a[0], node_a[1] + 0.35, f"V_{st_num}A", fontsize=8, weight='bold', color='#956400', ha='center')
        ax.text(node_b[0], node_b[1] - 0.45, f"V_{st_num}B", fontsize=8, weight='bold', color='#956400', ha='center')
        
        # Connect MN Drain to Node and PMOS Source to Node
        ax.plot([mna['drain'][0], node_a[0]], [mna['drain'][1], node_a[1]], color='#111111', lw=1.5)
        ax.plot([node_a[0], mpa['source'][0]], [node_a[1], mpa['source'][1]], color='#111111', lw=1.5)
        
        ax.plot([mnb['drain'][0], node_b[0]], [mnb['drain'][1], node_b[1]], color='#111111', lw=1.5)
        ax.plot([node_b[0], mpb['source'][0]], [node_b[1], mpb['source'][1]], color='#111111', lw=1.5)
        
        # Input feed from previous stage to NMOS sources
        in_node = (sx, 3.5)
        draw_dot(ax, in_node[0], in_node[1], '#111111')
        ax.plot([in_node[0], mna['source'][0], mna['source'][0]], [in_node[1], in_node[1], mna['source'][1]], color='#111111', lw=1.5)
        ax.plot([in_node[0], mnb['source'][0], mnb['source'][0]], [in_node[1], in_node[1], mnb['source'][1]], color='#111111', lw=1.5)
        
        # Output combine from PMOS drains
        out_node = (sx + 3.0, 3.5)
        draw_dot(ax, out_node[0], out_node[1], '#346538')
        ax.plot([mpa['drain'][0], out_node[0], out_node[0]], [mpa['drain'][1], mpa['drain'][1], out_node[1]], color='#111111', lw=1.5)
        ax.plot([mpb['drain'][0], out_node[0], out_node[0]], [mpb['drain'][1], mpb['drain'][1], out_node[1]], color='#111111', lw=1.5)
        
        # Cross-coupling gate lines between A and B
        # Gate MNa connected to Node B
        ax.plot([mna['gate'][0], mna['gate'][0] - 0.2, sx + 1.2, node_b[0]],
                [mna['gate'][1], mna['gate'][1] - 0.8, node_b[1] + 0.6, node_b[1]], color='#956400', lw=1.2, linestyle=':')
        # Gate MNb connected to Node A
        ax.plot([mnb['gate'][0], mnb['gate'][0] - 0.2, sx + 1.2, node_a[0]],
                [mnb['gate'][1], mnb['gate'][1] + 0.8, node_a[1] - 0.6, node_a[1]], color='#1F6C9F', lw=1.2, linestyle=':')
        
        # Gate MPa connected to Node B
        ax.plot([mpa['gate'][0], mpa['gate'][0] + 0.2, node_b[0] + 0.3, node_b[0]],
                [mpa['gate'][1], mpa['gate'][1] - 0.8, node_b[1] + 0.5, node_b[1]], color='#956400', lw=1.2, linestyle=':')
        # Gate MPb connected to Node A
        ax.plot([mpb['gate'][0], mpb['gate'][0] + 0.2, node_a[0] + 0.3, node_a[0]],
                [mpb['gate'][1], mpb['gate'][1] + 0.8, node_a[1] - 0.5, node_a[1]], color='#1F6C9F', lw=1.2, linestyle=':')
        
        # Pumping Capacitors
        clk_label_top = "CLK (Φ1)" if st_num % 2 == 1 else "CLKB (Φ2)"
        clk_label_bot = "CLKB (Φ2)" if st_num % 2 == 1 else "CLK (Φ1)"
        clk_color_top = '#956400' if st_num % 2 == 1 else '#1F6C9F'
        clk_color_bot = '#1F6C9F' if st_num % 2 == 1 else '#956400'
        
        draw_cap(ax, node_a[0], node_a[1], node_a[0], 6.0, label=f"C{st_num}A", val="15pF")
        draw_dot(ax, node_a[0], 6.0, clk_color_top)
        ax.text(node_a[0], 6.25, clk_label_top, fontsize=7.5, weight='bold', color=clk_color_top, ha='center')
        
        draw_cap(ax, node_b[0], node_b[1], node_b[0], 1.0, label=f"C{st_num}B", val="15pF")
        draw_dot(ax, node_b[0], 1.0, clk_color_bot)
        ax.text(node_b[0], 0.75, clk_label_bot, fontsize=7.5, weight='bold', color=clk_color_bot, ha='center')
        
        # Inter-stage wire
        if i < 3:
            next_sx = stage_x_starts[i+1]
            ax.plot([out_node[0], next_sx], [out_node[1], out_node[1]], color='#111111', lw=1.8)
            ax.annotate('', xy=(next_sx, out_node[1]), xytext=(out_node[0], out_node[1]),
                        arrowprops=dict(arrowstyle="->", color="#111111", lw=1.5, mutation_scale=10))
    
    # Final Output Stage at stage 4
    final_out_x = stage_x_starts[-1] + 3.0
    ax.plot([final_out_x, 17.2], [3.5, 3.5], color='#346538', lw=2.2)
    draw_dot(ax, 17.2, 3.5, '#346538')
    
    # Load Capacitor & Current Load
    draw_cap(ax, 17.2, 3.5, 17.2, 1.5, label="C_LOAD", val="50pF")
    # Ground symbol for C_LOAD
    ax.plot([16.9, 17.5], [1.5, 1.5], color='#111111', lw=1.8)
    ax.plot([17.0, 17.4], [1.35, 1.35], color='#111111', lw=1.4)
    ax.plot([17.1, 17.3], [1.2, 1.2], color='#111111', lw=1.0)
    
    # Current load source
    ax.plot([17.2, 18.2, 18.2], [3.5, 3.5, 2.7], color='#111111', lw=1.5)
    circle_i = patches.Circle((18.2, 2.3), 0.35, facecolor="#FFFFFF", edgecolor="#111111", lw=1.5)
    ax.add_patch(circle_i)
    ax.annotate('', xy=(18.2, 2.05), xytext=(18.2, 2.55),
                arrowprops=dict(arrowstyle="->", color="#111111", lw=1.4, mutation_scale=8))
    ax.plot([18.2, 18.2], [1.95, 1.5], color='#111111', lw=1.5)
    # Ground for I_load
    ax.plot([17.9, 18.5], [1.5, 1.5], color='#111111', lw=1.8)
    ax.plot([18.0, 18.4], [1.35, 1.35], color='#111111', lw=1.4)
    ax.plot([18.1, 18.3], [1.2, 1.2], color='#111111', lw=1.0)
    ax.text(18.2, 3.0, "I_LOAD\n(1-5 mA)", fontsize=8, color='#555552', ha='center')
    
    # VOUT Terminal Label
    ax.text(17.2, 4.2, "VOUT\n(7.4V)", fontsize=12, weight='bold', color='#346538', ha='center', va='bottom')
    
    # Footer annotation
    ax.text(9.0, 0.4, "All bulk terminals correctly biased (NMOS to GND, PMOS to local high-potential N-well) to prevent forward junction latchup.",
            fontsize=8.5, color='#787774', ha='center', style='italic')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "complete_4stage_cmos_charge_pump_schematic.png"), dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()


# ==============================================================================
# CIRCUIT 2: Detailed Cross-Coupled Unit Cell Dynamic Operation
# ==============================================================================
def generate_unit_cell_detail_schematic():
    print("Generating Detailed Unit Cell Transistor Diagram...")
    fig, ax = plt.subplots(figsize=(10, 6.0), dpi=300)
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 8.5)
    ax.axis('off')
    
    # Card container
    rect = patches.FancyBboxPatch((-0.8, -0.8), 11.6, 9.1, boxstyle="round,pad=0.2",
                                  facecolor="#FFFFFF", edgecolor="#D1D1CE", lw=1.2)
    ax.add_patch(rect)
    
    ax.text(5.0, 7.8, "Cross-Coupled CMOS Dynamic Latch Stage (Transistor Level)",
            fontsize=13, weight='bold', color='#111111', ha='center')
    ax.text(5.0, 7.35, "Full-Swing Dynamic Gate Drive Eliminates Diode V_th Voltage Drop",
            fontsize=9.5, color='#555552', ha='center')
    
    # VIN input
    ax.text(0.2, 3.8, "V_IN(i)", fontsize=11, weight='bold', color='#1F6C9F', ha='center', va='center')
    draw_dot(ax, 0.8, 3.8, '#1F6C9F')
    
    # Transistors
    mna = draw_nmos(ax, 2.5, 5.2, label="MN_A", w_l="W=24µm, L=180nm", scale=1.0, text_color='#1F6C9F')
    mpa = draw_pmos(ax, 6.8, 5.2, label="MP_A", w_l="W=48µm, L=180nm", scale=1.0, text_color='#346538')
    
    mnb = draw_nmos(ax, 2.5, 2.2, label="MN_B", w_l="W=24µm, L=180nm", scale=1.0, text_color='#1F6C9F')
    mpb = draw_pmos(ax, 6.8, 2.2, label="MP_B", w_l="W=48µm, L=180nm", scale=1.0, text_color='#346538')
    
    # Central Pumping Nodes
    node_a = (4.6, 5.2)
    node_b = (4.6, 2.2)
    draw_dot(ax, node_a[0], node_a[1], '#956400', radius=0.1)
    draw_dot(ax, node_b[0], node_b[1], '#956400', radius=0.1)
    ax.text(node_a[0], node_a[1] + 0.45, "Internal Node A (V_A)", fontsize=9.5, weight='bold', color='#956400', ha='center')
    ax.text(node_b[0], node_b[1] - 0.55, "Internal Node B (V_B)", fontsize=9.5, weight='bold', color='#956400', ha='center')
    
    # Wiring
    ax.plot([0.8, 1.5, 1.5], [3.8, 3.8, 4.4], color='#111111', lw=1.6)
    ax.plot([1.5, mna['source'][0], mna['source'][0]], [4.4, 4.4, mna['source'][1]], color='#111111', lw=1.6)
    ax.plot([0.8, 1.5, 1.5], [3.8, 3.8, 3.0], color='#111111', lw=1.6)
    ax.plot([1.5, mnb['source'][0], mnb['source'][0]], [3.0, 3.0, mnb['source'][1]], color='#111111', lw=1.6)
    
    ax.plot([mna['drain'][0], node_a[0], mpa['source'][0]], [node_a[1], node_a[1], node_a[1]], color='#111111', lw=1.8)
    ax.plot([mnb['drain'][0], node_b[0], mpb['source'][0]], [node_b[1], node_b[1], node_b[1]], color='#111111', lw=1.8)
    
    # Capacitors
    draw_cap(ax, node_a[0], node_a[1], node_a[0], 6.8, label="C_pumpA (15pF)", color='#111111')
    draw_dot(ax, node_a[0], 6.8, '#956400')
    ax.text(node_a[0], 7.15, "CLK (Phase 1)", fontsize=9, weight='bold', color='#956400', ha='center')
    
    draw_cap(ax, node_b[0], node_b[1], node_b[0], 0.6, label="C_pumpB (15pF)", color='#111111')
    draw_dot(ax, node_b[0], 0.6, '#1F6C9F')
    ax.text(node_b[0], 0.25, "CLKB (Phase 2)", fontsize=9, weight='bold', color='#1F6C9F', ha='center')
    
    # Cross coupling
    ax.plot([mna['gate'][0], 1.2, 4.0, node_b[0]], [mna['gate'][1], 4.2, 2.7, node_b[1]], color='#956400', lw=1.4, linestyle='--')
    ax.plot([mnb['gate'][0], 1.2, 4.0, node_a[0]], [mnb['gate'][1], 3.2, 4.7, node_a[1]], color='#1F6C9F', lw=1.4, linestyle='--')
    
    ax.plot([mpa['gate'][0], 7.8, 5.2, node_b[0]], [mpa['gate'][1], 4.2, 2.7, node_b[1]], color='#956400', lw=1.4, linestyle='--')
    ax.plot([mpb['gate'][0], 7.8, 5.2, node_a[0]], [mpb['gate'][1], 3.2, 4.7, node_a[1]], color='#1F6C9F', lw=1.4, linestyle='--')
    
    # Output combine
    ax.plot([mpa['drain'][0], 8.8, 8.8], [mpa['drain'][1], mpa['drain'][1], 3.8], color='#111111', lw=1.6)
    ax.plot([mpb['drain'][0], 8.8, 8.8], [mpb['drain'][1], mpb['drain'][1], 3.8], color='#111111', lw=1.6)
    ax.plot([8.8, 9.8], [3.8, 3.8], color='#346538', lw=2.2)
    draw_dot(ax, 9.8, 3.8, '#346538')
    ax.text(9.8, 4.3, "V_OUT(i)\n(Boosted)", fontsize=10, weight='bold', color='#346538', ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "cross_coupled_unit_cell_detailed.png"), dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()


# ==============================================================================
# CIRCUIT 3: Dickson vs Cross-Coupled Architectural Comparison
# ==============================================================================
def generate_comparison_diagram():
    print("Generating Architectural Comparison Diagram...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.0), dpi=300)
    
    # Subplot 1: Conventional Dickson
    ax1.set_xlim(-0.5, 10.5)
    ax1.set_ylim(-0.5, 3.5)
    ax1.axis('off')
    rect1 = patches.FancyBboxPatch((-0.3, -0.3), 10.6, 3.6, boxstyle="round,pad=0.1",
                                  facecolor="#FFFFFF", edgecolor="#D1D1CE", lw=1.0)
    ax1.add_patch(rect1)
    ax1.text(0.2, 3.0, "A. Conventional Dickson Charge Pump (Diode-Connected MOS)", fontsize=11, weight='bold', color='#9F2F2D')
    ax1.text(0.2, 2.65, "Loss mechanism: Vth drop per stage + substrate body effect -> V_out = V_in + N(V_clk - Vth)", fontsize=8.5, color='#787774')
    
    # Diodes
    d_x = [1.2, 3.2, 5.2, 7.2]
    ax1.plot([0.5, 1.2], [1.5, 1.5], color='#111111', lw=1.5)
    ax1.text(0.3, 1.5, "VIN", fontsize=9.5, weight='bold', color='#1F6C9F', va='center')
    
    for idx, x in enumerate(d_x):
        m = draw_nmos(ax1, x, 1.5, label=f"M{idx+1}", w_l="Diode", scale=0.65, text_color='#9F2F2D')
        # Diode connection
        ax1.plot([m['gate'][0], m['drain'][0]], [m['gate'][1], m['drain'][1]], color='#9F2F2D', lw=1.0)
        draw_dot(ax1, m['drain'][0], m['drain'][1], '#111111', radius=0.05)
        
        # Capacitors
        clk_txt = "CLK" if idx % 2 == 0 else "CLKB"
        draw_cap(ax1, m['drain'][0], 1.5, m['drain'][0], 0.3, label=f"C{idx+1}", color='#111111')
        ax1.text(m['drain'][0], 0.05, clk_txt, fontsize=7.5, weight='bold', color='#956400', ha='center')
        
        if idx < 3:
            ax1.plot([m['drain'][0], d_x[idx+1] - 0.5], [1.5, 1.5], color='#111111', lw=1.5)
        else:
            ax1.plot([m['drain'][0], 9.5], [1.5, 1.5], color='#9F2F2D', lw=1.8)
            draw_dot(ax1, 9.5, 1.5, '#9F2F2D')
            ax1.text(9.5, 1.85, "VOUT\n(Reduced by 4·Vth)", fontsize=8.5, weight='bold', color='#9F2F2D', ha='center')
            
    # Subplot 2: Cross-Coupled CMOS
    ax2.set_xlim(-0.5, 10.5)
    ax2.set_ylim(-0.5, 3.5)
    ax2.axis('off')
    rect2 = patches.FancyBboxPatch((-0.3, -0.3), 10.6, 3.6, boxstyle="round,pad=0.1",
                                  facecolor="#FFFFFF", edgecolor="#D1D1CE", lw=1.0)
    ax2.add_patch(rect2)
    ax2.text(0.2, 3.0, "B. Proposed Cross-Coupled CMOS Charge Pump (Dynamic Latch)", fontsize=11, weight='bold', color='#346538')
    ax2.text(0.2, 2.65, "Zero Vth threshold drop via dynamic cross-coupled gate overdrive -> High voltage gain & efficiency", fontsize=8.5, color='#787774')
    
    # Block representation of 4 cross-coupled cells
    cc_x = [1.2, 3.4, 5.6, 7.8]
    ax2.plot([0.5, 1.2], [1.5, 1.5], color='#111111', lw=1.5)
    ax2.text(0.3, 1.5, "VIN", fontsize=9.5, weight='bold', color='#1F6C9F', va='center')
    
    for idx, x in enumerate(cc_x):
        cell = patches.FancyBboxPatch((x, 0.6), 1.6, 1.6, boxstyle="round,pad=0.05",
                                      facecolor="#EDF3EC", edgecolor="#346538", lw=1.2)
        ax2.add_patch(cell)
        ax2.text(x + 0.8, 1.6, f"CMOS Cell {idx+1}", fontsize=8.5, weight='bold', color='#346538', ha='center')
        ax2.text(x + 0.8, 1.2, "MN1-2 / MP1-2\nC_A / C_B", fontsize=7.0, color='#555552', ha='center', family='monospace')
        
        if idx < 3:
            ax2.plot([x + 1.6, cc_x[idx+1]], [1.4, 1.4], color='#111111', lw=1.5)
            ax2.annotate('', xy=(cc_x[idx+1], 1.4), xytext=(x + 1.6, 1.4),
                        arrowprops=dict(arrowstyle="->", color="#111111", lw=1.2, mutation_scale=8))
        else:
            ax2.plot([x + 1.6, 9.8], [1.4, 1.4], color='#346538', lw=2.2)
            draw_dot(ax2, 9.8, 1.4, '#346538')
            ax2.text(9.8, 1.8, "VOUT\n(Near Ideal 4×VIN)", fontsize=9, weight='bold', color='#346538', ha='center')
            
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dickson_vs_cross_coupled_comparison.png"), dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()


if __name__ == '__main__':
    generate_full_4stage_cmos_schematic()
    generate_unit_cell_detail_schematic()
    generate_comparison_diagram()
    print("Comprehensive circuit diagrams successfully generated!")
