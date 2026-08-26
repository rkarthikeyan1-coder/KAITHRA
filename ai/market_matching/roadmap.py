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
# LOAD ARTISAN DATA
# ============================================================

def load_artisans(filename):

    with open(filename, "r", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        return list(reader)


# ============================================================
# ROADMAP GENERATOR
# ============================================================

def generate_roadmap(artisan):

    roadmap = []

    # --------------------------------------------------------
    # STEP 1 — IMAGE
    # --------------------------------------------------------

    if artisan.get("has_image", "").strip().lower() != "yes":

        roadmap.append({
            "step": len(roadmap) + 1,
            "action": "Upload or capture a product image",
            "priority": "HIGH",
            "status": "PENDING"
        })

    # --------------------------------------------------------
    # STEP 2 — DESCRIPTION
    # --------------------------------------------------------

    if artisan.get("has_description", "").strip().lower() != "yes":

        roadmap.append({
            "step": len(roadmap) + 1,
            "action": "Complete the product description",
            "priority": "HIGH",
            "status": "PENDING"
        })

    # --------------------------------------------------------
    # STEP 3 — PRICE
    # --------------------------------------------------------

    if artisan.get("has_price", "").strip().lower() != "yes":

        roadmap.append({
            "step": len(roadmap) + 1,
            "action": "Generate or confirm a suitable product price",
            "priority": "HIGH",
            "status": "PENDING"
        })

    # --------------------------------------------------------
    # STEP 4 — DOCUMENTS
    # --------------------------------------------------------

    if artisan.get("has_documents", "").strip().lower() != "yes":

        roadmap.append({
            "step": len(roadmap) + 1,
            "action": "Prepare required seller documents",
            "priority": "MEDIUM",
            "status": "PENDING"
        })

    # --------------------------------------------------------
    # STEP 5 — MARKETPLACE SELECTION
    # --------------------------------------------------------

    roadmap.append({
        "step": len(roadmap) + 1,
        "action": "Review recommended market channels",
        "priority": "HIGH",
        "status": "PENDING"
    })

    # --------------------------------------------------------
    # STEP 6 — ONBOARDING
    # --------------------------------------------------------

    roadmap.append({
        "step": len(roadmap) + 1,
        "action": "Complete the selected market channel's onboarding requirements",
        "priority": "HIGH",
        "status": "PENDING"
    })

    # --------------------------------------------------------
    # STEP 7 — PRODUCT LISTING
    # --------------------------------------------------------

    roadmap.append({
        "step": len(roadmap) + 1,
        "action": "Publish the product listing on the selected channel",
        "priority": "MEDIUM",
        "status": "PENDING"
    })

    # --------------------------------------------------------
    # STEP 8 — START SELLING
    # --------------------------------------------------------

    roadmap.append({
        "step": len(roadmap) + 1,
        "action": "Start selling and monitor orders",
        "priority": "LOW",
        "status": "FUTURE"
    })

    return roadmap


# ============================================================
# DISPLAY ROADMAP
# ============================================================

def main():

    print("\n======================================")
    print(" SHILPSETU AI - SELLING ROADMAP")
    print("======================================\n")

    artisans = load_artisans(
        ARTISAN_PROFILES_FILE
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
            f"Product: {artisan.get('product_name')}"
        )

        print("\nPERSONALISED ROADMAP:")

        roadmap = generate_roadmap(
            artisan
        )

        for item in roadmap:

            print(
                f"\n{item['step']}. "
                f"{item['action']}"
            )

            print(
                f"   Priority: {item['priority']}"
            )

            print(
                f"   Status: {item['status']}"
            )

        print("\n--------------------------------------")


if __name__ == "__main__":
    main()
