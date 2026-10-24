#!/usr/bin/env python3
import re
import subprocess  # nosec B404
import sys


def trace_route(target="1.1.1.1", max_hops=15):
    print("-" * 50)
    print(f"GRD SENTINEL // ROUTE TRACE: {target}")
    print(f"Max Hops: {max_hops} | Protocol: ICMP/UDP")
    print("-" * 50)

    cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", "1", target]
    try:
        proc = subprocess.run(  # nosec B603
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
    except FileNotFoundError:
        print("[FAIL] 'traceroute' binary not installed.")
        return False
    except subprocess.TimeoutExpired:
        print("[FAIL] Traceroute subprocess timed out.")
        return False

    lines = proc.stdout.strip().split("\n")
    hops = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        match = re.match(
            r"^(\d+)\s+([0-9\.\*]+)\s+([0-9\.]+|\*)\s*ms?",
            line
        )
        if match:
            hop_num = int(match.group(1))
            ip_addr = match.group(2)
            rtt = match.group(3)
            hops.append({"hop": hop_num, "ip": ip_addr, "rtt_ms": rtt})
            print(f"Hop {hop_num:02d} | IP: {ip_addr:<15} | RTT: {rtt} ms")
        elif "*" in line:
            parts = line.split()
            hop_num = int(parts[0]) if parts[0].isdigit() else len(hops) + 1
            hops.append({"hop": hop_num, "ip": "*", "rtt_ms": "*"})
            print(f"Hop {hop_num:02d} | IP: * (Request timed out)")

    print("-" * 50)
    print(f"[PASS] Route discovery completed. Total hops: {len(hops)}")
    return True


if __name__ == "__main__":
    success = trace_route()
    sys.exit(0 if success else 1)
