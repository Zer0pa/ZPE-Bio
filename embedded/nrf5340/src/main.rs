#![no_std]
#![no_main]

use cortex_m::asm;
use cortex_m_rt::entry;
use defmt::info;
use defmt_rtt as _;

use zpe_bio_codec::{encode, CodecMode};
use zpe_bio_codec::codec::ThresholdMode;

const WINDOW_SIZE: usize = 250;
const THRESHOLD: f64 = 0.05;
const STEP: f64 = 0.05;

#[entry]
fn main() -> ! {
    info!("zpe-bio nRF5340 codec smoke start");

    // Deterministic placeholder window for host-side embedded build validation.
    let window = [0.0_f64; WINDOW_SIZE];

    let encoded = encode::<512>(
        &window,
        CodecMode::Transport,
        THRESHOLD,
        ThresholdMode::Fixed,
        STEP,
    )
    .unwrap_or_else(|_| panic!("encode failed"));

    info!("encoded token count: {}", encoded.tokens.len());

    loop {
        asm::wfi();
    }
}
