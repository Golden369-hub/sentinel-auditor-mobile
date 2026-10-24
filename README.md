# GRD // Sentinel Auditor (Mobile)

[![Live Demo](https://img.shields.io/badge/GitHub_Pages-Live_HUD-00ffcc?style=flat-square&logo=github)](https://golden369-hub.github.io/sentinel-auditor-mobile/)

**Live Interface:** https://golden369-hub.github.io/sentinel-auditor-mobile/


Deterministic, NIST SP 800-171 Rev 3-compliant mobile network telemetry and auditing engine with an embedded Cyberpunk HUD interface.


## Compliance & Security Standard
- **Standard**: NIST SP 800-171 Rev 3
- **Controls**: System and Communications Protection (SC), System and Information Integrity (SI)
- **SAST**: Bandit verified (0 Medium, 0 High vulnerabilities)
- **Code Quality**: Flake8 verified (0 PEP 8 syntax/style drift)
- **TLS/Host Validation**: Strict scheme enforcement and default SSL context verification

## Architecture
- `grd_mobile_audit.py`: Core telemetry engine (ICMP latency/jitter probing + HTTP/TLS throughput audit).
- `app_gui.py`: Lightweight HTTP daemon serving the local dashboard.
- `index.html`: Responsive, mobile-first Cyberpunk HUD front-end.
- `config.json`: Structured target and threshold manifest.
- `test_audit.py`: CI/CD pre-commit schema integrity test.

## Execution

### Run CLI Engine
```bash
python3 grd_mobile_audit.py
