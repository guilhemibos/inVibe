import numpy as np
from ephysvibe.task import task_constants


def indep_roll(arr: np.ndarray, shifts: np.ndarray, axis: int = 1) -> np.ndarray:
    """Apply an independent roll for each dimensions of a single axis.
    Args:
        arr (np.ndarray): Array of any shape.
        shifts (np.ndarray): How many shifting to use for each dimension. Shape: `(arr.shape[axis],)`.
        axis (int, optional): Axis along which elements are shifted. Defaults to 1.

    Returns:
        np.ndarray: shifted array.
    """
    arr = np.swapaxes(arr, axis, -1)
    all_idcs = np.ogrid[[slice(0, n) for n in arr.shape]]
    # Convert to a positive shift
    shifts[shifts < 0] += arr.shape[-1]
    all_idcs[-1] = all_idcs[-1] - shifts[:, np.newaxis]
    result = arr[tuple(all_idcs)]
    arr = np.swapaxes(result, -1, axis)
    return arr


def align_on(
    sp_samples: np.ndarray,
    code_samples: np.ndarray,
    code_numbers: np.ndarray,
    trial_error: np.ndarray,
    block: np.ndarray,
    pos_code: np.ndarray,
    select_block: int = 1,
    event: str = "sample_on",
    time_before: int = 500,
    error_type: int = 0,
    select_pos: int = 1,
) -> [np.ndarray, np.ndarray]:
    # Select trials with the selected error and block
    mask = np.where(
        np.logical_and(
            pos_code == select_pos,
            np.logical_and(trial_error == error_type, block == select_block),
        ),
        True,
        False,
    )
    sp_samples_m = sp_samples[mask]
    # Code corresponding to the event
    if select_block == 1:
        code = task_constants.EVENTS_B1[event]
    elif select_block == 2:
        code = task_constants.EVENTS_B2[event]
    else:
        return
    # Find the codes in the code_numbers matrix
    code_mask = np.where(code_numbers[mask] == code, True, False)
    # Wether the event ocured in each trial
    trials_mask = np.any(code_mask, axis=1)
    # Select the sample when the event ocurred
    shifts = code_samples[mask][code_mask]
    shifts = (shifts - time_before).astype(int)
    # align sp
    align_sp = indep_roll(arr=sp_samples_m[trials_mask], shifts=-shifts, axis=1)
    # Create mask for selecting the trials from the original matrix size
    tr = np.arange(sp_samples.shape[0])
    complete_mask = np.isin(tr, tr[mask][trials_mask])
    return (
        align_sp,
        complete_mask,
    )
