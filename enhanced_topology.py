#!/usr/bin/python3
"""
Enhanced Topology for Comprehensive Handover Strategy Analysis
Supports both RandomDirection and RandomWayPoint with detailed metrics
"""

import os
import sys
import time
import argparse
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mn_wifi.node import Station
from mininet.log import setLogLevel, info, error
from mininet.link import TCLink
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
import subprocess
import json

class EnhancedHandoverTestTopology:
    """Enhanced topology for comprehensive handover strategy analysis"""
    
    def __init__(self, mobility_model='RandomWayPoint', test_duration=300, enable_analysis=True):
        self.net = None
        self.controller = None
        self.stations = []
        self.access_points = []
        self.mobility_model = mobility_model
        self.test_duration = test_duration
        self.sdn_enabled = True
        # Suppress background analysis logs in CLI by default
        self.quiet_cli = True
        # Control whether automated analysis phases run
        self.enable_analysis = enable_analysis
        
        # Test scenarios for handover analysis
        self.test_scenarios = {
            'signal_degradation': {'description': 'Test handovers due to signal degradation'},
            'load_balancing': {'description': 'Test load-aware handover strategies'},
            'mobility_prediction': {'description': 'Test proactive handover prediction'},
            'sdn_optimization': {'description': 'Test SDN-optimized handover mechanisms'},
            'coverage_analysis': {'description': 'Analyze AP coverage and residence times'}
        }

    def create_enhanced_stations(self):
        """Create stations with enhanced handover configuration for analysis"""
        info("*** Creating enhanced stations for handover strategy analysis\n")
        
        # Enhanced station configurations with different mobility characteristics
        station_configs = [
            {
                'name': 'sta1', 'mac': '00:00:00:00:00:01', 'ip': '10.0.0.1/8',
                'mobility_profile': 'high_speed',
                'handover_sensitivity': 'aggressive',
                'min_x': 200, 'max_x': 800, 'min_y': 200, 'max_y': 250,
                'min_v': 15, 'max_v': 30, 'min_wt': 1, 'max_wt': 2
            },
            {
                'name': 'sta2', 'mac': '00:00:00:00:00:02', 'ip': '10.0.0.2/8',
                'mobility_profile': 'medium_speed',
                'handover_sensitivity': 'moderate',
                'min_x': 800, 'max_x': 200, 'min_y': 200, 'max_y': 250,
                'min_v': 8, 'max_v': 18, 'min_wt': 2, 'max_wt': 4
            },
            {
                'name': 'sta3', 'mac': '00:00:00:00:00:03', 'ip': '10.0.0.3/8',
                'mobility_profile': 'low_speed',
                'handover_sensitivity': 'conservative',
                'min_x': 200, 'max_x': 800, 'min_y': 600, 'max_y': 700,
                'min_v': 3, 'max_v': 10, 'min_wt': 3, 'max_wt': 6
            },
            {
                'name': 'sta4', 'mac': '00:00:00:00:00:04', 'ip': '10.0.0.4/8',
                'mobility_profile': 'variable_speed',
                'handover_sensitivity': 'adaptive',
                'min_x': 800, 'max_x': 200, 'min_y': 600, 'max_y': 700,
                'min_v': 5, 'max_v': 25, 'min_wt': 1, 'max_wt': 5
            },
            {
                'name': 'sta5', 'mac': '00:00:00:00:00:05', 'ip': '10.0.0.5/8',
                'mobility_profile': 'predictable',
                'handover_sensitivity': 'proactive',
                'min_x': 500, 'max_x': 500, 'min_y': 150, 'max_y': 800,
                'min_v': 10, 'max_v': 20, 'min_wt': 2, 'max_wt': 3
            }
        ]
        
        # Create stations with enhanced parameters
        for config in station_configs:
            if self.mobility_model == 'RandomWayPoint':
                # Use mobility boundaries for RandomWayPoint
                sta = self.net.addStation(
                    config['name'], 
                    mac=config['mac'], 
                    passwd='123456789a', 
                    encrypt='wpa2', 
                    ip=config['ip'],
                    bgscan_threshold=-65,  # More sensitive for testing
                    s_interval=2,          # Faster scanning (fixed param name)
                    l_interval=5, 
                    bgscan_module="simple",
                    min_x=config['min_x'], max_x=config['max_x'],
                    min_y=config['min_y'], max_y=config['max_y'],
                    min_v=config['min_v'], max_v=config['max_v'],
                    min_wt=config['min_wt'], max_wt=config['max_wt']
                )
            else:
                # RandomDirection - no boundary constraints in addStation
                sta = self.net.addStation(
                    config['name'], 
                    mac=config['mac'], 
                    passwd='123456789a', 
                    encrypt='wpa2', 
                    ip=config['ip'],
                    bgscan_threshold=-65,
                    s_interval=2,
                    l_interval=5, 
                    bgscan_module="simple"
                )
            
            # Store mobility profile for later analysis
            sta.mobility_profile = config['mobility_profile']
            sta.handover_sensitivity = config['handover_sensitivity']
            self.stations.append(sta)
        
        info(f"*** Created 5 enhanced stations for {self.mobility_model} analysis\n")
        for i, sta in enumerate(self.stations):
            config = station_configs[i]
            info(f"   {sta.name}: {config['mobility_profile']} mobility, {config['handover_sensitivity']} handover\n")

    def create_enhanced_access_points(self):
        """Create APs with enhanced configurations for strategy testing"""
        info("*** Creating enhanced access points for strategy analysis\n")
        
        # Enhanced AP configurations with different characteristics
        ap_configs = [
            {
                'name': 'ap1', 'dpid': '1', 'mac': '00:00:00:00:00:06',
                'position': '150,600,0', 'channel': '1', 'range': 240,
                'capacity_profile': 'standard', 'interference': 'low'
            },
            {
                'name': 'ap2', 'dpid': '2', 'mac': '00:00:00:00:00:07',
                'position': '830,600,0', 'channel': '6', 'range': 220,
                'capacity_profile': 'standard', 'interference': 'medium'
            },
            {
                'name': 'ap3', 'dpid': '3', 'mac': '00:00:00:00:00:08',
                'position': '150,200,0', 'channel': '11', 'range': 240,
                'capacity_profile': 'standard', 'interference': 'low'
            },
            {
                'name': 'ap4', 'dpid': '4', 'mac': '00:00:00:00:00:09',
                'position': '830,200,0', 'channel': '3', 'range': 220,
                'capacity_profile': 'limited', 'interference': 'high'
            },
            {
                'name': 'ap5', 'dpid': '5', 'mac': '00:00:00:00:00:10',
                'position': '500,400,0', 'channel': '7', 'range': 250,
                'capacity_profile': 'high', 'interference': 'medium'
            },
            {
                'name': 'ap6', 'dpid': '6', 'mac': '00:00:00:00:00:11',
                'position': '500,810,0', 'channel': '9', 'range': 220,
                'capacity_profile': 'standard', 'interference': 'low'
            },
            {
                'name': 'ap7', 'dpid': '7', 'mac': '00:00:00:00:00:12',
                'position': '500,100,0', 'channel': '4', 'range': 180,
                'capacity_profile': 'limited', 'interference': 'high'
            }
        ]
        
        # Create APs with enhanced configurations
        for config in ap_configs:
            # Set maxAssoc based on capacity profile
            max_assoc = {
                'limited': 6,
                'standard': 10,
                'high': 15
            }[config['capacity_profile']]
            
            ap = self.net.addAccessPoint(
                config['name'],
                dpid=config['dpid'],
                mac=config['mac'],
                ssid='handover',
                maxAssoc=max_assoc,
                channel=config['channel'],
                mode='g',
                passwd='123456789a',
                encrypt='wpa2',
                failMode="standalone",
                position=config['position'],
                range=int(config['range']),
                datapath='user'
            )
            
            # Store enhanced attributes for analysis
            ap.capacity_profile = config['capacity_profile']
            ap.interference_level = config['interference']
            self.access_points.append(ap)
        
        info(f"*** Created {len(self.access_points)} enhanced access points\n")
        for ap in self.access_points:
            info(f"   {ap.name}: {ap.capacity_profile} capacity, {ap.interference_level} interference\n")

    def create_optimized_network_links(self):
        """Create optimized network links for enhanced handover testing"""
        info("*** Creating optimized network links for handover analysis\n")
        
        # Enhanced linking strategy for better handover opportunities
        ap1, ap2, ap3, ap4, ap5, ap6, ap7 = self.access_points
        
        # Central hub topology with redundant paths
        central_links = [
            (ap5, ap1), (ap5, ap2), (ap5, ap3), (ap5, ap4),  # ap5 as central hub
            (ap5, ap6), (ap5, ap7)
        ]
        
        # Cross connections for load balancing
        cross_links = [
            (ap1, ap3), (ap2, ap4),  # Vertical connections
            (ap1, ap2), (ap3, ap4),  # Horizontal connections
            (ap6, ap1), (ap6, ap2),  # ap6 connections
            (ap7, ap3), (ap7, ap4)   # ap7 connections
        ]
        
        # Additional redundant paths for SDN optimization
        redundant_links = [
            (ap1, ap6), (ap2, ap7), (ap3, ap6), (ap4, ap7)
        ]
        
        all_links = central_links + cross_links + redundant_links
        
        for ap_a, ap_b in all_links:
            self.net.addLink(ap_a, ap_b)
        
        info("*** Enhanced network topology created:\n")
        info("   - Central hub (ap5) with full connectivity\n")
        info("   - Cross connections for load balancing\n")
        info("   - Redundant paths for SDN optimization\n")
        info(f"   - Total links: {len(all_links)}\n")

    def setup_mobility_model(self):
        """Setup mobility model with enhanced parameters for handover analysis"""
        info(f"*** Setting up {self.mobility_model} mobility with handover analysis\n")
        
        if self.mobility_model == 'RandomWayPoint':
            self._setup_random_waypoint_mobility()
        elif self.mobility_model == 'RandomDirection':
            self._setup_random_direction_mobility()
        else:
            error(f"*** Unknown mobility model: {self.mobility_model}\n")
            return False
        
        return True

    def _setup_random_waypoint_mobility(self):
        """Setup RandomWayPoint mobility with enhanced handover triggers"""
        info("*** Configuring RandomWayPoint with enhanced handover scenarios\n")
        
        # Configure mobility model
        self.net.setMobilityModel(
            time=0, 
            model='RandomWayPoint', 
            min_v=5, max_v=20,
            seed=42,
            ac_method='ssf'  # Prefer strongest signal to trigger roaming
        )
        
        # Enhanced movement patterns designed to trigger different handover scenarios
        sta1, sta2, sta3, sta4, sta5 = self.stations
        
        # Scenario 1: Fast movement for stress testing (sta1)
        self.net.mobility(sta1, 'start', time=1, position='200,200,0')   # Near ap3
        self.net.mobility(sta1, 'stop', time=100, position='800,600,0')  # Fast to ap2
        
        # Scenario 2: Load balancing test (sta2 & sta3)
        self.net.mobility(sta2, 'start', time=1, position='500,400,0')   # Start at ap5 (high capacity)
        self.net.mobility(sta2, 'stop', time=150, position='830,200,0')  # Move to ap4 (limited)
        
        self.net.mobility(sta3, 'start', time=1, position='500,400,0')   # Also start at ap5
        self.net.mobility(sta3, 'stop', time=200, position='150,600,0')  # Move to ap1
        
        # Scenario 3: Signal degradation test (sta4)
        self.net.mobility(sta4, 'start', time=1, position='830,200,0')   # Near ap4
        self.net.mobility(sta4, 'stop', time=180, position='200,700,0')  # Far movement
        
        # Scenario 4: Predictable pattern for proactive testing (sta5)
        self.net.mobility(sta5, 'start', time=1, position='500,100,0')   # Near ap7
        self.net.mobility(sta5, 'stop', time=250, position='500,810,0')  # Straight to ap6
        
        # Start mobility
        self.net.startMobility(time=1)
        info("*** RandomWayPoint mobility configured for comprehensive handover analysis\n")

    def _setup_random_direction_mobility(self):
        """Setup RandomDirection mobility with enhanced handover triggers"""
        info("*** Configuring RandomDirection with enhanced handover scenarios\n")
        
        # Configure mobility model with parameters optimized for handover analysis
        self.net.setMobilityModel(
            time=0,
            model='RandomDirection',
            max_x=1000, max_y=1000, min_x=0, min_y=0,
            min_v=3, max_v=15,  # Variable speeds for different handover scenarios
            seed=42,
            pauseTime=1.0,
            ac_method='ssf'     # Prefer strongest signal to trigger roaming
        )
        
        # Position stations for enhanced handover scenario testing
        sta1, sta2, sta3, sta4, sta5 = self.stations
        
        # Strategic initial positioning to trigger handovers
        movement_scenarios = [
            (sta1, '150,600,0', '830,200,0'),  # ap1 -> ap4 (diagonal)
            (sta2, '830,600,0', '150,200,0'),  # ap2 -> ap3 (diagonal)
            (sta3, '150,200,0', '500,810,0'),  # ap3 -> ap6 (vertical)
            (sta4, '830,200,0', '500,100,0'),  # ap4 -> ap7 (central)
            (sta5, '500,400,0', '150,600,0')   # ap5 -> ap1 (hub to edge)
        ]
        
        for i, (sta, start_pos, end_pos) in enumerate(movement_scenarios):
            self.net.mobility(sta, 'start', time=1, position=start_pos)
            # Stagger end times to create different movement patterns
            end_time = 200 + (i * 30)
            self.net.mobility(sta, 'stop', time=end_time, position=end_pos)
        
        # Start mobility
        self.net.startMobility(time=1)
        info("*** RandomDirection mobility configured for comprehensive handover analysis\n")

    def setup_enhanced_networking(self):
        """Setup enhanced networking with handover optimization"""
        info("*** Setting up enhanced networking for handover strategy testing\n")
        
        try:
            # Configure stations with enhanced handover parameters
            for i, sta in enumerate(self.stations):
                station_ip = f'10.0.0.{i+1}'
                
                # Configure network interface
                sta.cmd(f'ifconfig {sta.name}-wlan0 {station_ip}/8')
                sta.cmd(f'iwconfig {sta.name}-wlan0 power off')  # Disable power saving
                
                # Enhanced wpa_supplicant configuration for different handover sensitivities
                sensitivity_config = {
                    'aggressive': {'scan_interval': 10, 'threshold': -60, 'roam_scan_thresh': -65},
                    'moderate': {'scan_interval': 20, 'threshold': -65, 'roam_scan_thresh': -70},
                    'conservative': {'scan_interval': 30, 'threshold': -70, 'roam_scan_thresh': -75},
                    'adaptive': {'scan_interval': 15, 'threshold': -65, 'roam_scan_thresh': -68},
                    'proactive': {'scan_interval': 5, 'threshold': -60, 'roam_scan_thresh': -62}
                }
                
                config = sensitivity_config.get(sta.handover_sensitivity, sensitivity_config['moderate'])
                
                wpa_config = f"""
network={{
    ssid="handover"
    psk="123456789a"
    key_mgmt=WPA-PSK
    scan_ssid=1
    bgscan="simple:{config['scan_interval']}:{config['threshold']}:300"
}}
"""
                with open(f'/tmp/wpa_{sta.name}.conf', 'w') as f:
                    f.write(wpa_config)
                
                # Start wpa_supplicant with enhanced configuration
                sta.cmd(f'wpa_supplicant -B -i {sta.name}-wlan0 -c /tmp/wpa_{sta.name}.conf')
                
                # Configure routing
                sta.cmd(f'route add default gw 10.0.0.1 dev {sta.name}-wlan0')
                sta.cmd(f'route add -net 10.0.0.0/8 dev {sta.name}-wlan0')
                
                info(f"   ✅ {sta.name}: {sta.handover_sensitivity} handover profile configured\n")
            
            # Setup optimized ARP entries
            info("*** Setting up optimized ARP entries\n")
            for i, sta in enumerate(self.stations):
                for j in range(5):
                    if i != j:
                        target_ip = f'10.0.0.{j+1}'
                        target_mac = f'00:00:00:00:00:0{j+1}'
                        sta.cmd(f'arp -s {target_ip} {target_mac}')
            
            # Wait for network stabilization
            time.sleep(10)
            info("*** ✅ Enhanced networking configured for handover strategy testing\n")
            
        except Exception as e:
            error(f"   ❌ Enhanced networking setup error: {e}\n")

    def generate_enhanced_traffic(self):
        """Generate enhanced traffic patterns for comprehensive handover analysis"""
        info("*** Generating enhanced traffic for handover strategy analysis\n")
        
        try:
            # Different traffic patterns for different analysis scenarios
            traffic_patterns = [
                # Continuous ping for basic connectivity
                ('sta1', 'ping 10.0.0.2 -i 0.5 > /dev/null &'),
                ('sta2', 'ping 10.0.0.3 -i 0.8 > /dev/null &'),
                ('sta3', 'ping 10.0.0.4 -i 1.0 > /dev/null &'),
                ('sta4', 'ping 10.0.0.5 -i 0.7 > /dev/null &'),
                ('sta5', 'ping 10.0.0.1 -i 0.6 > /dev/null &'),
                
                # Broadcast traffic for AP discovery
                ('sta1', 'ping -b 10.255.255.255 -i 2 > /dev/null &'),
                ('sta3', 'ping -b 10.255.255.255 -i 3 > /dev/null &'),
                
                # High-frequency traffic for stress testing
                ('sta1', 'ping 10.0.0.5 -i 0.1 -s 1024 > /dev/null &'),
                ('sta2', 'ping 10.0.0.4 -i 0.2 -s 512 > /dev/null &'),
                
                # UDP traffic for throughput analysis
                ('sta3', 'iperf -u -c 10.0.0.5 -t 300 -i 10 > /dev/null &'),
                ('sta4', 'iperf -u -c 10.0.0.1 -t 300 -i 15 > /dev/null &')
            ]
            
            # Execute traffic patterns
            for sta_name, command in traffic_patterns:
                station = next((s for s in self.stations if s.name == sta_name), None)
                if station:
                    station.cmd(command)
            
            info("*** Enhanced traffic patterns started:\n")
            info("   - Continuous ping with variable intervals\n")
            info("   - Broadcast traffic for AP discovery\n")
            info("   - High-frequency stress testing traffic\n")
            info("   - UDP throughput measurement traffic\n")
            
        except Exception as e:
            error(f"*** Enhanced traffic generation failed: {e}\n")

    # ---- Helper logging methods to keep CLI clean ----
    def _print_info(self, msg):
        """Conditional console logging respecting quiet CLI."""
        if not self.quiet_cli:
            info(msg)
        # Always persist to runtime log for later review
        self._append_runtime_log(msg)

    def _append_runtime_log(self, msg):
        """Append analysis messages to a file under results/."""
        try:
            os.makedirs('results', exist_ok=True)
            with open('results/runtime_analysis.log', 'a') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                # Ensure messages end with newline
                if not msg.endswith('\n'):
                    msg = msg + '\n'
                f.write(f"[{timestamp}] {msg}")
        except Exception:
            # Best-effort logging; ignore file errors
            pass

    def notify_controller_about_test(self):
        """Notify controller about test configuration and scenarios"""
        info("*** Notifying controller about enhanced test configuration\n")
        
        try:
            # Send test configuration to controller
            test_config = {
                'mobility_model': self.mobility_model,
                'test_duration': self.test_duration,
                'station_profiles': {
                    sta.name: {
                        'mobility_profile': sta.mobility_profile,
                        'handover_sensitivity': sta.handover_sensitivity
                    } for sta in self.stations
                },
                'ap_profiles': {
                    ap.name: {
                        'capacity_profile': ap.capacity_profile,
                        'interference_level': ap.interference_level
                    } for ap in self.access_points
                },
                'test_scenarios': self.test_scenarios
            }
            
            # Try to send configuration via REST API
            import requests
            response = requests.post(
                'http://localhost:8080/test/config',
                json=test_config,
                timeout=5
            )
            info(f"   ✅ Controller notified: {response.status_code}\n")
            
        except Exception as e:
            info(f"   ℹ️  Controller notification skipped (REST API not available on controller)\n")

    def run_handover_analysis_tests(self):
        """Run comprehensive handover analysis tests"""
        self._print_info("*** Running comprehensive handover strategy analysis tests\n")
        
        test_phases = [
            {'name': 'Initial Connectivity', 'duration': 30, 'description': 'Establish baseline connectivity'},
            {'name': 'Mobility Warmup', 'duration': 60, 'description': 'Allow stations to start moving'},
            {'name': 'Strategy Testing', 'duration': 180, 'description': 'Test different handover strategies'},
            {'name': 'Load Analysis', 'duration': 90, 'description': 'Analyze load balancing effects'},
            {'name': 'Coverage Analysis', 'duration': 60, 'description': 'Analyze coverage and residence times'}
        ]
        
        start_time = time.time()
        
        for phase in test_phases:
            phase_start = time.time()
            self._print_info(f"*** TEST PHASE: {phase['name']} - {phase['description']}\n")
            self._print_info(f"*** Duration: {phase['duration']} seconds\n")
            
            # Monitor phase progress
            while time.time() - phase_start < phase['duration']:
                elapsed = time.time() - phase_start
                remaining = phase['duration'] - elapsed
                
                # Log progress every 30 seconds
                if int(elapsed) % 30 == 0 and elapsed > 0:
                    self._print_info(f"   Phase progress: {elapsed:.0f}s/{phase['duration']}s ({elapsed/phase['duration']*100:.1f}%)\n")
                    # Log station status to file without spamming CLI
                    self._log_current_station_status(silent=True)
                
                time.sleep(10)
            
            self._print_info(f"*** COMPLETED: {phase['name']}\n")
        
        total_duration = time.time() - start_time
        self._print_info(f"*** ✅ ALL TEST PHASES COMPLETED in {total_duration:.1f} seconds\n")

    def _log_current_station_status(self, silent=False):
        """Log current status of all stations; silent=True writes to file only."""
        header = "   Current station status:\n"
        if not self.quiet_cli and not silent:
            info(header)
        else:
            self._append_runtime_log(header)
        for sta in self.stations:
            try:
                # Get current WiFi connection info
                wifi_info = sta.cmd('iwconfig 2>/dev/null | grep "Access Point"')
                link_info = sta.cmd(f'iW dev {sta.name}-wlan0 link 2>/dev/null') or sta.cmd(f'iw dev {sta.name}-wlan0 link 2>/dev/null')
                if wifi_info:
                    msg = f"     {sta.name}: {wifi_info.strip()}\n"
                    if not self.quiet_cli and not silent:
                        info(msg)
                    else:
                        self._append_runtime_log(msg)
                if link_info:
                    # Shows BSSID (AP MAC) and signal, bitrate
                    msg = f"     {sta.name} link: {link_info.strip()}\n"
                    if not self.quiet_cli and not silent:
                        info(msg)
                    else:
                        self._append_runtime_log(msg)
                if not wifi_info and not link_info:
                    msg = f"     {sta.name}: No connection info available\n"
                    if not self.quiet_cli and not silent:
                        info(msg)
                    else:
                        self._append_runtime_log(msg)
            except Exception:
                msg = f"     {sta.name}: Status check failed\n"
                if not self.quiet_cli and not silent:
                    info(msg)
                else:
                    self._append_runtime_log(msg)

    def test_connectivity(self):
        """Test connectivity with enhanced analysis"""
        info("*** Testing enhanced connectivity for handover analysis\n")
        
        connectivity_results = {}
        
        for i, sta in enumerate(self.stations):
            results = []
            targets = [f'10.0.0.{j+1}' for j in range(5) if j != i]
            
            for target_ip in targets:
                try:
                    # Increased to 5 pings to allow for ARP resolution
                    result = sta.cmd(f'ping -c 5 -W 1 {target_ip}')
                    
                    if "5 received" in result:
                        status = "EXCELLENT"
                    elif "4 received" in result:
                        status = "EXCELLENT"
                    elif "3 received" in result:
                        status = "GOOD"
                    elif "2 received" in result:
                        status = "LIMITED"
                    else:
                        status = "FAILED"
                    
                    results.append((target_ip, status))
                    
                except Exception as e:
                    results.append((target_ip, "ERROR"))
            
            connectivity_results[sta.name] = results
            
            # Log results
            success_count = sum(1 for _, status in results if status in ["EXCELLENT", "GOOD"])
            info(f"   {sta.name} ({sta.mobility_profile}): {success_count}/{len(results)} connections successful\n")
        
        return connectivity_results

    def print_enhanced_testing_guide(self):
        """Print comprehensive testing guide"""
        info("*** ================================================================\n")
        info("*** ENHANCED HANDOVER STRATEGY ANALYSIS TESTING GUIDE\n")
        info("*** ================================================================\n")
        info("*** \n")
        info(f"*** Mobility Model: {self.mobility_model}\n")
        info(f"*** Test Duration: {self.test_duration} seconds\n")
        info("*** \n")
        info("*** STATION PROFILES:\n")
        for sta in self.stations:
            info(f"***   {sta.name}: {sta.mobility_profile} mobility, {sta.handover_sensitivity} handover\n")
        info("*** \n")
        info("*** ACCESS POINT PROFILES:\n")
        for ap in self.access_points:
            info(f"***   {ap.name}: {ap.capacity_profile} capacity, {ap.interference_level} interference\n")
        info("*** \n")
        info("*** TESTING COMMANDS:\n")
        info("*** \n")
        info("*** 1. Monitor station mobility and handovers:\n")
        info("***    mininet-wifi> xterm sta1 sta2 sta3 sta4 sta5\n")
        info("***    # In each terminal:\n")
        info("***    sta1# watch -n 2 'iwconfig | grep \"Access Point\"'\n")
        info("*** \n")
        info("*** 2. Monitor handover strategy performance:\n")
        info("***    # In another terminal:\n")
        info("***    tail -f results/*Enhanced_Handover_Analysis*.csv\n")
        info("*** \n")
        info("*** 3. Real-time network analysis:\n")
        info("***    mininet-wifi> stations\n")
        info("***    mininet-wifi> links\n")
        info("***    mininet-wifi> pingall\n")
        info("*** \n")
        info("*** 4. SDN Controller monitoring:\n")
        info("***    # Check controller logs for strategy changes\n")
        info("***    # Monitor flow table updates\n")
        info("*** \n")
        info("*** ANALYSIS FEATURES:\n")
        info("***   ✅ Multiple handover strategies (Reactive, Proactive, Load-Aware, etc.)\n")
        info("***   ✅ AP residence time analysis\n")
        info("***   ✅ Coverage overlap analysis\n")
        info("***   ✅ SDN controller impact measurement\n")
        info("***   ✅ Handover trigger analysis\n")
        info("***   ✅ Performance comparison between strategies\n")
        info("***   ✅ Load balancing effectiveness\n")
        info("*** ================================================================\n")

    def create_enhanced_topology(self):
        """Create the complete enhanced topology"""
        info(f"*** Creating Enhanced {self.mobility_model} Topology for Handover Analysis ***\n")
        
        # Record mobility model for controller CSV naming
        try:
            os.makedirs('results', exist_ok=True)
            with open('results/mobility_model.txt', 'w') as f:
                f.write(self.mobility_model)
            info(f"*** Recorded mobility model: {self.mobility_model}\n")
        except Exception as e:
            error(f"*** Failed to record mobility model: {e}\n")
        
        try:
            # Initialize Mininet-WiFi with realistic wireless medium simulation
            # Use wmediumd in interference mode so signal strength and movement
            # actually affect associations and trigger roaming decisions.
            self.net = Mininet_wifi(
                controller=Controller,
                link=wmediumd,
                wmediumd_mode=interference,
                accessPoint=OVSKernelAP
            )
            
            # Create network components
            self.create_enhanced_stations()
            self.create_enhanced_access_points()
            
            # Create controller
            info("*** Creating SDN controller connection\n")
            try:
                self.controller = self.net.addController('c1', controller=RemoteController, port=6633)
            except Exception as e:
                error(f"*** Remote controller connection failed: {e}\n")
                info("*** Falling back to local Controller for CLI access\n")
                try:
                    self.controller = self.net.addController('c1', controller=Controller)
                except Exception as e2:
                    error(f"*** Controller fallback failed: {e2}\n")
                    error("*** Unable to start any controller.\n")
                    return False
            
            # Configure propagation model
            info("*** Configuring propagation model for handover analysis\n")
            self.net.setPropagationModel(model="logDistance", exp=4)
            
            # Configure WiFi nodes
            info("*** Configuring WiFi nodes\n")
            self.net.configureWifiNodes()
            self.net.plotGraph(max_x=1000, max_y=1000)

            # Ensure association control prefers strongest signal first
            # This complements the ac_method set in the mobility model.
            # Note: setAssociationControl removed as it is not supported in this version
            # try:
            #     self.net.setAssociationControl('ssf')
            #     info("*** Association control set to strongest-signal-first (ssf)\n")
            # except Exception as e:
            #     info(f"*** Association control setup warning: {e}\n")
            
            # Setup mobility
            if not self.setup_mobility_model():
                return False
            
            # Create network links
            self.create_optimized_network_links()
            
            # Start network
            info("*** Starting enhanced network\n")
            self.net.build()
            self.controller.start()
            
            # Start access points
            info("*** Starting access points\n")
            for ap in self.access_points:
                ap.start([self.controller])
            
            # Setup enhanced networking
            self.setup_enhanced_networking()
            
            # Wait for network stabilization
            info("*** Waiting for network stabilization (30 seconds)\n")
            time.sleep(30)
            
            # Test connectivity
            connectivity_results = self.test_connectivity()
            
            # Generate traffic and notify controller
            self.generate_enhanced_traffic()
            self.notify_controller_about_test()
            
            return True
            
        except Exception as e:
            error(f"*** Error creating enhanced topology: {e}\n")
            import traceback
            traceback.print_exc()
            return False

    def run_enhanced_handover_test(self):
        """Run the complete enhanced handover analysis test"""
        try:
            if self.create_enhanced_topology():
                info(f"*** Enhanced {self.mobility_model} topology ready for analysis\n")
                self.print_enhanced_testing_guide()
                
                # Optionally start automated analysis in the background
                if self.enable_analysis:
                    self._print_info("*** Starting automated handover analysis (background)\n")
                    try:
                        import threading
                        analysis_thread = threading.Thread(target=self.run_handover_analysis_tests, daemon=True)
                        analysis_thread.start()
                    except Exception as e:
                        error(f"*** Failed to start background analysis: {e}\n")
                        self._print_info("*** Proceeding to CLI without background analysis\n")

                # Start CLI for manual testing
                info("*** Starting CLI for manual testing and monitoring\n")
                CLI(self.net)
            else:
                error("*** Failed to create enhanced topology\n")
                return False
                
        except KeyboardInterrupt:
            info("*** Enhanced test interrupted by user\n")
        except Exception as e:
            error(f"*** Enhanced test error: {e}\n")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.net:
                info("*** Stopping enhanced network\n")
                self.net.stop()
        
        return True

