use crate::quantise::{quantise_ecg, DIRECTION_DELTAS};
use heapless::Vec;

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum CodecMode {
    Transport,
    Clinical,
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum ThresholdMode {
    Fixed,
    AdaptiveRms,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum CodecError {
    InputTooShort,
    EncodeBufferFull,
    EmptyOutputBuffer,
}

pub const ADAPTIVE_K: f64 = 0.15;
pub const ADAPTIVE_THR_MIN: f64 = 0.001;
pub const ADAPTIVE_ALPHA: f64 = 0.95;
pub const LOG_BASE: f64 = 0.08794406087123912; // ln(1.091928)

pub const LOG_MAG_TABLE: [f64; 64] = [
    1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0,
    5.0, 6.0, 6.0, 7.0, 8.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 17.0, 18.0, 20.0, 22.0,
    24.0, 26.0, 28.0, 31.0, 34.0, 37.0, 40.0, 44.0, 48.0, 52.0, 57.0, 62.0, 68.0, 74.0, 81.0, 89.0,
    97.0, 106.0, 115.0, 126.0, 138.0, 150.0, 164.0, 179.0, 196.0, 214.0, 233.0, 255.0,
];

pub struct EncodedStream<const N: usize> {
    pub tokens: Vec<(u8, u8, u16), N>,
    pub start_value: f64,
    pub threshold: f64,
    pub step: f64,
    pub mode: CodecMode,
    pub thr_mode: ThresholdMode,
    pub num_samples: usize,
}

impl<const N: usize> EncodedStream<N> {
    pub fn compression_ratio(&self) -> f64 {
        let raw_bits = (self.num_samples * 16) as f64;
        let mut total_bits = 0;
        for &(_d, _m, count) in &self.tokens {
            let mut token_bits = 3; // direction
            if self.mode == CodecMode::Clinical {
                token_bits += 6; // log_magnitude
            }
            token_bits += 1; // RLE flag
            if count < 16 {
                token_bits += 4;
            } else {
                token_bits += 16;
            }
            total_bits += token_bits;
        }
        if total_bits > 0 {
            raw_bits / (total_bits as f64)
        } else {
            0.0
        }
    }
}

pub fn encode<const N: usize>(
    samples: &[f64],
    mode: CodecMode,
    threshold: f64,
    thr_mode: ThresholdMode,
    step: f64,
) -> Result<EncodedStream<N>, CodecError> {
    if samples.len() < 2 {
        return Err(CodecError::InputTooShort);
    }

    let mut tokens = Vec::new();
    let mut reconstructed_val = samples[0];

    let mut current_d = 0u8;
    let mut current_m = 0u8;
    let mut current_count = 0u16;

    let mut env = 0.0;

    for &actual in &samples[1..] {
        let delta = actual - reconstructed_val;

        let current_thr = if thr_mode == ThresholdMode::AdaptiveRms {
            env = ADAPTIVE_ALPHA * env + (1.0 - ADAPTIVE_ALPHA) * delta.abs();
            let adapt = ADAPTIVE_K * env;
            if adapt > ADAPTIVE_THR_MIN {
                adapt
            } else {
                ADAPTIVE_THR_MIN
            }
        } else {
            threshold
        };

        let d = quantise_ecg(delta, current_thr);

        let (mag_idx, mag_val) = if mode == CodecMode::Transport {
            (0u8, 1.0)
        } else if d == 0 {
            (0u8, 0.0)
        } else {
            let d_delta = DIRECTION_DELTAS[d as usize];
            let target_m = delta.abs() / (d_delta.abs() * step);

            // Find closest index in LOG_MAG_TABLE (Standardized Linear Search)
            let mut best_idx = 0;
            let mut min_err = (LOG_MAG_TABLE[0] - target_m).abs();
            for (j, value) in LOG_MAG_TABLE.iter().enumerate().skip(1) {
                let err = (*value - target_m).abs();
                if err < min_err {
                    min_err = err;
                    best_idx = j;
                }
            }
            (best_idx as u8, LOG_MAG_TABLE[best_idx])
        };

        if current_count > 0 && d == current_d && mag_idx == current_m && current_count < u16::MAX {
            current_count += 1;
        } else {
            if current_count > 0 {
                tokens
                    .push((current_d, current_m, current_count))
                    .map_err(|_| CodecError::EncodeBufferFull)?;
            }
            current_d = d;
            current_m = mag_idx;
            current_count = 1;
        }

        reconstructed_val += (DIRECTION_DELTAS[d as usize] * mag_val) * step;
    }

    if current_count > 0 {
        tokens
            .push((current_d, current_m, current_count))
            .map_err(|_| CodecError::EncodeBufferFull)?;
    }

    Ok(EncodedStream {
        tokens,
        start_value: samples[0],
        threshold,
        step,
        mode,
        thr_mode,
        num_samples: samples.len(),
    })
}

pub fn decode_into<const N: usize>(
    encoded: &EncodedStream<N>,
    output: &mut [f64],
) -> Result<usize, CodecError> {
    if output.is_empty() {
        return Err(CodecError::EmptyOutputBuffer);
    }
    output[0] = encoded.start_value;
    let mut idx = 1;
    let mut val = encoded.start_value;
    for &(d, m_idx, count) in &encoded.tokens {
        let mag_val = if encoded.mode == CodecMode::Transport {
            1.0
        } else if d == 0 {
            0.0
        } else {
            LOG_MAG_TABLE[m_idx as usize]
        };

        let delta = (DIRECTION_DELTAS[d as usize] * mag_val) * encoded.step;
        for _ in 0..count {
            if idx >= output.len() {
                break;
            }
            val += delta;
            output[idx] = val;
            idx += 1;
        }
    }
    Ok(idx)
}
