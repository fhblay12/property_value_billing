import csv
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Database import Database
from services.property_service import Property_service
from services.auth import Login
from fastapi import FastAPI, Form, Request, UploadFile, File, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
from typing import Optional
from starlette.responses import StreamingResponse
import plotly.graph_objs as go
import plotly.io as pio
from fastapi.responses import JSONResponse
import qrcode
import secrets
from datetime import datetime, timedelta

def generate_qr_with_token(collector_code, expire_minutes=60):
    # Generate a secure random token
    token = secrets.token_urlsafe(16)

    # Set expiration time
    expiration = datetime.now() + timedelta(minutes=expire_minutes)

    # Save token and expiration in database
    db.execute(
        "UPDATE collectors SET qr_token = %s, qr_token_expiration = %s WHERE collector_id_code = %s",
        (token, expiration, collector_code)
    )


    # Generate URL QR code
    url = f"http://127.0.0.1:8000/scan/{token}"
    img = qrcode.make(url)
    img.save(f"static/qrcodes/{collector_code}.png")



BILLING_MULTIPlIER=0.001

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
#--------------------------------------MYSQL Database connection--------------------------------------------------------------#
db = Database()
login_service = Login(db)

from fastapi.responses import PlainTextResponse
import traceback

@app.exception_handler(Exception)
async def all_exceptions_handler(request, exc):
    return PlainTextResponse(str(traceback.format_exc()))
def build_property_filters(q: str | None, city: str | None, category: int | None, has_been_paid: int | None):
    """
    Returns:
        conditions: list of SQL WHERE clauses
        params: list of parameter values
    """
    conditions = []
    params = []

    if q:
        conditions.append("(p.property_id LIKE %s OR p.city LIKE %s OR p.digital_address LIKE %s OR p.description LIKE %s)")
        search = f"%{q}%"
        params.extend([search, search, search, search])

    if city:
        conditions.append("p.city LIKE %s")
        params.append(f"%{city}%")

    if category:
        conditions.append("p.category_id = %s")
        params.append(category)

    if has_been_paid in ("0", "1"):
        conditions.append("b.has_been_paid = %s")
        params.append(has_been_paid)

    return conditions, params
#--------------------------------HOME----------------------------------------------------------------------------------#
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )
#--------------------------------LOGIN----------------------------------------------------------------------------------#
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return (templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    ))

@app.post("/login")
def submit_form(
    request: Request,
    last_name: str = Form(...),
    password: str = Form(...)
):
    # Try owner login
    login_details=login_service.login(last_name=last_name, password=password)
    print(login_details)
    if login_details[1]=="owner":
        owner_id = login_details[0][0]
        return RedirectResponse(
            url=f"/propertylist/{owner_id}",
            status_code=303
        )
    if login_details[1]=="admin":
        admin_id = login_details[0][0]
        return RedirectResponse(
            url=f"/admin/{admin_id}",
            status_code=303
        )

    if login_details[1]=="collector":
        collector_id = login_details[0][0]
        return RedirectResponse(
            url=f"/collector-home/{collector_id}",
            status_code=303
        )

    # If neither matched
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Invalid credentials"
        }
    )
