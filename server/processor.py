from datetime import datetime

import numpy as np
from sgp4.functions import jday


async def process(
        satellites
):
    time_now = datetime.now()
    jd, fr = jday(
        time_now.year,
        time_now.month,
        time_now.day,
        time_now.hour,
        time_now.minute,
        time_now.second
    )
    jd, fr = np.array((jd,)), np.array((fr,))
    _, r, _ = satellites.sgp4(jd, fr)
    return r.tolist()
