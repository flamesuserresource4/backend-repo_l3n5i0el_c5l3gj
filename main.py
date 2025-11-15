import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Organimo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class ProductModel(BaseModel):
    title: str
    slug: str
    description: str
    price: float
    sku: str
    category: str
    image: str
    badges: List[str] = []
    rating: float = 5.0
    reviews: int = 0

# ---------- Helpers ----------

def seed_products_if_needed():
    try:
        from database import db
        if db is None:
            return
        col = db["product"]
        if col.count_documents({}) == 0:
            sample_products = [
                {
                    "title": "Organimo® Sea Moss Gel",
                    "slug": "sea-moss-gel",
                    "description": "Premium wildcrafted Sea Moss gel infused with Bladderwrack for a daily wellness boost.",
                    "price": 29.99,
                    "sku": "ORG-SM-001",
                    "category": "gel",
                    "image": "https://images.unsplash.com/photo-1604909052743-89d4387d9453?q=80&w=1200&auto=format&fit=crop",
                    "badges": ["Vegan", "Non-GMO", "Gluten-Free", "No Preservatives", "Harvested in Canada"],
                    "rating": 4.9,
                    "reviews": 312,
                },
                {
                    "title": "Organimo® Sea Moss Capsules",
                    "slug": "sea-moss-capsules",
                    "description": "Convenient daily capsules with Sea Moss + Bladderwrack for energy and immune support.",
                    "price": 24.99,
                    "sku": "ORG-SM-002",
                    "category": "capsules",
                    "image": "https://images.unsplash.com/photo-1590686576338-71b9362b61fe?q=80&w=1200&auto=format&fit=crop",
                    "badges": ["Vegan", "Non-GMO", "No Preservatives"],
                    "rating": 4.8,
                    "reviews": 198,
                },
                {
                    "title": "Organimo® Sea Moss + Bladderwrack Powder",
                    "slug": "sea-moss-powder",
                    "description": "Fine powder blend perfect for smoothies and recipes.",
                    "price": 27.0,
                    "sku": "ORG-SM-003",
                    "category": "powder",
                    "image": "https://images.unsplash.com/photo-1517433456452-f9633a875f6f?q=80&w=1200&auto=format&fit=crop",
                    "badges": ["Vegan", "Gluten-Free"],
                    "rating": 4.7,
                    "reviews": 154,
                },
            ]
            col.insert_many(sample_products)
    except Exception:
        # fail silently; API will still work for non-DB endpoints
        pass

seed_products_if_needed()

# ---------- Routes ----------

@app.get("/")
def read_root():
    return {"message": "Organimo® API is running"}

@app.get("/api/products", response_model=List[ProductModel])
def list_products(category: Optional[str] = None):
    """List products from database, optionally filter by category."""
    try:
        from database import db
        col = db["product"] if db else None
    except Exception:
        col = None

    products: List[ProductModel] = []
    if col is not None:
        query = {"category": category} if category else {}
        for p in col.find(query):
            products.append(ProductModel(
                title=p.get("title"),
                slug=p.get("slug"),
                description=p.get("description", ""),
                price=float(p.get("price", 0)),
                sku=p.get("sku", ""),
                category=p.get("category", ""),
                image=p.get("image", ""),
                badges=p.get("badges", []),
                rating=float(p.get("rating", 5.0)),
                reviews=int(p.get("reviews", 0)),
            ))
    else:
        # Fallback sample data if DB unavailable
        fallback = [
            ProductModel(
                title="Organimo® Sea Moss Gel",
                slug="sea-moss-gel",
                description="Premium wildcrafted Sea Moss gel infused with Bladderwrack for a daily wellness boost.",
                price=29.99,
                sku="ORG-SM-001",
                category="gel",
                image="https://images.unsplash.com/photo-1604909052743-89d4387d9453?q=80&w=1200&auto=format&fit=crop",
                badges=["Vegan", "Non-GMO", "Gluten-Free", "No Preservatives", "Harvested in Canada"],
                rating=4.9,
                reviews=312,
            )
        ]
        products = [p for p in fallback if (not category or p.category == category)]

    return products

@app.get("/api/products/{slug}", response_model=ProductModel)
def get_product(slug: str):
    try:
        from database import db
        col = db["product"] if db else None
    except Exception:
        col = None

    if col is not None:
        p = col.find_one({"slug": slug})
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductModel(
            title=p.get("title"),
            slug=p.get("slug"),
            description=p.get("description", ""),
            price=float(p.get("price", 0)),
            sku=p.get("sku", ""),
            category=p.get("category", ""),
            image=p.get("image", ""),
            badges=p.get("badges", []),
            rating=float(p.get("rating", 5.0)),
            reviews=int(p.get("reviews", 0)),
        )
    else:
        # Fallback
        if slug == "sea-moss-gel":
            return ProductModel(
                title="Organimo® Sea Moss Gel",
                slug="sea-moss-gel",
                description="Premium wildcrafted Sea Moss gel infused with Bladderwrack for a daily wellness boost.",
                price=29.99,
                sku="ORG-SM-001",
                category="gel",
                image="https://images.unsplash.com/photo-1604909052743-89d4387d9453?q=80&w=1200&auto=format&fit=crop",
                badges=["Vegan", "Non-GMO", "Gluten-Free", "No Preservatives", "Harvested in Canada"],
                rating=4.9,
                reviews=312,
            )
        raise HTTPException(status_code=404, detail="Product not found")

class CheckoutRequest(BaseModel):
    items: List[dict]
    email: Optional[str] = None
    address: Optional[str] = None

@app.post("/api/checkout")
def checkout(payload: CheckoutRequest):
    # Placeholder checkout - in real app integrate Stripe/Razorpay
    total = 0.0
    for item in payload.items:
        try:
            qty = float(item.get("qty", 1))
            price = float(item.get("price", 0))
            total += qty * price
        except Exception:
            continue
    return {"status": "ok", "message": "Checkout initialized", "total": round(total, 2)}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
