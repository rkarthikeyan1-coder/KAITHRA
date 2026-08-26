import os

from .matcher import load_csv, recommend_for_artisan
from .readiness import load_artisans, calculate_readiness
from .roadmap import generate_roadmap
from .category_mapper import normalize_artisan_category


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
# UNIFIED M5 MARKET-LINKAGE FUNCTION
# ============================================================

def get_market_linkage_result(artisan, channels):
    """
    Returns the complete M5 result for one artisan.

    This combines:
    1. Craft category standardization
    2. Market matching
    3. Seller readiness
    4. Personalized roadmap

    This function will later be used by M2/FastAPI.
    """

    # --------------------------------------------------------
    # 0. STANDARDIZE CRAFT CATEGORY
    # --------------------------------------------------------

    category_mapping = normalize_artisan_category(
        artisan.get("craft_category")
    )

    # --------------------------------------------------------
    # PREPARE ARTISAN FOR MARKET MATCHING
    # --------------------------------------------------------

    if category_mapping["matched"]:

        artisan_for_matching = artisan.copy()

        artisan_for_matching["craft_category"] = (
            category_mapping["category_name"]
        )

    else:

        artisan_for_matching = artisan

    # --------------------------------------------------------
    # 1. MARKET MATCHING
    # --------------------------------------------------------

    market_recommendations = recommend_for_artisan(
        artisan_for_matching,
        channels
    )

    # --------------------------------------------------------
    # 2. SELLER READINESS
    # --------------------------------------------------------

    readiness = calculate_readiness(
        artisan
    )

    # --------------------------------------------------------
    # 3. PERSONALIZED ROADMAP
    # --------------------------------------------------------

    roadmap = generate_roadmap(
        artisan
    )

    # --------------------------------------------------------
    # FINAL M5 RESULT
    # --------------------------------------------------------

    return {
        "artisan_id": artisan.get("artisan_id"),
        "product_name": artisan.get("product_name"),
        "category_mapping": category_mapping,
        "market_recommendations": market_recommendations,
        "readiness": readiness,
        "roadmap": roadmap
    }


# ============================================================
# PROCESS ONE ARTISAN
# ============================================================

def process_artisan(artisan, channels):
    """
    Process one artisan through the complete M5 pipeline.
    """

    return get_market_linkage_result(
        artisan,
        channels
    )


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

def display_result(result):

    print("\n")
    print("==============================================")
    print("          KAITHRA - M5 MARKET LINKAGE")
    print("==============================================")

    print(
        f"\nArtisan ID: {result['artisan_id']}"
    )

    print(
        f"Product: {result['product_name']}"
    )

    # ========================================================
    # 0. CRAFT CATEGORY STANDARDIZATION
    # ========================================================

    category_mapping = result["category_mapping"]

    print("\n----------------------------------------------")
    print("0. CRAFT CATEGORY STANDARDIZATION")
    print("----------------------------------------------")

    if category_mapping["matched"]:

        print(
            f"Standard Category: "
            f"{category_mapping['category_name']}"
        )

        print(
            f"Category ID: "
            f"{category_mapping['category_id']}"
        )

        print(
            f"Confidence: "
            f"{category_mapping['confidence']}%"
        )

        print(
            f"Source: "
            f"{category_mapping['source']}"
        )

    else:

        print(
            "No verified standard category match found."
        )

    # ========================================================
    # 1. MARKET RECOMMENDATIONS
    # ========================================================

    print("\n----------------------------------------------")
    print("1. MARKET RECOMMENDATIONS")
    print("----------------------------------------------")

    recommendations = result[
        "market_recommendations"
    ]

    if not recommendations:

        print(
            "No suitable market channels found."
        )

    else:

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"\n{index}. "
                f"{recommendation['channel_name']}"
            )

            # ------------------------------------------------
            # Eligibility
            # ------------------------------------------------

            print(
                f"   Eligibility: "
                f"{recommendation['eligibility']}"
            )

            # ------------------------------------------------
            # Match Score
            # ------------------------------------------------

            print(
                f"   Match Score: "
                f"{recommendation['score']}%"
            )

            # ------------------------------------------------
            # Match Level
            # ------------------------------------------------

            print(
                f"   Match Level: "
                f"{recommendation['match_level']}"
            )

            # ------------------------------------------------
            # Reasons
            # ------------------------------------------------

            if recommendation["reasons"]:

                print("   Reasons:")

                for reason in recommendation[
                    "reasons"
                ]:

                    print(
                        f"      ✓ {reason}"
                    )

            # ------------------------------------------------
            # Warnings
            # ------------------------------------------------

            if recommendation["warnings"]:

                print("   Warnings:")

                for warning in recommendation[
                    "warnings"
                ]:

                    print(
                        f"      ⚠ {warning}"
                    )

    # ========================================================
    # 2. SELLER READINESS
    # ========================================================

    readiness = result["readiness"]

    print("\n----------------------------------------------")
    print("2. SELLER READINESS")
    print("----------------------------------------------")

    print(
        f"Readiness Score: "
        f"{readiness['score']}%"
    )

    print(
        f"Status: "
        f"{readiness['level']}"
    )

    print("\nCompleted:")

    for item in readiness["completed"]:

        print(
            f"   ✓ {item}"
        )

    print("\nMissing:")

    if readiness["missing"]:

        for item in readiness["missing"]:

            print(
                f"   ⚠ {item}"
            )

    else:

        print(
            "   ✓ Nothing missing"
        )

    print(
        f"\nNext Action: "
        f"{readiness['next_action']}"
    )

    # ========================================================
    # 3. PERSONALIZED SELLING ROADMAP
    # ========================================================

    print("\n----------------------------------------------")
    print("3. PERSONALIZED SELLING ROADMAP")
    print("----------------------------------------------")

    for item in result["roadmap"]:

        print(
            f"\n{item['step']}. "
            f"{item['action']}"
        )

        print(
            f"   Priority: "
            f"{item['priority']}"
        )

        print(
            f"   Status: "
            f"{item['status']}"
        )

    print("\n==============================================")
    print("                 END OF M5")
    print("==============================================\n")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "\nLoading KAITHRA M5 datasets..."
    )

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

    print(
        f"Market channels: {len(channels)}"
    )

    print(
        f"Artisan profiles: {len(artisans)}"
    )

    # --------------------------------------------------------
    # PROCESS EVERY ARTISAN
    # --------------------------------------------------------

    for artisan in artisans:

        result = process_artisan(
            artisan,
            channels
        )

        display_result(
            result
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
