"""
Populates the catalog with sample products and real size-chart numbers so
later phases (Size Advisor, Style Advisor, Trial Room) have something
real to work against instead of hard-coded frontend data.

Run from backend/ with the venv active:
    python -m app.seed

Safe to re-run — it checks for existing rows by name before inserting.
"""

from app.core.database import SessionLocal
from app.models.clothing import Clothing
from app.models.size_chart import ClothingSize, SizeChart


def get_or_create_size_chart(db, name: str, category: str, rows: list[dict]) -> SizeChart:
    existing = db.query(SizeChart).filter(SizeChart.name == name).first()
    if existing:
        return existing

    chart = SizeChart(name=name, category=category)
    db.add(chart)
    db.flush()  # assigns chart.id without committing yet

    for row in rows:
        db.add(ClothingSize(size_chart_id=chart.id, **row))
    return chart


def get_or_create_clothing(db, name: str, **fields) -> None:
    if db.query(Clothing).filter(Clothing.name == name).first():
        return
    db.add(Clothing(name=name, **fields))


def run():
    db = SessionLocal()
    try:
        # Numbers straight from docs/10-product-size-chart's worked example.
        tops_chart = get_or_create_size_chart(
            db,
            name="Standard Tops",
            category="tops",
            rows=[
                {"size_label": "S", "chest_cm": 88, "waist_cm": 70, "hip_cm": 90, "length_cm": 65, "stock_qty": 20},
                {"size_label": "M", "chest_cm": 94, "waist_cm": 76, "hip_cm": 96, "length_cm": 67, "stock_qty": 25},
                {"size_label": "L", "chest_cm": 100, "waist_cm": 82, "hip_cm": 102, "length_cm": 69, "stock_qty": 20},
                {"size_label": "XL", "chest_cm": 106, "waist_cm": 88, "hip_cm": 108, "length_cm": 71, "stock_qty": 12},
            ],
        )

        jeans_chart = get_or_create_size_chart(
            db,
            name="Straight Jeans Fit",
            category="jeans",
            rows=[
                {"size_label": "28", "waist_cm": 71, "hip_cm": 94, "length_cm": 102, "stock_qty": 10},
                {"size_label": "30", "waist_cm": 76, "hip_cm": 99, "length_cm": 104, "stock_qty": 18},
                {"size_label": "32", "waist_cm": 81, "hip_cm": 104, "length_cm": 106, "stock_qty": 22},
                {"size_label": "34", "waist_cm": 86, "hip_cm": 109, "length_cm": 108, "stock_qty": 15},
                {"size_label": "36", "waist_cm": 91, "hip_cm": 114, "length_cm": 110, "stock_qty": 8},
            ],
        )
        db.flush()

        get_or_create_clothing(
            db,
            name="Classic Oxford Shirt",
            brand="VirtualFit Basics",
            category="Shirt",
            description="A breathable cotton oxford shirt that works from desk to dinner.",
            primary_color="Navy",
            available_colors=["Navy", "White", "Light Blue"],
            material="100% cotton",
            price=42,
            currency="USD",
            size_chart_id=tops_chart.id,
            fit_type="regular",
            tags=["work", "casual"],
        )
        get_or_create_clothing(
            db,
            name="Everyday Hoodie",
            brand="VirtualFit Basics",
            category="Hoodie",
            description="A relaxed-fit fleece hoodie for daily wear.",
            primary_color="Charcoal",
            available_colors=["Charcoal", "Black"],
            material="80% cotton, 20% polyester",
            price=58,
            currency="USD",
            size_chart_id=tops_chart.id,
            fit_type="relaxed",
            tags=["casual", "streetwear"],
        )
        get_or_create_clothing(
            db,
            name="Straight-Fit Jeans",
            brand="VirtualFit Basics",
            category="Jeans",
            description="Straight-leg denim with a classic mid-rise fit.",
            primary_color="Indigo",
            available_colors=["Indigo", "Black"],
            material="99% cotton, 1% elastane",
            price=65,
            currency="USD",
            size_chart_id=jeans_chart.id,
            fit_type="regular",
            tags=["casual"],
        )
        get_or_create_clothing(
            db,
            name="Minimal Bomber Jacket",
            brand="VirtualFit Basics",
            category="Jacket",
            description="A lightweight bomber jacket with a minimal silhouette.",
            primary_color="Olive",
            available_colors=["Olive", "Black"],
            material="Polyester shell, cotton lining",
            price=89,
            currency="USD",
            size_chart_id=tops_chart.id,
            fit_type="regular",
            tags=["streetwear", "minimal"],
        )

        # These three exist mainly so the Style Advisor (Phase 9) has
        # real bottoms/shoes/tops to coordinate against — without them
        # every color-pairing suggestion would come back empty.
        get_or_create_clothing(
            db,
            name="Classic Chinos",
            brand="VirtualFit Basics",
            category="Pants",
            description="Straight-leg cotton chinos that go with almost everything.",
            primary_color="Beige",
            available_colors=["Beige", "Olive", "Navy"],
            material="98% cotton, 2% elastane",
            price=55,
            currency="USD",
            size_chart_id=jeans_chart.id,
            fit_type="regular",
            tags=["work", "casual"],
        )
        get_or_create_clothing(
            db,
            name="White Canvas Sneakers",
            brand="VirtualFit Basics",
            category="Shoes",
            description="Minimal low-top canvas sneakers.",
            primary_color="White",
            available_colors=["White", "Black"],
            material="Canvas upper, rubber sole",
            price=48,
            currency="USD",
            size_chart_id=None,  # shoe sizing isn't modeled by our chest/waist/hip chart yet
            fit_type=None,
            tags=["casual", "daily"],
        )
        get_or_create_clothing(
            db,
            name="Everyday Tee",
            brand="VirtualFit Basics",
            category="T-shirt",
            description="A soft cotton crewneck tee for daily wear.",
            primary_color="White",
            available_colors=["White", "Black", "Gray"],
            material="100% cotton",
            price=24,
            currency="USD",
            size_chart_id=tops_chart.id,
            fit_type="regular",
            tags=["daily", "casual"],
        )

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
