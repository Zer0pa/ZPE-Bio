use crate::codec::{encode, CodecError, CodecMode, ThresholdMode};
use core::slice;

const ERR_OUTPUT_TOO_SMALL: i32 = -1;
const ERR_ENCODE_FAILED: i32 = -2;
const ERR_NULL_POINTER: i32 = -3;
const ERR_INVALID_ARGUMENT: i32 = -4;

#[no_mangle]
/// Encode a signal into `(direction, magnitude, count)` tuples.
///
/// # Safety
/// - `samples` must point to `n_samples` contiguous `f64` values.
/// - `out_tokens` must point to writable memory for at least `capacity` `Token` entries.
/// - Pointers must remain valid for the duration of this call.
pub unsafe extern "C" fn zpe_encode(
    samples: *const f64,
    n_samples: usize,
    mode_idx: u8,     // 0 for Transport, 1 for Clinical
    thr_mode_idx: u8, // 0 for Fixed, 1 for AdaptiveRms
    threshold: f64,
    step: f64,
    out_tokens: *mut Token,
    capacity: usize,
) -> i32 {
    if samples.is_null() || out_tokens.is_null() {
        return ERR_NULL_POINTER;
    }
    if n_samples < 2 || capacity == 0 {
        return ERR_INVALID_ARGUMENT;
    }

    let samples_slice = {
        // SAFETY: Pointer validity is checked above and the caller upholds layout/length invariants.
        unsafe { slice::from_raw_parts(samples, n_samples) }
    };
    let mode = if mode_idx == 0 {
        CodecMode::Transport
    } else {
        CodecMode::Clinical
    };
    let thr_mode = if thr_mode_idx == 0 {
        ThresholdMode::Fixed
    } else {
        ThresholdMode::AdaptiveRms
    };

    // Use a large enough N for the internal Vec
    match encode::<1024>(samples_slice, mode, threshold, thr_mode, step) {
        Ok(stream) => {
            let n = stream.tokens.len();
            if n > capacity {
                return ERR_OUTPUT_TOO_SMALL;
            }
            let tokens_slice = {
                // SAFETY: Pointer validity is checked above and `n <= capacity`.
                unsafe { slice::from_raw_parts_mut(out_tokens, n) }
            };
            for (idx, token) in tokens_slice.iter_mut().enumerate().take(n) {
                let (d, m, c) = stream.tokens[idx];
                *token = Token {
                    direction: d,
                    magnitude: m,
                    count: c,
                };
            }
            n as i32
        }
        Err(CodecError::InputTooShort) => ERR_INVALID_ARGUMENT,
        Err(CodecError::EncodeBufferFull | CodecError::EmptyOutputBuffer) => ERR_ENCODE_FAILED,
    }
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Token {
    pub direction: u8,
    pub magnitude: u8,
    pub count: u16,
}
