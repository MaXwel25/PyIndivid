from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response

import sqlite3

app = FastAPI()

templates = Jinja2Templates(directory="pages")

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

def init_db():
    conn = sqlite3.connect('archaeology.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS sites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL,
                  location TEXT,
                  period TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS archaeologists
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  specialization TEXT,
                  site_id INTEGER NOT NULL,
                  FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS finds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  material TEXT,
                  find_type TEXT,
                  archaeologist_id INTEGER NOT NULL,
                  FOREIGN KEY (archaeologist_id) REFERENCES archaeologists(id) ON DELETE CASCADE)''')
    
    conn.commit()
    conn.close()

init_db()



@app.get("/")
def read_root(request: Request):
    conn = sqlite3.connect('archaeology.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT s.name as site_name, s.location, s.period,
                   a.name as archaeologist_name, a.specialization,
                   f.name as find_name, f.material, f.find_type
            FROM sites s
            JOIN archaeologists a ON s.id = a.site_id
            JOIN finds f ON a.id = f.archaeologist_id
        ''')
        all_data = c.fetchall()
        
        c.execute("SELECT * FROM sites")
        sites = c.fetchall()
        
        c.execute("SELECT * FROM archaeologists")
        archaeologists = c.fetchall()
        
        c.execute("SELECT * FROM finds")
        finds = c.fetchall()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "all_data": all_data,
            "sites": sites,
            "archaeologists": archaeologists,
            "finds": finds
        })
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.post("/add_site")
def add_site(name: str = Form(...), location: str = Form(...), period: str = Form(...)):
    conn = sqlite3.connect('archaeology.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO sites (name, location, period) VALUES (?, ?, ?)", 
                 (name, location, period))
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/add_archaeologist")
def add_archaeologist(name: str = Form(...), specialization: str = Form(...), site_id: int = Form(...)):
    conn = sqlite3.connect('archaeology.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO archaeologists (name, specialization, site_id) VALUES (?, ?, ?)", 
                 (name, specialization, site_id))
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/add_find")
def add_find(name: str = Form(...), material: str = Form(...), find_type: str = Form(...), archaeologist_id: int = Form(...)):
    conn = sqlite3.connect('archaeology.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO finds (name, material, find_type, archaeologist_id) VALUES (?, ?, ?, ?)", 
                 (name, material, find_type, archaeologist_id))
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)

# Экспорт находок в XML
@app.get("/export_xml")
def export_xml():
    try:
        conn = sqlite3.connect('archaeology.db')
        c = conn.cursor()
        
        # Получаем находки с информацией об археологе и сайте
        c.execute('''
            SELECT f.*, a.name as archaeologist_name, s.name as site_name 
            FROM finds f 
            JOIN archaeologists a ON f.archaeologist_id = a.id
            JOIN sites s ON a.site_id = s.id
        ''')
        finds = c.fetchall()
        conn.close()
        
        # Создаем XML с построчной записью
        xml_lines = []
        xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_lines.append('<artifacts>')
        xml_lines.append('')  # Пустая строка для разделения
        
        for find in finds:
            xml_lines.append('  <artifact>')
            xml_lines.append(f'    <id>{find[0]}</id>')
            xml_lines.append(f'    <name>{find[1] or ""}</name>')
            xml_lines.append(f'    <material>{find[2] or ""}</material>')
            xml_lines.append(f'    <type>{find[3] or ""}</type>')
            xml_lines.append(f'    <archaeologist_id>{find[4] or ""}</archaeologist_id>')
            xml_lines.append(f'    <archaeologist_name>{find[5] or ""}</archaeologist_name>')
            xml_lines.append(f'    <site_name>{find[6] or ""}</site_name>')
            xml_lines.append('  </artifact>')
            xml_lines.append('')  # Пустая строка между артефактами
        
        xml_lines.append('</artifacts>')
        xml_content = '\n'.join(xml_lines)  # Каждая строка в отдельной линии
        
        return Response(
            content=xml_content,
            media_type="application/xml", 
            headers={"Content-Disposition": "attachment; filename=artifacts.xml"}
        )
        
    except Exception as e:
        return {"error": f"Failed to export XML: {str(e)}"}
