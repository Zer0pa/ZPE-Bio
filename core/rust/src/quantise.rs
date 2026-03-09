pub const DIRECTION_DELTAS: [f64; 8] = [
    0.0,   // 0
    1.0,   // 1 (+1x)
    8.0,   // 2 (+8x)
    32.0,  // 3 (+32x)
    128.0, // 4 (+128x)
    -32.0, // 5 (-32x)
    -8.0,  // 6 (-8x)
    -1.0,  // 7 (-1x)
];

pub fn quantise_ecg(delta: f64, threshold: f64) -> u8 {
    let abs_delta = if delta < 0.0 { -delta } else { delta };
    if abs_delta < threshold {
        return 0;
    }

    if delta > 0.0 {
        if abs_delta > 64.0 * threshold {
            return 4;
        }
        if abs_delta > 16.0 * threshold {
            return 3;
        }
        if abs_delta > 4.0 * threshold {
            return 2;
        }
        1
    } else {
        if abs_delta > 16.0 * threshold {
            return 5;
        }
        if abs_delta > 4.0 * threshold {
            return 6;
        }
        7
    }
}