#---------------------------------ADMIN HOME------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}", response_class=HTMLResponse)
async def admin_login(request: Request, admin_id: int):


    # Fetch category counts
    data=db.execute("SELECT category_id, COUNT(*) FROM properties GROUP BY category_id", fetchall=True)


    labels=["Residential", "Commercial"]
    categories = [row[0] for row in data]
    counts = [row[1] for row in data]

    # Create Pie chart using Plotly
    fig = go.Figure(data=[go.Pie(labels=labels, values=counts, hole=0.3)])
    fig.update_layout(
        title=dict(
            text="Property category",
            font=dict(
                size=20,
                color="#000000",
                family="Arial Black"  # ✅ bold
            )
        ),
        paper_bgcolor="#668cff",  # outside chart
        plot_bgcolor="#668cff",
        font=dict(color="#000000"),
    )

    data=db.execute("SELECT city, COUNT(*) FROM properties GROUP BY city", fetchall=True)




    cities = [row[0] for row in data]
    counts = [row[1] for row in data]

    # Create Pie chart using Plotly
    fig2 = go.Figure(data=[go.Pie(labels=cities, values=counts, hole=0.3)])
    fig2.update_layout(
        title=dict(
            text="Property cities",
            font=dict(
                size=20,
                color="#000000",
                family="Arial Black"  # ✅ bold
            )
        ),
        paper_bgcolor="#668cff",  # outside chart
        plot_bgcolor="#668cff",
        font=dict(color="#000000"),
    )

    # Convert Plotly figure to HTML div
    pie_div = pio.to_html(fig, full_html=False)
    pie_div2 = pio.to_html(fig2, full_html=False)
    count_of_props=db.execute(
    """SELECT COUNT(*)
    FROM
    properties
    WHERE
    created_datetime = CURDATE()""", fetchall=True
    )[0][0]
    number_of_props=str(count_of_props)

    count_of_contacts=db.execute(
    """SELECT COUNT(*)
    FROM
    contacts
    WHERE
    created_datetime = CURDATE()""", fetchall=True
    )[0][0]
    number_of_contacts=str(count_of_contacts)

    count_of_total_props=db.execute(
    """SELECT COUNT(*)
    FROM
    properties
    """, fetchall=True
    )[0][0]
    total_number_of_props=str(count_of_total_props)
    print(number_of_props)

    total_exp_revenue=db.execute(
        """SELECT SUM(monthly_bill) AS total
            FROM billing
        """, fetchall=True
    )[0][0]
    expected_revenue = int(total_exp_revenue)
    print(expected_revenue)
    total_rec_revenue=db.execute(
        """SELECT SUM(monthly_bill) AS total
            FROM billing
            WHERE has_been_paid = 1
        """, fetchall=True
    )[0][0]
    received_revenue = int(total_rec_revenue)
    print(expected_revenue)

    rows=db.execute("""
        SELECT payment_date, SUM(monthly_bill) AS total_revenue
        FROM billing
        WHERE has_been_paid = 1
        GROUP BY payment_date
        ORDER BY payment_date
    """, fetchall=True)

    # Fetch and convert dates
    print(rows)
    date_strings = [row[0].date().isoformat() for row in rows]
    revenue = [row[1] for row in rows]


    # Create Plotly line chart
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=date_strings,
        y=revenue,
        name='Revenue',

    ))

    # Dark theme
    fig3.update_layout(
    title=dict(
        text="Daily Revenue",
        font=dict(
            size=20,
            color="#000000",
            family="Arial Black"  # ✅ bold
        )
    ),
    paper_bgcolor="#668cff",
    plot_bgcolor="#668cff",
    font=dict(color="#000000"),
    )

    # Convert to HTML div for FastAPI template
    chart_html = pio.to_html(fig3, full_html=False)

    return templates.TemplateResponse(
        "admin_home.html",
        {
            "admin_id": admin_id,
            "pie_div": pie_div,
            "pie_div2": pie_div2,
            "chart_div": chart_html,
            "number_of_props": number_of_props,
            "number_of_contacts": number_of_contacts,
            "total_number_of_props": total_number_of_props,
            "expected_revenue": expected_revenue,
            "received_revenue": received_revenue,
            "request": request,

        }
    )

#---------------------------------ADMIN PROPERTY_LIST------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}/property_list", response_class=HTMLResponse)
async def admin_property_list(
    request: Request,
    admin_id: int,
    q: str | None = Query(None),
    city: str | None = Query(None),
    category: str | None = Query(None),
    has_been_paid: str | None = Query(None),
):


    base_query = """
        SELECT p.*, b.has_been_paid
        FROM properties p
        JOIN billing b ON p.property_id = b.property_id
        
    """

    conditions, filter_params = build_property_filters(q, city, category, has_been_paid)
    params =  filter_params

    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    rows=db.execute(base_query, tuple(params), fetchall=True)


    # Map category_id to human-readable
    categories = ["residential" if row[1] == 1 else "commercial" for row in rows]
    paid_or_not = ["Yes" if str(row[-1]) == "1" else "No" for row in rows]

    combined = zip(rows, categories, paid_or_not)

    return templates.TemplateResponse(
        "admin_propertylist.html",
        {"request": request, "combined": combined, "admin_id": admin_id},
    )


@app.get("/admin/{admin_id}/export-csv")
def export_properties_csv(
    admin_id: int,
    q: str | None = None,
    city: str | None = None,
    category: str | None = None,
    has_been_paid: str | None = None
):


    base_query = """
        SELECT p.property_id, p.digital_address, p.city,
               b.monthly_bill, b.billing_date, b.has_been_paid
        FROM properties p
        JOIN billing b ON p.property_id = b.property_id
        
    """

    conditions, filter_params = build_property_filters(q, city, category, has_been_paid)
    params =  filter_params

    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    rows=db.execute(base_query, tuple(params), fetchall=True)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["# Property export"])
    writer.writerow([f"# Generated by admin_id: {admin_id}"])
    writer.writerow([f"# Filters: q={q}, city={city}, category={category}, paid={has_been_paid}"])
    writer.writerow([])  # blank line for readability

    writer.writerow(["property_id", "digital_address", "city", "monthly_bill", "billing_date", "has_been_paid"])
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=properties.csv"}
    )
