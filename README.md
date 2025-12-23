# sdn-handover-comparative-analysis
implemented with Hussein Mohammad & Gebre Halefom Meresa in 2025

Comparative analysis of SDN-assisted handover strategies under Random Way Point and Random Direction mobility using Mininet-WiFi and Ryu (performance, video streaming, and controller overhead).

# SDN Handover Comparative Analysis — Mininet-WiFi & Ryu

in this Project we implement and evaluate five handover strategies for SDN-enabled WLANs (Reactive, Proactive, Load-Aware, Signal-Based, and SDN-Optimized). Experiments were run in Mininet-WiFi with the Ryu controller to compare performance under two canonical mobility models (Random Way Point and Random Direction). The study evaluates handover delay, success rate, packet loss, throughput, latency, and SDN control-plane overhead, including an application-level video streaming scenario.

---

## Motivation
Seamless mobility in dense Wi-Fi deployments is critical for latency-sensitive applications (VoIP, real-time video). Client-driven handovers are reactive and often cause high delay and packet loss. This project investigates how SDN-assisted strategies can improve handover responsiveness and stability under different mobility patterns.

---

## Implemented strategies
- **Reactive** — baseline, client-like reactive handover on threshold.  
- **Proactive** — signal-trend prediction, pre-installation of flow rules.  
- **Load-Aware** — selects APs balancing signal strength and AP load.  
- **Signal-Based** — aggressive, fast switching with hysteresis to avoid ping-pong.  
- **SDN-Optimized** — prediction + pre-installed multi-hop flows and end-to-end optimization (best overall).

---


## Requirements
- Linux environment (Ubuntu recommended)  
- Mininet-WiFi (tested version X.X) — install per Mininet-WiFi docs  
- Ryu SDN Framework  
- Open vSwitch (ovs)  
- Python 3.8+ and packages in `requirements.txt`: `psutil`, `pandas`, `matplotlib`, `numpy`, `scipy`, `flask` (if used), `mininet-wifi` (Python bindings), etc. 

---

## Quickstart (local test)
Tested on Linux with Mininet-WiFi and Ryu installed. two codes : one for controller and one for the mobility (include RD & RWP)
there are two codes ... the first code is controller code while the second code ( mobility code ) apply twice ( one with RD (2) and one with RWP (3) )

 1 - run controller on terminal 1 :  ryu-manager enhanced_controller.py

 2 - run Random direction mobility on terminal 2 : sudo python3 enhanced_topology.py --mobility RandomDirection --duration 300

 3 - run Random way point mobility on terminal 2 : sudo python3 enhanced_topology.py --mobility RandomWayPoint --duration 300


 run 1 & 2 and then 1 & 3

## Experimental methodology

Testbed: Mininet-WiFi emulated WLAN with 7 APs (central hub), 5 mobile stations, Ryu controller via OpenFlow 1.3.

Mobility: Random Way Point (RWP) and Random Direction (RD) models.

Metrics: handover delay, success rate, packet loss, throughput, latency, jitter, AP residence time, and SDN control-plane overhead.

Each run: 15–20 minutes, metrics logged every 5 seconds; strategies rotated to ensure comparable measurement windows

