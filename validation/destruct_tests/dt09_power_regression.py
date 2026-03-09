"""
DT-9: Power Regression Test
PRD: §2.1 | REQ-EMBED-2
PASS CONDITION:
  1) Estimated TX energy reduction >= 3x vs raw streaming
  2) Duty-cycle power estimate (with BLE overhead) < 5 mW average
EXIT CODE: 0 = PASS, 1 = FAIL

Host-side proxy: BLE TX energy is approximated as proportional to transmitted bits.
"""
import sys
from pathlib import Path

import numpy as np
import wfdb

from zpe_bio.codec import encode, CodecMode

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
TEST_RECORDS = ["100", "103", "105", "108", "114", "200", "207", "210", "223", "233"]
MIN_REDUCTION_FACTOR = 3.0
MAX_AVG_POWER_MW = 5.0

# Datasheet-style duty-cycle estimate (RUNBOOK_03 Step 4.2 assumptions).
SUPPLY_VOLTAGE_V = 3.3
ACTIVE_ENCODE_CURRENT_MA = 7.0
SLEEP_CURRENT_UA = 1.5
ENCODE_WINDOW_MS = 1.0
PERIOD_MS = 1000.0
BLE_TX_OVERHEAD_MW = 10.0


def main():
    print("Executing DT-9: Power Regression (TX Proxy Audit)...")
    print("-" * 60)

    reductions = []
    for rec_id in TEST_RECORDS:
        record = wfdb.rdrecord(str(MIT_BIH_DIR / rec_id))
        signal = record.p_signal[:, 0]
        # Use transport battery profile (fixed threshold preset) for TX-energy proxy.
        encoded = encode(signal, mode=CodecMode.TRANSPORT, thr_mode="fixed", signal_type="ecg")
        reduction = float(encoded.compression_ratio)
        reductions.append(reduction)
        print(f"{rec_id}: estimated TX reduction={reduction:.2f}x")

    mean_reduction = float(np.mean(reductions))
    min_reduction = float(np.min(reductions))

    duty_cycle = ENCODE_WINDOW_MS / PERIOD_MS
    active_power_mw = SUPPLY_VOLTAGE_V * ACTIVE_ENCODE_CURRENT_MA
    sleep_power_mw = SUPPLY_VOLTAGE_V * (SLEEP_CURRENT_UA / 1000.0)
    avg_power_mw = duty_cycle * active_power_mw + (1.0 - duty_cycle) * sleep_power_mw
    avg_power_with_ble_mw = avg_power_mw + duty_cycle * BLE_TX_OVERHEAD_MW

    battery_energy_mwh = 220.0 * 3.0  # CR2032 rough model
    battery_days = battery_energy_mwh / avg_power_with_ble_mw / 24.0

    print("-" * 60)
    print(f"Mean estimated reduction: {mean_reduction:.2f}x")
    print(f"Min estimated reduction:  {min_reduction:.2f}x")
    print(f"Required minimum:         {MIN_REDUCTION_FACTOR:.2f}x")
    print("-" * 60)
    print(f"Active power estimate:    {active_power_mw:.3f} mW")
    print(f"Sleep power estimate:     {sleep_power_mw:.5f} mW")
    print(f"Duty-cycle average:       {avg_power_mw:.5f} mW")
    print(f"+ BLE overhead average:   {avg_power_with_ble_mw:.5f} mW")
    print(f"Power budget limit:       {MAX_AVG_POWER_MW:.2f} mW")
    print(f"Battery life estimate:    {battery_days:.1f} days")

    if mean_reduction >= MIN_REDUCTION_FACTOR and avg_power_with_ble_mw < MAX_AVG_POWER_MW:
        print("PASS: Power regression gate satisfied by TX + duty-cycle proxy ✅")
        sys.exit(0)

    print("FAIL: Power regression gate violated ❌")
    sys.exit(1)


if __name__ == "__main__":
    main()
