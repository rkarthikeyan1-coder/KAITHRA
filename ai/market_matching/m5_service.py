import os

from matcher import load_csv
from readiness import load_artisans
from market_linkage import get_market_linkage_result


# ============================================================
# FILE PATHS
# ============================================================

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


# ============================================================
# M5 SERVICE
# ============================================================

def get_m5_result(artisan_id):
    """
    Main service function for M2/FastAPI.

    Input:
        artisan_id

    Output:
        Complete M5 market-linkage result.
    """

    # --------------------------------------------------------
    # LOAD MARKET CHANNELS
    # --------------------------------------------------------

    channels = load_csv(
        MARKET_CHANNELS_FILE
    )

    # --------------------------------------------------------
    # LOAD ARTISAN PROFILES
    # --------------------------------------------------------

    artisans = load_artisans(
        ARTISAN_PROFILES_FILE
    )

    # --------------------------------------------------------
    # FIND REQUESTED ARTISAN
    # --------------------------------------------------------

    artisan = None

    for profile in artisans:

        if profile.get("artisan_id") == str(artisan_id):

            artisan = profile
            break

    # --------------------------------------------------------
    # ARTISAN NOT FOUND
    # --------------------------------------------------------

    if artisan is None:

        return {
            "success": False,
            "error": "Artisan profile not found."
        }

    # --------------------------------------------------------
    # RUN COMPLETE M5 PIPELINE
    # --------------------------------------------------------

    result = get_market_linkage_result(
        artisan,
        channels
    )

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "success": True,
        "data": result
    }
