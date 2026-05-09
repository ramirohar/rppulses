#include <arm_neon.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

size_t count(const int16_t *data, size_t n, int16_t th) {
    if (n < 2) return 0;
    size_t count = 0;
    int16x8_t vth = vdupq_n_s16(th);

    size_t i = 1;
    for (; i + 8 < n; i += 8) {
        int16x8_t  prev8      = vld1q_s16(&data[i - 1]);
        int16x8_t  curr8      = vld1q_s16(&data[i]);
        uint16x8_t prev_above = vcgeq_s16(prev8, vth);   // uint mask
        uint16x8_t curr_below = vcltq_s16(curr8, vth);   // uint mask
        uint16x8_t edges      = vandq_u16(prev_above, curr_below);
        uint64x1_t narrowed   = vreinterpret_u64_u8(vmovn_u16(edges));
        count += __builtin_popcountll(vget_lane_u64(narrowed, 0)) / 8;
    }
    // scalar tail
    bool prev = data[i-1] < th;
    for (; i < n; i++) {
        bool curr = data[i] < th;
        count += (~prev & curr) & 1;
        prev = curr;
    }
    return count;
}

void find(const int16_t *data, size_t n, int16_t th, uint8_t *out) {
    if (n < 2) return;
    int16x8_t vth = vdupq_n_s16(th);

    size_t i = 1;
    for (; i + 8 < n; i += 8) {
        int16x8_t prev8 = vld1q_s16(&data[i-1]);
        int16x8_t  curr8      = vld1q_s16(&data[i]);
        uint16x8_t prev_above = vcgeq_s16(prev8, vth);
        uint16x8_t curr_below = vcltq_s16(curr8, vth);
        uint16x8_t edges      = vandq_u16(prev_above, curr_below);
        vst1_u8(&out[i], vmovn_u16(edges));
    }

    // zero the tail then fill scalarly
    bool prev = data[i-1] >= th;
    for (; i < n; i++) {
        bool curr = data[i] < th;
        out[i] = (prev & curr) ? 0xFF : 0x00;
        prev = data[i] >= th;
    }
}