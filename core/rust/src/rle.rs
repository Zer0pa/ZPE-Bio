use heapless::Vec;

pub fn compress_rle_hybrid<const N: usize>(raw_tokens: &[(u8, u8)]) -> Vec<(u8, u8, u16), N> {
    let mut result = Vec::new();
    if raw_tokens.is_empty() {
        return result;
    }

    let mut curr_d = raw_tokens[0].0;
    let mut curr_m = raw_tokens[0].1;
    let mut curr_count = 1u16;

    for &(d, m) in &raw_tokens[1..] {
        if d == curr_d && m == curr_m && curr_count < u16::MAX {
            curr_count += 1;
        } else {
            let _ = result.push((curr_d, curr_m, curr_count));
            curr_d = d;
            curr_m = m;
            curr_count = 1;
        }
    }
    let _ = result.push((curr_d, curr_m, curr_count));
    result
}

pub fn decompress_rle_hybrid<const N: usize>(tokens: &[(u8, u8, u16)]) -> Vec<(u8, u8), N> {
    let mut result = Vec::new();
    for &(d, m, count) in tokens {
        for _ in 0..count {
            if result.push((d, m)).is_err() {
                break;
            }
        }
    }
    result
}
