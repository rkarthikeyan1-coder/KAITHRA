import csv
import os


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

    with open(
        filename,
        "r",
        encoding="utf-8-sig"
    ) as file:

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

        value = normalize(
            channel.get("b2b")
        )

        if value == "yes":
            return True

        if value == "no":
            return False

        return None

    if target_market == "b2c":

        value = normalize(
            channel.get("b2c")
        )

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
# ELIGIBILITY CLASSIFICATION
# ============================================================

def classify_eligibility(channel):
    """
    Classify a market channel as:

        ELIGIBLE
        CONDITIONAL
        NOT_ELIGIBLE

    based on the eligibility text stored in the dataset.
    """

    eligibility_text = normalize(
        channel.get("eligibility")
    )

    if not eligibility_text:
        return "CONDITIONAL"

    # Explicit exclusion
    if (
        "not eligible" in eligibility_text
        or "ineligible" in eligibility_text
    ):
        return "NOT_ELIGIBLE"

    # Conditional language
    conditional_terms = [
        "subject to",
        "conditional",
        "verify",
        "applicable requirements",
        "empanelment",
        "onboarding requirements",
        "registration",
        "approval",
        "requirements"
    ]

    for term in conditional_terms:

        if term in eligibility_text:
            return "CONDITIONAL"

    return "ELIGIBLE"


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
    # Eligibility classification
    # --------------------------------------------------------

    eligibility_status = classify_eligibility(
        channel
    )

    # --------------------------------------------------------
    # NOT ELIGIBLE
    # --------------------------------------------------------

    if eligibility_status == "NOT_ELIGIBLE":

        return {
            "eligible": False,
            "eligibility": "NOT_ELIGIBLE",
            "score": 0,
            "match_level": "EXCLUDED",
            "reasons": [],
            "warnings": [
                "Channel is not eligible for this seller."
            ]
        }

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = 0

    # --------------------------------------------------------
    # Category = 30 points
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Seller type = 30 points
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # B2B/B2C = 15 points
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Documents = 10 points
    # --------------------------------------------------------

    if documents is True:

        score += 10

        reasons.append(
            "Seller documents are available."
        )

    elif documents is False:

        warnings.append(
            "Seller documents are not yet available."
        )

    else:

        warnings.append(
            "Document availability is unknown."
        )

    # --------------------------------------------------------
    # Product listing completeness = 15 points
    # --------------------------------------------------------

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

    profile_score = (
        completed / len(profile_fields)
    ) * 15

    score += profile_score

    if completed == len(profile_fields):

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
    # Conditional eligibility warning
    # --------------------------------------------------------

    if eligibility_status == "CONDITIONAL":

        warnings.append(
            "Channel eligibility is conditional; "
            "seller must satisfy the stated requirements."
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "eligible": True,
        "eligibility": eligibility_status,
        "score": round(score, 2),
        "match_level": match_level,
        "reasons": reasons,
        "warnings": warnings
    }


# ============================================================
# RECOMMENDATION ENGINE
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

                "eligibility":
                    result["eligibility"],

                "score":
                    result["score"],

                "match_level":
                    result["match_level"],

                "reasons":
                    result["reasons"],

                "warnings":
                    result["warnings"]
            })

    # --------------------------------------------------------
    # Highest score first
    # --------------------------------------------------------

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "\n======================================"
    )

    print(
        " KAITHRA - MARKET MATCHING ENGINE"
    )

    print(
        "======================================\n"
    )

    print(
        "Loading datasets..."
    )

    # --------------------------------------------------------
    # Load market channels
    # --------------------------------------------------------

    channels = load_csv(
        MARKET_CHANNELS_FILE
    )

    # --------------------------------------------------------
    # Load artisan profiles
    # --------------------------------------------------------

    artisans = load_csv(
        ARTISAN_PROFILES_FILE
    )

    print(
        f"Market channels loaded: "
        f"{len(channels)}"
    )

    print(
        f"Artisan profiles loaded: "
        f"{len(artisans)}"
    )

    print(
        "\n--------------------------------------"
    )

    # --------------------------------------------------------
    # Process each artisan
    # --------------------------------------------------------

    for artisan in artisans:

        print(
            f"\nARTISAN "
            f"{artisan.get('artisan_id')}"
        )

        print(
            f"Craft: "
            f"{artisan.get('craft_category')}"
        )

        print(
            f"Product: "
            f"{artisan.get('product_name')}"
        )

        print(
            f"Seller: "
            f"{artisan.get('seller_type')}"
        )

        print(
            f"Target market: "
            f"{artisan.get('target_market')}"
        )

        print(
            "\nRECOMMENDATIONS:"
        )

        recommendations = recommend_for_artisan(
            artisan,
            channels
        )

        if not recommendations:

            print(
                "No suitable market channels found."
            )

            continue

        # ----------------------------------------------------
        # Display recommendations
        # ----------------------------------------------------

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"\n{index}. "
                f"{recommendation['channel_name']}"
            )

            print(
                f"   Eligibility: "
                f"{recommendation['eligibility']}"
            )

            print(
                f"   Score: "
                f"{recommendation['score']}%"
            )

            print(
                f"   Match: "
                f"{recommendation['match_level']}"
            )

            # ------------------------------------------------
            # Reasons
            # ------------------------------------------------

            if recommendation["reasons"]:

                print(
                    "   Reasons:"
                )

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

                print(
                    "   Warnings:"
                )

                for warning in recommendation[
                    "warnings"
                ]:

                    print(
                        f"      ⚠ {warning}"
                    )

        print(
            "\n--------------------------------------"
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
