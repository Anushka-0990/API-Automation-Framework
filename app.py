"""
Inventory API — a small FastAPI service used as the Application Under Test
for this API automation framework.

Run from the project root:
    uvicorn api_server.app:app --port 8080

Interactive docs:  http://127.0.0.1:8080/docs
Login (any of):    admin / admin123     qa_user / qa123
"""
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

app = FastAPI(title="Inventory API", version="1.0.0")
security = HTTPBearer(auto_error=False)

# ------------------------------------------------------------- in-memory data
USERS = {"admin": "admin123", "qa_user": "qa123"}
TOKENS = {f"tok-{u}": u for u in USERS}

_products = [
    {"id": 1, "name": "Wireless Mouse", "price": 25.99, "stock": 50, "category": "accessories"},
    {"id": 2, "name": "USB-C Cable", "price": 9.99, "stock": 200, "category": "cables"},
    {"id": 3, "name": "Mechanical Keyboard", "price": 89.00, "stock": 35, "category": "peripherals"},
    {"id": 4, "name": "HD Webcam", "price": 60.00, "stock": 40, "category": "peripherals"},
]
_next_id = 5


# -------------------------------------------------------------------- models
class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price: float = Field(gt=0, description="Price must be positive")
    stock: int = Field(ge=0)
    category: str = "general"


class ProductOut(ProductIn):
    id: int


class LoginIn(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------- dependencies
def current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    if credentials is None or credentials.credentials not in TOKENS:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return TOKENS[credentials.credentials]


# --------------------------------------------------------------------- routes
@app.get("/health")
def health():
    return {"status": "ok", "service": "inventory-api"}


@app.post("/auth/login")
def login(payload: LoginIn):
    if USERS.get(payload.username) != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": f"tok-{payload.username}", "token_type": "bearer"}


@app.get("/products", response_model=list[ProductOut])
def list_products(_: str = Depends(current_user)):
    return _products


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, _: str = Depends(current_user)):
    for p in _products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(payload: ProductIn, _: str = Depends(current_user)):
    global _next_id
    product = {"id": _next_id, **payload.model_dump()}
    _products.append(product)
    _next_id += 1
    return product


@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductIn, _: str = Depends(current_user)):
    for p in _products:
        if p["id"] == product_id:
            p.update(payload.model_dump())
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, _: str = Depends(current_user)):
    global _products
    before = len(_products)
    _products = [p for p in _products if p["id"] != product_id]
    if len(_products) == before:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
