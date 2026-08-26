import csv
import os


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

MARKET_CHANNELS_FILE = os.path.join(
    BASE_DIR, "datasets", "market_channels.csv"
)

ARTISAN_PROFILES_FILE = os.path.join(
    BASE_DIR, "datasets", "artisan_test_profiles.csv"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize(value):
    """Convert text into a consistent format."""
    if value is None:
        return ""

    return str(value).strip().lower()


def split_values(value):
    """
    Convert pipe-separated CSV values into a list.

    Example:
    'metal craft|tribal textile|jewellery'

    becomes:

    ['metal craft', 'tribal textile', 'jewellery']
    """
    if not value:
        return []

    return [
        normalize(item)
        for item in str(value).split("|")
        if normalize(item)
    ]


def load_csv(filename):
    """Load a CSV file and return a list of dictionaries."""

    with open(filename, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        return list(reader)


# ============================================================
# MATCHING FUNCTIONS
# ============================================================

def category_match(artisan, channel):
    """Check whether the artisan's craft category matches."""

    artisan_category = normalize(
        artisan.get("craft_category")
    )

    channel_categories = split_values(
        channel.get("product_categories")
    )

    if not artisan_category or not channel_categories:
        return None

    for category in channel_categories:

        if (
            artisan_category == category
            or artisan_category in category
            or category in artisan_category
        ):
            return True

    return False


def seller_type_match(artisan, channel):
    """Check whether the seller type is compatible."""

    artisan_type = normalize(
        artisan.get("seller_type")
    )

    channel_sellers = split_values(
        channel.get("seller_types")
    )

    if not artisan_type or not channel_sellers:
        return None

    for seller in channel_sellers:

        if (
            artisan_type == seller
            or artisan_type in seller
            or seller in artisan_type
        ):
            return True

    return False


def target_market_match(artisan, channel):
    """Check B2B/B2C compatibility."""

    target_market = normalize(
        artisan.get("target_market")
    )

    if target_market == "b2b":

        value = normalize(channel.get("b2b"))

        if value == "yes":
            return True

        if value == "no":
            return False

        return None

    if target_market == "b2c":

        value = normalize(channel.get("b2c"))

        if value == "yes":
            return True

        if value == "no":
            return False

        return None

    return None


def document_readiness(artisan):
    """Check whether the artisan has documents."""

    value = normalize(
        artisan.get("has_documents")
    )

    if value == "yes":
        return True

    if value == "no":
        return False

    return None


# ============================================================
# MATCH SCORE
# ============================================================

def calculate_match(artisan, channel):

    reasons = []
    warnings = []

    category = category_match(
        artisan,
        channel
    )

    seller = seller_type_match(
        artisan,
        channel
    )

    market = target_market_match(
        artisan,
        channel
    )

    documents = document_readiness(
        artisan
    )

    # --------------------------------------------------------
    # Eligibility gate
    # --------------------------------------------------------

    eligibility_text = normalize(
        channel.get("eligibility")
    )

    if "not eligible" in eligibility_text:
        return {
            "eligible": False,
            "score": 0,
            "reasons": [],
            "warnings": ["Channel marked as not eligible."]
        }

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = 0

    # Category = 30 points
    if category is True:
        score += 30
        reasons.append(
            "Product category is compatible."
        )

    elif category is False:
        warnings.append(
            "Product category does not clearly match."
        )

    else:
        warnings.append(
            "Product category compatibility is unknown."
        )

    # Seller = 30 points
    if seller is True:
        score += 30
        reasons.append(
            "Seller type appears compatible."
        )

    elif seller is False:
        warnings.append(
            "Seller type does not clearly match."
        )

    else:
        warnings.append(
            "Seller eligibility could not be determined."
        )

    # B2B/B2C = 15 points
    if market is True:
        score += 15
        reasons.append(
            "Target market is compatible."
        )

    elif market is False:
        warnings.append(
            "Target market does not match."
        )

    else:
        warnings.append(
            "B2B/B2C suitability is unknown."
        )

    # Documents = 10 points
    if documents is True:
        score += 10
        reasons.append(
            "Seller documents are available."
        )

    elif documents is False:
        warnings.append(
            "Seller documents are not yet available."
        )

    # Remaining profile completeness = 15 points
    profile_fields = [
        "has_image",
        "has_description",
        "has_price"
    ]

    completed = 0

    for field in profile_fields:

        if normalize(
            artisan.get(field)
        ) == "yes":
            completed += 1

    profile_score = (completed / 3) * 15

    score += profile_score

    if completed == 3:

        reasons.append(
            "Product listing information is complete."
        )

    else:

        warnings.append(
            "Some product listing information is incomplete."
        )

    # --------------------------------------------------------
    # Match level
    # --------------------------------------------------------

    if score >= 80:
        match_level = "HIGH"

    elif score >= 60:
        match_level = "MEDIUM"

    elif score >= 40:
        match_level = "LOW"

    else:
        match_level = "VERY LOW"

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "eligible": True,
        "score": round(score, 2),
        "match_level": match_level,
        "reasons": reasons,
        "warnings": warnings
    }


# ============================================================
# RUN RECOMMENDATION ENGINE
# ============================================================

def recommend_for_artisan(artisan, channels):

    recommendations = []

    for channel in channels:

        result = calculate_match(
            artisan,
            channel
        )

        if result["eligible"]:

            recommendations.append({
                "channel_id": channel.get("id"),
                "channel_name": channel.get("name"),
                "score": result["score"],
                "match_level": result["match_level"],
                "reasons": result["reasons"],
                "warnings": result["warnings"]
            })

    # Highest score first
    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("\n======================================")
    print(" SHILPSETU AI - MARKET MATCHING ENGINE")
    print("======================================\n")

    print("Loading datasets...")

    channels = load_csv(
        MARKET_CHANNELS_FILE
    )

    artisans = load_csv(
        ARTISAN_PROFILES_FILE
    )

    print(
        f"Market channels loaded: {len(channels)}"
    )

    print(
        f"Artisan profiles loaded: {len(artisans)}"
    )

    print("\n--------------------------------------")

    for artisan in artisans:

        print(
            f"\nARTISAN {artisan.get('artisan_id')}"
        )

        print(
            f"Craft: {artisan.get('craft_category')}"
        )

        print(
            f"Product: {artisan.get('product_name')}"
        )

        print(
            f"Seller: {artisan.get('seller_type')}"
        )

        print(
            f"Target market: {artisan.get('target_market')}"
        )

        print("\nRECOMMENDATIONS:")

        recommendations = recommend_for_artisan(
            artisan,
            channels
        )

        if not recommendations:

            print(
                "No suitable market channels found."
            )

            continue

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"\n{index}. "
                f"{recommendation['channel_name']}"
            )

            print(
                f"   Score: "
                f"{recommendation['score']}%"
            )

            print(
                f"   Match: "
                f"{recommendation['match_level']}"
            )

            print("   Reasons:")

            for reason in recommendation["reasons"]:

                print(
                    f"      ✓ {reason}"
                )

            if recommendation["warnings"]:

                print("   Warnings:")

                for warning in recommendation["warnings"]:

                    print(
                        f"      ⚠ {warning}"
                    )

        print("\n--------------------------------------")


if __name__ == "__main__":
    main()