#---------------------------------ADMIN CONTACT_LIST------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}/contact_list", response_class=HTMLResponse)
async def contact_list(request: Request, admin_id: int, q: str | None = Query(None)):
    if q:
        search = f"%{q}%"
        row=db.execute("""
                SELECT * FROM contacts WHERE  (
                      first_name LIKE %s
                      OR last_name LIKE %s
                      OR phone_number LIKE %s

                    ) 
        """, (search, search, search), fetchall=True
                       )
    else:
        row=db.execute("""
            SELECT * FROM CONTACTS
        """, fetchall=True)
    contacts=row
    print(contacts)
    return templates.TemplateResponse(
        "contact_list.html",
        {
            "admin_id": admin_id,
            "contacts": contacts,
            "request": request,
        }
    )
#--------------------------------ADMIN PROPERTY VIEW------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}/property_view/{property_id}", response_class=HTMLResponse)
async def admin_property_view(request: Request, admin_id: int, property_id: int):

    property_view=db.execute(
        """
        SELECT
            *
        FROM properties
        WHERE property_id = %s 
        """,
        (property_id,), fetchone=True
    )
    if property_view:
        property_view = list(property_view)
        if isinstance(property_view[8], (bytes, bytearray)):
            property_view[8] = property_view[8].decode("utf-8")
        property_view = tuple(property_view)

    print(property_view)
    billing=db.execute(
        """
        SELECT
            *
        FROM billing
        WHERE property_id = %s 
        """,
        (property_id,), fetchone=True
    )
    return templates.TemplateResponse(
        "admin_propertyview.html",
        {
            "property_view": property_view,
            "property_id": property_id,
            "admin_id": admin_id,
            "billing": billing,
            "request": request,

        }
    )
#--------------------------------ADMIN CONTACT VIEW------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}/contact_view/{owner_id}", response_class=HTMLResponse)
async def admin_property_view(request: Request, admin_id: int, owner_id: int):

    contact_view=db.execute(
        """
        SELECT
            *
        FROM contacts
        WHERE owner_id = %s 
        """,
        (owner_id,), fetchone=True
    )


    properties_of_contact=db.execute("""
                SELECT * FROM properties
                WHERE owner_id = %s
            """, (owner_id,), fetchall=True)
    return templates.TemplateResponse(
        "admin_contactview.html",
        {
            "contact_view": contact_view,
            "properties_of_contact": properties_of_contact,
            "admin_id": admin_id,
            "request": request,

        }
    )

#--------------------------------PROPERTY LIST----------------------------------------------------------------------------------#
@app.get("/propertylist/{owner_id}", response_class=HTMLResponse)
async def show_property_list(
    request: Request,
    owner_id: int,
    q: str | None = Query(None),
    city: str | None = Query(None),
    category: str | None = Query(None),
    has_been_paid: str | None = Query(None)
):
    base_query = """
        SELECT
            p.property_id,
            p.category_id,
            p.digital_address,
            p.city,
            b.monthly_bill,
            b.billing_date,
            b.has_been_paid
        FROM properties p
        JOIN billing b ON p.property_id = b.property_id
        WHERE p.owner_id = %s
    """

    conditions = []
    params = [owner_id]

    # 🔍 General search
    if q:
        conditions.append("""
            ( p.digital_address LIKE %s)
        """)
        search = f"%{q}%"
        params.extend([search])

    # 🏙️ City filter
    if city:
        conditions.append("p.city LIKE %s")
        params.append(f"%{city}%")

    # 🗂️ Category filter
    if category in ("1", "2"):
        conditions.append("p.category_id = %s")
        params.append(category)

    if has_been_paid in ("1", "0"):
        conditions.append("b.has_been_paid = %s")
        params.append(has_been_paid)

    # ➕ Append filters
    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    # 🧪 Debug (optional)
    # print(base_query)
    # print(params)

    property_list=db.execute(base_query, tuple(params), False , True)
    print(property_list)
    category_id = [property[1] for property in property_list]
    has_been_paid = [property[6] for property in property_list]
    old_value = 1
    category1 = "residential"
    category2 = "commercial"
    paid="Yes"
    not_paid="No"
    categories = [category1 if id == old_value else category2 for id in category_id]
    paid_or_not = [paid if item == 1 else not_paid for item in has_been_paid]
    combined = zip(property_list, categories, paid_or_not)
    #print(categories)
    print(has_been_paid)

    return templates.TemplateResponse(
        "property_list.html",
        {
            "request": request,
            "combined": combined,
            "q": q,
            "owner_id": owner_id
        }
    )

