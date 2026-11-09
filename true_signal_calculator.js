function calculateTrueSignalBars(rsrp_dbm) {
    // 369-Standard: Zero-entropy translation of raw hardware RSRP to UI bars
    if (rsrp_dbm === null || rsrp_dbm === undefined) return 0;
    
    const rsrp = Number(rsrp_dbm);
    
    if (rsrp >= -80) return 4;
    if (rsrp >= -90) return 3;
    if (rsrp >= -100) return 2;
    if (rsrp >= -110) return 1;
    return 0; 
}
