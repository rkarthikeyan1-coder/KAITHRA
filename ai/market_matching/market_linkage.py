import csv
import os

from matcher import load_csv, recommend_for_artisan
from readiness import load_artisans, calculate_readiness
from roadmap import generate_roadmap


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
# COMPLETE M5 PIPELINE
# ============================================================

def process_artisan(artisan, channels):

    # --------------------------------------------------------
    # 1. MARKET MATCHING
    # --------------------------------------------------------

    market_recommendations = recommend_for_artisan(
        artisan,
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
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "artisan_id": artisan.get("artisan_id"),
        "product_name": artisan.get("product_name"),

        "market_recommendations":
            market_recommendations,

        "readiness": readiness,

        "roadmap": roadmap
    }


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

def display_result(result):

    print("\n")
    print("==============================================")
    print("       SHILPSETU AI - M5 MARKET LINKAGE")
    print("==============================================")

    print(
        f"\nArtisan ID: {result['artisan_id']}"
    )

    print(
        f"Product: {result['product_name']}"
    )

    # --------------------------------------------------------
    # MARKET RECOMMENDATIONS
    # --------------------------------------------------------

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

            print(
                f"   Match Score: "
                f"{recommendation['score']}%"
            )

            print(
                f"   Match Level: "
                f"{recommendation['match_level']}"
            )

            if recommendation["reasons"]:

                print("   Reasons:")

                for reason in recommendation[
                    "reasons"
                ]:

                    print(
                        f"      ✓ {reason}"
                    )

            if recommendation["warnings"]:

                print("   Warnings:")

                for warning in recommendation[
                    "warnings"
                ]:

                    print(
                        f"      ⚠ {warning}"
                    )

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ROADMAP
    # --------------------------------------------------------

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

    print("\n==============================================\n")


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\nLoading ShilpSetu M5 datasets..."
    )

    channels = load_csv(
        MARKET_CHANNELS_FILE
    )

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
