from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import cursor, conn
import bcrypt
from fastapi.responses import StreamingResponse
import csv
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    msg = request.query_params.get("msg")
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "msg": msg}
    )

@app.get("/test-db")
def test_db():
    try:
        cursor.execute("SELECT 1")
        return {"message": "Database connected successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register")
def register(name: str = Form(...), password: str = Form(...)):

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute(
        "INSERT INTO users (name, password) VALUES (%s, %s)",
        (name, hashed_password)
    )
    conn.commit()

    return RedirectResponse("/?msg=registered", status_code=303)

@app.post("/login")
def login(name: str = Form(...), password: str = Form(...)):

    cursor.execute(
        "SELECT * FROM users WHERE name=%s",
        (name,)
    )

    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(key="user_id", value=str(user["id"]), httponly=True)
        return response
    else:
        return RedirectResponse("/?msg=invalid", status_code=303)

@app.get("/dashboard")
def dashboard(request: Request, category: str = None, sort: str = "date", page: int = 1):

    user_id = request.cookies.get("user_id")
    limit = 5
    offset = (page - 1) * limit

    if not user_id:
        return RedirectResponse("/", status_code=303)
    
    if sort == "amount":
        order = "ORDER BY amount DESC"
    else:
        order = "ORDER BY date DESC"

    if category:
        cursor.execute(
            f"SELECT * FROM expenses WHERE user_id=%s AND category=%s {order} LIMIT %s OFFSET %s",
            (user_id, category, limit, offset)
        )
    else:
        cursor.execute(
            f"SELECT * FROM expenses WHERE user_id=%s {order} LIMIT %s OFFSET %s",
            (user_id, limit, offset)
        )
    expenses = cursor.fetchall()

    if category:
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id=%s AND category=%s GROUP BY category",
            (user_id, category)
        )
    else:
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id=%s GROUP BY category",
            (user_id,)
        )
    
    data = cursor.fetchall()

    labels = [d["category"] for d in data]
    values = [float(d["total"]) for d in data]
    total_expense = sum(values)

    if category:
        cursor.execute(
            "SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(amount) as total FROM expenses WHERE user_id=%s AND category=%s GROUP BY month",
            (user_id, category)
        )
    else:
        cursor.execute(
            "SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(amount) as total FROM expenses WHERE user_id=%s GROUP BY month",
            (user_id,)
        )
    monthly_data = cursor.fetchall()

    months = [m["month"] for m in monthly_data]
    month_totals = [float(m["total"]) for m in monthly_data]

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request":request,
            "expenses":expenses,
            "labels":labels,
            "values":values,
            "total":total_expense,
            "months":months,
            "month_totals":month_totals,
            "page":page or 1,
            "category":category or "",
            "sort":sort or "date"
        }
    )

@app.post("/add")
def add_expense(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    date: str = Form(...)
):
    
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/", status_code=303)
    
    category = category or "Other"
    
    cursor.execute(
        "INSERT INTO expenses (title, amount, category, date, user_id) VALUES (%s,%s,%s,%s,%s)",
        (title, amount, category, date, user_id)
    )

    conn.commit()

    return RedirectResponse("/dashboard", status_code=303)

@app.get("/delete/{id}")
def delete_expense(request: Request, id: int):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)

    cursor.execute("DELETE FROM expenses WHERE id=%s AND user_id=%s", (id, user_id))
    conn.commit()

    return RedirectResponse("/dashboard", status_code=303)

@app.get("/edit/{id}")
def edit_page(request: Request, id: int):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)

    cursor.execute("SELECT * FROM expenses WHERE id=%s AND user_id=%s", (id, user_id))
    expense = cursor.fetchone()

    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "expense": expense}
    )

@app.post("/update/{id}")
def update_expense(
    request: Request,
    id: int,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    date: str = Form(...)
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)
    
    cursor.execute(
        "UPDATE expenses SET title=%s, amount=%s, category=%s, date=%s WHERE id=%s AND user_id=%s",
        (title, amount, category, date, id, user_id)
    )

    conn.commit()

    return RedirectResponse("/dashboard", status_code=303)

@app.get("/download")
def download_report(request: Request):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)
    
    cursor.execute(
        "SELECT title, amount, category, date FROM expenses WHERE user_id=%s",
        (user_id,)
    )
    data = cursor.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Title", "Amount", "Category", "Date"])

    for row in data:
        writer.writerow([row["title"], row["amount"], row["category"], row["date"]])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"}
    )

@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user_id")
    return response