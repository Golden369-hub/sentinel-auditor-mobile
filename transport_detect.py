import ipaddress
import socket

def detect_transport():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        local_ip = s.getsockname()[0]
        s.close()

        ip_obj = ipaddress.ip_address(local_ip)

        # RFC 7335 / RFC 6877: 464XLAT cellular baseband interface
        clat_network = ipaddress.ip_network("192.0.0.0/29")
        # RFC 6598: Carrier-Grade NAT pool
        cgnat_network = ipaddress.ip_network("100.64.0.0/10")

        if ip_obj in clat_network or ip_obj in cgnat_network:
            return {"transport": "CELLULAR", "status": "PASS"}
        elif ip_obj.is_private:
            return {"transport": "WIFI", "status": "PASS"}
        else:
            return {"transport": "DIRECT_PUBLIC", "status": "PASS"}
    except Exception:
        return {"transport": "DISCONNECTED", "status": "FAIL"}
