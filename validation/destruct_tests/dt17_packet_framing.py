"""
DT-17: Packet Framing Test
PRD: §2.1 | REQ-BLE-1
PASS CONDITION: CRC-16-CCITT detects >99.9% corrupted packets
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import binascii
import numpy as np

PACKET_SYNC_BYTE = 0x5A
NUM_PACKETS = 1000
SINGLE_BIT_ERROR_RATE = 0.10
MULTI_BIT_ERROR_RATE = 0.05
MIN_DETECTION_PERCENT = 99.9


def crc16_ccitt(data: bytes) -> int:
    return binascii.crc_hqx(data, 0xFFFF) & 0xFFFF


def build_packet(payload: bytes) -> bytes:
    header = bytes([PACKET_SYNC_BYTE]) + len(payload).to_bytes(2, "big")
    crc = crc16_ccitt(payload).to_bytes(2, "big")
    return header + payload + crc


def validate_packet(packet: bytes) -> bool:
    if len(packet) < 5:
        return False
    if packet[0] != PACKET_SYNC_BYTE:
        return False

    payload_len = int.from_bytes(packet[1:3], "big")
    expected_len = 1 + 2 + payload_len + 2
    if len(packet) != expected_len:
        return False

    payload = packet[3:-2]
    received_crc = int.from_bytes(packet[-2:], "big")
    return crc16_ccitt(payload) == received_crc


def flip_random_bits(packet: bytes, n_bits: int, rng: np.random.RandomState) -> bytes:
    out = bytearray(packet)
    n_total_bits = len(out) * 8
    bit_positions = rng.choice(n_total_bits, size=n_bits, replace=False)
    for bit_pos in bit_positions:
        byte_idx = int(bit_pos // 8)
        bit_idx = int(bit_pos % 8)
        out[byte_idx] ^= 1 << bit_idx
    return bytes(out)


def main() -> None:
    print("Executing DT-17: Packet Framing (Payload Integrity Audit)...")
    print("-" * 60)

    rng = np.random.RandomState(20260212)
    payload_lens = rng.randint(24, 245, size=NUM_PACKETS)
    packets = [build_packet(bytes(rng.randint(0, 256, size=n, dtype=np.uint8))) for n in payload_lens]

    clean_ok = sum(1 for packet in packets if validate_packet(packet))
    if clean_ok != NUM_PACKETS:
        print(f"FAIL: Clean packet validation failed ({clean_ok}/{NUM_PACKETS})")
        sys.exit(1)
    print(f"Clean packets validated: {clean_ok}/{NUM_PACKETS}")

    n_single = int(NUM_PACKETS * SINGLE_BIT_ERROR_RATE)
    n_multi = int(NUM_PACKETS * MULTI_BIT_ERROR_RATE)
    idx = rng.permutation(NUM_PACKETS)
    single_idx = idx[:n_single]
    multi_idx = idx[n_single:n_single + n_multi]

    detected = 0
    total_corrupted = n_single + n_multi

    for packet_idx in single_idx:
        corrupted = flip_random_bits(packets[int(packet_idx)], 1, rng)
        if not validate_packet(corrupted):
            detected += 1

    for packet_idx in multi_idx:
        n_flip = int(rng.randint(2, 9))
        corrupted = flip_random_bits(packets[int(packet_idx)], n_flip, rng)
        if not validate_packet(corrupted):
            detected += 1

    detection_percent = 100.0 * detected / total_corrupted if total_corrupted else 100.0
    print(f"Corrupted packets tested: {total_corrupted}")
    print(f"Detected corruptions:     {detected}")
    print(f"Detection rate:           {detection_percent:.3f}%")
    print(f"Required minimum:         {MIN_DETECTION_PERCENT:.3f}%")

    if detection_percent >= MIN_DETECTION_PERCENT:
        print("PASS: Packet framing CRC gate satisfied")
        sys.exit(0)

    print("FAIL: Packet framing CRC gate violated")
    sys.exit(1)


if __name__ == "__main__":
    main()
