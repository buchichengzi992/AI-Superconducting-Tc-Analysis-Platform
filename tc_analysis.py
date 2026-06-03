import numpy as np
from scipy.signal import savgol_filter

def smooth_curve(R):
    if len(R) < 51:
        return R

    return savgol_filter(R, window_length=51, polyorder=3)

def find_tc(T, R, tc_min=None, tc_max=None):

    T = np.array(T).flatten()
    R = np.array(R).flatten()

    idx = np.argsort(T)

    T_sorted = T[idx]
    R_sorted = R[idx]

    R_smooth_sorted = smooth_curve(R_sorted)

    R_smooth_display = np.empty_like(R_smooth_sorted)
    R_smooth_display[idx] = R_smooth_sorted

    if tc_min is None:
        tc_min = np.min(T_sorted)

    if tc_max is None:
        tc_max = np.max(T_sorted)

    mask = (T_sorted >= tc_min) & (T_sorted <= tc_max)

    T_search = T_sorted[mask]
    R_search = R_smooth_sorted[mask]

    if len(T_search) < 50:
        return {
            "Tc": np.nan,
            "Tc_onset": np.nan,
            "Tc_end": np.nan,
            "Width": np.nan,
            "R_smooth": R_smooth_display
        }

    R_high = np.mean(R_search[-100:])
    R_low = np.mean(R_search[:100])

    R_mid = (R_high + R_low) / 2

    idx_tc = np.argmin(np.abs(R_search - R_mid))
    Tc = T_search[idx_tc]

    R90 = R_low + 0.9 * (R_high - R_low)
    R10 = R_low + 0.1 * (R_high - R_low)

    idx90 = np.argmin(np.abs(R_search - R90))
    idx10 = np.argmin(np.abs(R_search - R10))

    Tc_onset = T_search[idx90]
    Tc_end = T_search[idx10]

    width = abs(Tc_onset - Tc_end)

    R_max = np.max(R)
    R_min = np.min(R)

    transition_strength = (R_max - R_min) / R_max

    noise_level = np.std(R - R_smooth_display)

    quality_score = 100 - width * 5 - noise_level * 10
    quality_score = max(0, min(100, quality_score))

    return {
        "Tc": Tc,
        "Tc_onset": Tc_onset,
        "Tc_end": Tc_end,
        "Width": width,
        "R_smooth": R_smooth_display,
        "NoiseLevel": noise_level,
        "TransitionStrength": transition_strength,
        "QualityScore": quality_score
    }

def detect_outliers(R):

    R = np.array(R)
    smooth = smooth_curve(R)
    residual = R - smooth
    std = np.std(residual)

    return np.where(np.abs(residual) > 3 * std)[0]
