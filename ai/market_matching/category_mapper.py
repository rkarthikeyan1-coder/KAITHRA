import csv
import os


# ============================================================
# FILE PATH
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

CRAFT_CATEGORIES_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "craft_categories.csv"
)


# ============================================================
# LOAD CRAFT CATEGORIES
# ============================================================

def load_craft_categories():
    """
    Load verified craft categories from
    craft_categories.csv.
    """

    with open(
        CRAFT_CATEGORIES_FILE,
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(value):
    """
    Normalize text for comparison.
    """

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


# ============================================================
# CATEGORY MATCHING
# ============================================================

def map_to_standard_category(
    artisan_category,
    categories
):
    """
    Map an artisan's category to a verified
    standard category.

    Returns:
        category_name
        category_id
        confidence
        source
    """

    input_category = normalize_text(
        artisan_category
    )

    if not input_category:

        return {
            "matched": False,
            "category_id": None,
            "category_name": None,
            "confidence": 0,
            "source": None
        }

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for category in categories:

        standard_name = normalize_text(
            category.get("category_name")
        )

        if input_category == standard_name:

            return {
                "matched": True,
                "category_id":
                    category.get("category_id"),
                "category_name":
                    category.get("category_name"),
                "confidence": 100,
                "source":
                    category.get("source")
            }

    # --------------------------------------------------------
    # Partial match
    # --------------------------------------------------------

    for category in categories:

        standard_name = normalize_text(
            category.get("category_name")
        )

        if (
            input_category in standard_name
            or standard_name in input_category
        ):

            return {
                "matched": True,
                "category_id":
                    category.get("category_id"),
                "category_name":
                    category.get("category_name"),
                "confidence": 80,
                "source":
                    category.get("source")
            }

    # --------------------------------------------------------
    # No match
    # --------------------------------------------------------

    return {
        "matched": False,
        "category_id": None,
        "category_name": None,
        "confidence": 0,
        "source": None
    }


# ============================================================
# ARTISAN CATEGORY NORMALIZATION
# ============================================================

def normalize_artisan_category(
    artisan_category
):
    """
    Convenience function used by M5.

    Loads the verified category dataset
    and attempts to normalize the artisan's
    category.
    """

    categories = load_craft_categories()

    return map_to_standard_category(
        artisan_category,
        categories
    )
