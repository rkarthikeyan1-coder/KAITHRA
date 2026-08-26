import csv
import os


# ============================================================
# FILE PATH
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

ARTISAN_PROFILES_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "artisan_test_profiles.csv"
)


# ============================================================
# LOAD CSV
# ============================================================

def load_artisans(filename):
    with open(filename, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return list(reader)


# ============================================================
# READINESS CALCULATION
# ============================================================

def calculate_readiness(artisan):

    score = 0
    completed = []
    missing = []

    # --------------------------------------------------------
    # Product Image — 20%
    # --------------------------------------------------------

    if artisan.get("has_image", "").strip().lower() == "yes":
        score += 20
        completed.append("Product image")
    else:
        missing.append("Upload product image")

    # --------------------------------------------------------
    # Description — 25%
    # --------------------------------------------------------

    if artisan.get("has_description", "").strip().lower() == "yes":
        score += 25
        completed.append("Product description")
    else:
        missing.append("Complete product description")

    # --------------------------------------------------------
    # Price — 20%
    # --------------------------------------------------------

    if artisan.get("has_price", "").strip().lower() == "yes":
        score += 20
        completed.append("Product price")
    else:
        missing.append("Generate/fix product price")

    # --------------------------------------------------------
    # Documents — 20%
    # --------------------------------------------------------

    if artisan.get("has_documents", "").strip().lower() == "yes":
        score += 20
        completed.append("Required documents")
    else:
        missing.append("Prepare required documents")

    # --------------------------------------------------------
    # Basic Profile — 15%
    # --------------------------------------------------------

    profile_fields = [
        "craft_category",
        "product_name",
        "material",
        "seller_type",
        "location",
        "business_type",
        "target_market"
    ]

    filled_fields = 0

    for field in profile_fields:

        value = artisan.get(field, "").strip()

        if value:
            filled_fields += 1

    profile_score = round(
        (filled_fields / len(profile_fields)) * 15
    )

    score += profile_score

    if filled_fields == len(profile_fields):

        completed.append("Basic artisan profile")

    else:

        missing.append("Complete artisan profile")

    # --------------------------------------------------------
    # Readiness Level
    # --------------------------------------------------------

    if score >= 80:
        level = "READY"

    elif score >= 60:
        level = "NEARLY READY"

    elif score >= 40:
        level = "PARTIALLY READY"

    else:
        level = "NOT READY"

    # --------------------------------------------------------
    # Next Action
    # --------------------------------------------------------

    if missing:

        next_action = missing[0]

    else:

        next_action = (
            "Proceed to market-channel onboarding"
        )

    return {
        "artisan_id": artisan.get("artisan_id"),
        "product_name": artisan.get("product_name"),
        "score": score,
        "level": level,
        "completed": completed,
        "missing": missing,
        "next_action": next_action
    }


# ============================================================
# DISPLAY RESULTS
# ============================================================

def main():

    print("\n======================================")
    print(" KAITHRA - SELLER READINESS")
    print("======================================\n")

    artisans = load_artisans(
        ARTISAN_PROFILES_FILE
    )

    print(
        f"Artisan profiles loaded: {len(artisans)}"
    )

    print("\n--------------------------------------")

    for artisan in artisans:

        result = calculate_readiness(
            artisan
        )

        print(
            f"\nARTISAN {result['artisan_id']}"
        )

        print(
            f"Product: {result['product_name']}"
        )

        print(
            f"Readiness Score: {result['score']}%"
        )

        print(
            f"Status: {result['level']}"
        )

        print("\nCompleted:")

        for item in result["completed"]:

            print(
                f"   ✓ {item}"
            )

        print("\nMissing:")

        if result["missing"]:

            for item in result["missing"]:

                print(
                    f"   ⚠ {item}"
                )

        else:

            print(
                "   ✓ Nothing missing"
            )

        print(
            f"\nNext Action: {result['next_action']}"
        )

        print("\n--------------------------------------")


if __name__ == "__main__":
    main()