def main():
    """Main execution function with argument parsing"""
    parser = argparse.ArgumentParser(description='Enhanced Handover Strategy Analysis')
    parser.add_argument('--mobility', choices=['RandomWayPoint', 'RandomDirection'], 
                       default='RandomWayPoint', help='Mobility model to use')
    parser.add_argument('--duration', type=int, default=300, 
                       help='Test duration in seconds')
    parser.add_argument('--sdn', action='store_true', default=True,
                       help='Enable SDN controller features')
    parser.add_argument('--no-analysis', action='store_true', default=False,
                        help='Open CLI without running automated analysis phases')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Show background analysis logs in CLI')
    
    args = parser.parse_args()
    
    setLogLevel('info')
    
    print("=" * 80)
    print("ENHANCED HANDOVER STRATEGY ANALYSIS SIMULATION")
    print("=" * 80)
    print(f"Mobility Model: {args.mobility}")
    print(f"Test Duration: {args.duration} seconds")
    print(f"SDN Features: {'Enabled' if args.sdn else 'Disabled'}")
    print("")
    print("ENHANCED FEATURES:")
    print("✅ Multiple handover strategies (Reactive, Proactive, Load-Aware, etc.)")
    print("✅ Station mobility profiles (high_speed, predictable, etc.)")
    print("✅ AP capacity and interference modeling")
    print("✅ SDN controller impact measurement")
    print("✅ Coverage and residence time analysis")
    print("✅ Handover trigger analysis")
    print("✅ Performance comparison between strategies")
    print("✅ Comprehensive CSV logging with strategy metrics")
    print("")
    print("PREREQUISITES:")
    print("1. Start Enhanced Ryu controller FIRST:")
    print("   ryu-manager --ofp-tcp-listen-port=6633 enhanced_controller.py")
    print("2. Then run this script:")
    print(f"   sudo python3 enhanced_topology.py --mobility {args.mobility}")
    print("=" * 80)
    
    # Check if running as root (Linux only). On non-POSIX systems, skip.
    try:
        if hasattr(os, 'geteuid') and os.geteuid() != 0:
            print("Error: This script must be run as root (use sudo)")
            sys.exit(1)
    except Exception:
        # If the environment doesn't support geteuid, continue.
        pass
    
    # Create and run enhanced topology
    topology = EnhancedHandoverTestTopology(
        mobility_model=args.mobility,
        test_duration=args.duration,
        enable_analysis=(not args.no_analysis)
    )
    # Configure CLI verbosity
    topology.quiet_cli = not args.verbose
    
    success = topology.run_enhanced_handover_test()
    
    if success:
        print(f"Enhanced {args.mobility} handover analysis completed successfully")
        sys.exit(0)
    else:
        print(f"Enhanced {args.mobility} handover analysis failed")
        sys.exit(1)

if __name__ == '__main__':
    main()