@app.post("/propertylist/{owner_id}")
async def submit_form(owner_id: int):
    property_id=db.execute(
        """
        SELECT property_id FROM properties
        WHERE owner_id = %s
        """,
        (owner_id, ), fetchall=True
    )



    return RedirectResponse(
        url=f"/pay/{property_id}",
        status_code=303
    )

#--------------------------------PROPERTY------------------------------------------------------------------------------#
@app.get("/property", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse(
        "property.html",
        {"request": request}
    )

@app.post("/property")
async def submit_form(
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(... ),
    category: int = Form(...),
    property_value: int = Form(...),
    longitude: float = Form(...),
    latitude: float = Form(...),
    city: str = Form(...),
    digital_address: str = Form(...),
    description: str = Form(...),
    password: str = Form(...)
):
    first_name = first_name.title()
    last_name = last_name.title()
    city = city.title()
    owner_id=Property_service.create_contact(first_name, last_name, phone_number, email, password)
    property_id=Property_service.create_property(owner_id, category, property_value, longitude, latitude, city, digital_address, description)
    Property_service.create_monthly_bill(property_id, property_value)
    return RedirectResponse(
        url=f"/image&docs/{property_id}",
        status_code=303  # 303 ensures browser performs a GET
    )


#--------------------------------IMAGE AND DOCS------------------------------------------------------------------------------#


@app.get("/image&docs/{property_id}", response_class=HTMLResponse)
async def show_image_docs_form(request: Request, property_id: int):
    return templates.TemplateResponse(
        "image&docs.html",
        {
            "request": request,
            "property_id": property_id
        }
    )

@app.post("/image&docs/{property_id}")
async def submit_form(
    property_id: int,
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    image3: Optional[UploadFile] = File(None),
    image4: Optional[UploadFile] = File(None),
    document1: UploadFile = File(...),
    document2: UploadFile = File(...),
    document3: Optional[UploadFile] = File(None),
    document4: Optional[UploadFile] = File(None),
):
    await Property_service.add_property_files(property_id, image1, image2, image3, image4, document1, document2, document3, document4)

    return RedirectResponse(
        url="/",
        status_code=303
    )

#--------------------------------------------------------------------ADD PROPERTY---------------------------------------------------------------------------------------------#
@app.get("/addproperty/{owner_id}", response_class=HTMLResponse)
async def show_form(request: Request, owner_id : int):
    return templates.TemplateResponse(
        "add_property.html",
        {"request": request,
         "owner_id": owner_id}
    )


@app.post("/addproperty/{owner_id}")
async def submit_form(
        owner_id: int,
        category: int = Form(...),
        property_value: int = Form(...),
        longitude: float = Form(...),
        latitude: float = Form(...),
        city: str = Form(...),
        digital_address: str = Form(...),
        description: str = Form(...)
):
    created_time = datetime.now()
    property_id=Property_service.create_property(owner_id, category, property_value, longitude, latitude, city, digital_address, description)
 
  
    return RedirectResponse(
        url=f"/image&docs/{property_id}",
        status_code=303  # 303 ensures browser performs a GET
    )


#--------------------------------PAY------------------------------------------------------------------------------#
@app.get("/pay/{property_id}", response_class=HTMLResponse)
async def show_form(request: Request, property_id: int):
    db.execute(
        """
        UPDATE billing
        SET has_been_paid = %s
        WHERE property_id = %s
        """,
        (1, property_id)
    )
    created_time = datetime.now()
    db.execute(
        """
        UPDATE billing
        SET payment_date = %s
        WHERE property_id = %s
        """,
        (created_time, property_id)
    )

    return templates.TemplateResponse(
        "pay.html",
        {"request": request,
         "property_id": property_id}
    )

#--------------------------------------------------------------MAP OF ALL PROPERTIES-------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}/property_map")
async def submit_form(request: Request, admin_id: int):

    sql = """
        SELECT latitude, longitude FROM properties
    """

    lat_long=db.execute(sql, fetchall=True)
    lat_long_floats = [(float(lat), float(lng)) for lat, lng in lat_long]
    print(lat_long_floats)

    sql = """
        SELECT b.has_been_paid
        FROM billing b
        JOIN properties p ON p.property_id = b.property_id
    """

    paid_or_not=db.execute(sql, fetchall=True)
    paid_or_not=[item[0] for item in paid_or_not]
    print(paid_or_not)

    sql = """
            SELECT property_id 
            FROM properties
            ORDER BY property_id
    """
    property_ids=[item[0] for item in db.execute(sql, fetchall=True)]
    print(property_ids)
    return templates.TemplateResponse(
        "property_map.html",
        {
            "request": request,
            "lat_long": lat_long_floats,
            "paid_or_not": paid_or_not,
            "admin_id": admin_id,
            "property_ids": property_ids
        }
    )

#----------------------------------------------------------------COLLECTOR HOME PAGE -------------------------------------------------------------------------------#
@app.get("/collector-home/{collector_id_code}", response_class=HTMLResponse)
async def collector_home(request: Request, collector_id_code: str):
    # No user location yet
    return templates.TemplateResponse(
        "collector-home.html",
        {"request": request}
    )

from fastapi import Query
from fastapi.responses import JSONResponse

@app.get("/api/nearby-properties")
async def nearby_properties(lat: float = Query(...), lng: float = Query(...)):
    sql = """
        SELECT 
    p.property_id,
    p.digital_address,
    c. first_name,
    c.last_name,
    c.phone_number,
    c.email,
    p.latitude, 
    p.longitude,
    b.has_been_paid
FROM properties p
JOIN billing b ON b.property_id = p.property_id
join contacts c ON c.owner_id = p.owner_id
WHERE ST_Distance_Sphere(
    POINT(p.longitude, p.latitude),
    POINT(%s, %s)
) <= 5000
AND b.has_been_paid =0
    """
    rows=db.execute(sql, (lng, lat), fetchall=True)  # ⚠️ Order matters: POINT(lng, lat)
    properties = []
    for row in rows:
        properties.append({
            "id": row[0],
            "digital_address": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "phone_number": row[4],
            "email": row[5],
            "latitude": float(row[6]),
            "longitude": float(row[7]),
            "has_been_paid": bool(row[8])
        })
    print(properties)
    return JSONResponse(properties)


#----------------------------------------------------------Collectors List --------------------------------------------------------------------------------------------------------#
@app.get("/admin/{admin_id}/collector_list", response_class=HTMLResponse)
async def admin_login(request: Request, admin_id: int):
    # Fetch category counts
    collectors = db.execute("SELECT * FROM collectors", fetchall=True)
    work_status = ["not at work" if item[7] == 0 else "at work" for item in collectors]
    id_codes=[item[1] for item in collectors]
    for code in id_codes:
        generate_qr_with_token(code, 60)
    combined = zip(collectors, work_status)
    print(collectors)
    return templates.TemplateResponse(
        "collectors_list.html",
        {
            "admin_id": admin_id,
            "collectors": combined,
            "request": request,

        }
    )

@app.post("/admin/{admin_id}/update_collector")
async def update_collector(
    admin_id: int,
    collector_id: str = Form(...),
    work_status: int = Form(...)
):
    db.execute(
        "UPDATE collectors SET at_work = %s WHERE collector_id_code = %s",
        (work_status, collector_id)
    )

    return RedirectResponse(
        url=f"/admin/{admin_id}/collector_list",
        status_code=303
    )
#------------------------------------------------------------------------QR CODE----------------------------------------------------------------------------------------------------#
@app.get("/scan/{token}", response_class=HTMLResponse)
async def scan_collector(token: str):
    # Look up collector by token
    result=db.execute(
        "SELECT collector_id_code, qr_token_expiration FROM collectors WHERE qr_token = %s",
        (token,),fetchone=True
    )

    if not result:
        return HTMLResponse("<h2>Invalid QR Code</h2>", status_code=400)

    collector_code, expiration = result

    # Check if token expired
    now = datetime.now()
    if expiration < now:
        return HTMLResponse("<h2>QR Code Expired</h2>", status_code=400)

    # Mark as at work
    db.execute(
        "UPDATE collectors SET at_work = %s WHERE qr_token = %s",
        (1, token), fetchone=True
    )


    # Optional: insert into attendance log
    db.execute(
        "INSERT INTO attendance (collector_id_code, check_in) VALUES (%s, %s)",
        (collector_code, now), fetchone=True
    )


    return f"""
    <h2>Welcome!</h2>
    <p>Collector {collector_code} marked as AT WORK.</p>
    <p>Time: {now}</p>
    """