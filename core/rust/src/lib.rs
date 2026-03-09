#![cfg_attr(not(feature = "std"), no_std)]

pub mod codec;
pub mod ffi;
pub mod quantise;
pub mod rle;

pub use codec::{decode_into, encode, CodecError, CodecMode, EncodedStream};

#[cfg(not(feature = "std"))]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[cfg(test)]
mod tests {
    use super::codec::EncodedStream;
    use core::mem::size_of;

    const MAX_STACK_BYTES: usize = 8 * 1024;

    #[test]
    fn embedded_stack_proxy_within_budget() {
        // Conservative proxy for the embedded encode loop frame:
        // - 1s ECG window (250 f64 samples)
        // - encoded token container (N=512 profile used in embedded main)
        // - extra scratch allowance for locals/call overhead
        let stack_proxy = size_of::<[f64; 250]>() + size_of::<EncodedStream<512>>() + 512;
        println!("embedded_stack_proxy_bytes={stack_proxy}");
        assert!(
            stack_proxy < MAX_STACK_BYTES,
            "stack proxy {} exceeds {} bytes",
            stack_proxy,
            MAX_STACK_BYTES
        );
    }
}
