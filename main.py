from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import json
from pathlib import Path

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    transaction_file = Path("data/transactions.json")
    category_file = Path("data/categories.json")

    if transaction_file.exists():
        with transaction_file.open("r", encoding="utf-8") as f:
            transactions = json.load(f)
    else:
        transactions = []

    with category_file.open("r", encoding="utf-8") as f:
        categories = json.load(f)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "transactions": transactions,
            "categories": categories
        }
    )

@app.post("/transactions")
def create_transaction(
    date: str = Form(),
    category: str = Form(),
    amount: int = Form(),
    memo: str | None = Form(None)
):

    file_path = Path("data/transactions.json")

    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as f:
            transactions = json.load(f)
    else:
        transactions = []

    if transactions:
        new_id = max(transaction["id"] for transaction in transactions) + 1
    else:
        new_id = 1

    transaction = {
        "id": new_id,
        "date": date,
        "category": category,
        "amount": amount,
        "memo": memo
    }

    transactions.append(transaction)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)

    return RedirectResponse("/", status_code=303)

@app.post("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    file_path = Path("data/transactions.json")

    with file_path.open("r", encoding="utf-8") as f:
        transactions = json.load(f)

    transactions = [
        transaction
        for transaction in transactions
        if transaction["id"] != transaction_id
    ]

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)

    return RedirectResponse("/", status_code=303)

@app.get("/transactions/{transaction_id}/edit")
def edit_transaction(request: Request, transaction_id: int):
    file_path = Path("data/transactions.json")

    with file_path.open("r", encoding="utf-8") as f:
        transactions = json.load(f)

    transaction = next(
        transaction
        for transaction in transactions
        if transaction["id"] == transaction_id
    )

    category_file = Path("data/categories.json")

    with category_file.open("r", encoding="utf-8") as f:
        categories = json.load(f)

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={
            "transaction": transaction,
            "categories": categories
        }
    )

@app.post("/transactions/{transaction_id}/edit")
def update_transaction(
    transaction_id: int,
    date: str = Form(),
    category: str = Form(),
    amount: int = Form(),
    memo: str | None = Form(None)
):
    file_path = Path("data/transactions.json")

    with file_path.open("r", encoding="utf-8") as f:
        transactions = json.load(f)

    for transaction in transactions:
        if transaction["id"] == transaction_id:
            transaction["date"] = date
            transaction["category"] = category
            transaction["amount"] = amount
            transaction["memo"] = memo

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)

    return RedirectResponse("/", status_code=303)

@app.post("/categories")
def create_category(category: str = Form()):
    file_path = Path("data/categories.json")

    with file_path.open("r", encoding="utf-8") as f:
        categories = json.load(f)

    if category not in categories:
        categories.append(category)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    return RedirectResponse("/", status_code=303)
