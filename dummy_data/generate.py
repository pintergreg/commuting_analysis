import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from pathlib import Path


def get_cells(area):
    header = ["radio", "mcc", "mnc", "lac", "cid", "?", "lon", "lat", "range",
              "samples", "changeable", "created", "updated", "avg_signal"]
    opencellid = pd.read_csv("input/216.csv.gz", names=header)

    # create geometry table
    opencellid["point_tuple"] = tuple(zip(opencellid["lon"], opencellid["lat"]))
    opencellid["geometry"] = opencellid["point_tuple"].apply(Point)
    cells = gpd.GeoDataFrame(opencellid, geometry="geometry", crs=4326)

    # filter to Vodafone cells and remove 4G
    cells = cells.query("mnc == 70 & radio != 'LTE'").copy()
    # keep cells with at least 250 samples from Budapest
    cells = cells.query("geometry.intersects(@area) & samples >= 250").copy()

    # drop unnecessary columns
    cells = cells.drop(["?", "changeable", "avg_signal", "point_tuple"], axis=1)
    return cells


def generate_timstamp(day, size, p):
    hh = np.random.choice(range(24), size=size, p=p)
    mm = np.random.choice(range(60), size=size)
    ss = np.random.choice(range(60), size=size)

    hh = np.array([str(f"{day} {i:02d}:") for i in hh])
    mm = np.array([str(f"{i:02d}:") for i in mm])
    ss = np.array([str(f"{i:02d}") for i in ss])

    return np.char.add(np.char.add(hh, mm), ss)


def generate_device_ids(record_counts):
    result = np.array([])
    for i, e in enumerate(record_counts):
        result = np.append(result, [i+1]*int(e))
    return result.astype(int)


def choose_cells(cells, size):
    s1 = np.random.choice(cells)
    s2 = np.random.choice(cells)
    n = len(cells)
    weight = np.ones(n)
    weight[np.where(cells == s1)[0][0]] = np.random.randint(n*0.01, high=n*0.05)
    weight[np.where(cells == s2)[0][0]] = np.random.randint(n*0.01, high=n*0.1)
    p = weight/sum(weight)
    return np.random.choice(cells, size=size, p=p)


def generate_dummy_cdr(cells):
    global SIZE, DAYS, HOUR_WEIGHT
    p = HOUR_WEIGHT/sum(HOUR_WEIGHT)

    records = np.floor(np.random.lognormal(size=SIZE)*20)
    df = pd.DataFrame()
    for d in DAYS:
        day = f"2017-04-{d:02d}"
        size = int(records.sum())
        df = pd.concat([df, pd.DataFrame({
            "device_id": generate_device_ids(records),
            "timestamp": generate_timstamp(day, size, p),
            "cell_id": choose_cells(cells, size)})
            ])
    return df.sort_values("timestamp")


def generate_dummy_device_table(size):
    """
    Generating dummy device/SIM data.

    - Customer type is allways set to [C]onsumer
        - no [B]usiness subscription is generated.
    - Subscription type is pr[E]paid or p[O]stpaid with the ratio of 3:7.
    - The generator do not deal with Type Allocation Codes; all set to NaN.
    - Age is generated between 15 and 85, or NaN.
    - Gender is [F]emale, [M]ale or NaN with equal probability.
    """
    df = pd.DataFrame({
        "device_id": list(range(1, size+1)),
        "customer_type": ["C"] * size,
        "subscription_type": np.random.choice(["E", "O"], p=[0.3, 0.7], size=size),
        "tac": [np.NaN] * size,
        "age": np.random.choice(list(range(15, 85))+[np.NaN], p=[0.01]*70+[0.3], size=size),
        "sex": np.random.choice(["F", "M", np.NaN], size=size),
    })

    return df


if __name__ == "__main__":
    # make the script deterministic
    np.random.seed(42)

    DAYS = [1, 2, 3, 4, 5, 6, 7]
    SIZE = 10000
    # to mimick the daily distribution,
    # use the following weight for the hour generation
    HOUR_WEIGHT = np.array([4, 3, 2, 1, 1, 2, 2, 3, 4, 6, 7, 8, 9, 8, 8, 8, 9, 9,
                            9, 8, 6, 5, 4, 3])

    area = gpd.read_file("input/agglomeration_border.geojson", crs=4326)

    Path("dummy_data").mkdir(exist_ok=True)

    cells = get_cells(area.geometry[0])
    cells.to_csv("dummy_data/cells.csv", index=False)
    cdr = generate_dummy_cdr(cells["cid"])
    cdr.to_csv("dummy_data/cdr.csv", index=False)

    devices = generate_dummy_device_table(SIZE)
    devices.to_csv("dummy_data/device.csv", index=False)
