from market_linkage import (
    get_market_linkage_result,
    load_csv,
    load_artisans
)

import os


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

MARKET_CHANNELS_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "market_channels.csv"
)

ARTISAN_PROFILES_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "artisan_test_profiles.csv"
)


def get_m5_result(artisan_id):
    """
    Main service function for M2/FastAPI.

    Input:
        artisan_id

    Output:
        Complete M5 market-linkage result.
    """

    channels = load_csv(
        MARKET_CHANNELS_FILE
    )

    artisans = load_artisans(
        ARTISAN_PROFILES_FILE
    )

    artisan = None

    for profile in artisans:

        if profile.get("artisan_id") == str(artisan_id):
            artisan = profile
            break

    if artisan is None:

        return {
            "success": False,
            "error": "Artisan profile not found."
        }

    result = get_market_linkage_result(
        artisan,
        channels
    )

    return {
        "success": True,
        "data": result
    }
