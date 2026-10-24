# GRD // Sentinel Auditor (Mobile)

[![Live Demo](https://img.shields.io/badge/GitHub_Pages-Live_HUD-00ffcc?style=flat-square&logo=github)](https://golden369-hub.github.io/sentinel-auditor-mobile/)

**Live Interface:** https://golden369-hub.github.io/sentinel-auditor-mobile/

Deterministic, NIST SP 800-171 Rev 3-compliant mobile network telemetry and auditing engine with an embedded Cyberpunk HUD interface.

## Compliance & Security Standard
- **Standard**: NIST SP 800-171 Rev 3
- **Controls**: System and Communications Protection (SC), System and Information Integrity (SI), Audit and Accountability (AU-9)
- **SAST**: Bandit verified (0 Medium, 0 High vulnerabilities)
- **Code Quality**: Flake8 verified (0 PEP 8 syntax/style drift)
- **TLS/Host Validation**: Strict scheme enforcement and default SSL context verification

## Architecture
- `grd_mobile_audit.py`: Core telemetry engine (ICMP latency/jitter probing + HTTP/TLS throughput audit).
- `app.py`: Lightweight HTTP daemon serving the local mobile dashboard on port 8080.
- `index.html`: Responsive, mobile-first Cyberpunk HUD front-end.
- `config.json`: Structured target and threshold manifest.
- `verify_audit.py`: Independent NIST SP 800-171 AU-9 cryptographic seal verification tool.
- `run_tests.py`: 5-stage automated CI/CD test and compliance pipeline.

## Execution

### Run CLI Telemetry Engine
```bash
python3 grd_mobile_audit.py
