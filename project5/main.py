from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response

import xml.etree.ElementTree as ET
import os
import io
import sqlite3

app = FastAPI()

templates = Jinja2Templates(directory="pages")


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


def init_db():
    conn = sqlite3.connect("archaeology.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS sites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL,
                  location TEXT,
                  period TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS archaeologists
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  specialization TEXT,
                  site_id INTEGER NOT NULL,
                  FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE)""")

    c.execute("""CREATE TABLE IF NOT EXISTS finds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  material TEXT,
                  find_type TEXT,
                  archaeologist_id INTEGER NOT NULL,
                  FOREIGN KEY (archaeologist_id) REFERENCES archaeologists(id) ON DELETE CASCADE)""")

    conn.commit()
    conn.close()


init_db()


@app.get("/")
def read_root(request: Request):
    conn = sqlite3.connect("archaeology.db")
    c = conn.cursor()

    try:
        site_error = request.query_params.get('site_error')
        archaeologist_error = request.query_params.get('archaeologist_error')
        find_error = request.query_params.get('find_error')
        import_success = request.query_params.get('import_success')
        imported_count = request.query_params.get('imported_count')
        import_error = request.query_params.get('import_error')
        error_message = request.query_params.get('error_message')

        c.execute("""
            SELECT s.name as site_name, s.location, s.period,
                   a.name as archaeologist_name, a.specialization,
                   f.name as find_name, f.material, f.find_type
            FROM sites s
            JOIN archaeologists a ON s.id = a.site_id
            JOIN finds f ON a.id = f.archaeologist_id
        """)
        all_data = c.fetchall()

        c.execute("SELECT * FROM sites")
        sites = c.fetchall()

        c.execute("SELECT * FROM archaeologists")
        archaeologists = c.fetchall()

        c.execute("SELECT * FROM finds")
        finds = c.fetchall()

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "all_data": all_data,
                "sites": sites,
                "archaeologists": archaeologists,
                "finds": finds,
                "site_error": site_error,
                "archaeologist_error": archaeologist_error,
                "find_error": find_error,
                "import_success": import_success,
                "imported_count": imported_count,
                "import_error": import_error,
                "error_message": error_message,
            },
        )
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


@app.post("/add_site")
def add_site(name: str = Form(...), location: str = Form(...), period: str = Form(...)):
    conn = sqlite3.connect("archaeology.db")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO sites (name, location, period) VALUES (?, ?, ?)",
            (name, location, period),
        )
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)


@app.post("/add_archaeologist")
def add_archaeologist(
    name: str = Form(...), specialization: str = Form(...), site_id: int = Form(...)
):
    conn = sqlite3.connect("archaeology.db")
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM sites WHERE id = ?", (site_id,))
        site = c.fetchone()
        
        if not site:
            return RedirectResponse(f"/?archaeologist_error=true&error_message=Сайт с ID {site_id} не существует", status_code=303)
        
        c.execute(
            "INSERT INTO archaeologists (name, specialization, site_id) VALUES (?, ?, ?)",
            (name, specialization, site_id),
        )
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)


@app.post("/add_find")
def add_find(
    name: str = Form(...),
    material: str = Form(...),
    find_type: str = Form(...),
    archaeologist_id: int = Form(...),
):
    conn = sqlite3.connect("archaeology.db")
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM archaeologists WHERE id = ?", (archaeologist_id,))
        archaeologist = c.fetchone()
        
        if not archaeologist:
            return RedirectResponse(f"/?find_error=true&error_message=Археолог с ID {archaeologist_id} не существует", status_code=303)
        
        c.execute(
            "INSERT INTO finds (name, material, find_type, archaeologist_id) VALUES (?, ?, ?, ?)",
            (name, material, find_type, archaeologist_id),
        )
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)


@app.get("/export_xml")
def export_xml():
    try:
        conn = sqlite3.connect("archaeology.db")
        c = conn.cursor()

        c.execute("""
            SELECT f.*, a.name as archaeologist_name, s.name as site_name 
            FROM finds f 
            JOIN archaeologists a ON f.archaeologist_id = a.id
            JOIN sites s ON a.site_id = s.id
        """)
        finds = c.fetchall()
        conn.close()

        xml_lines = []
        xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_lines.append("<artifacts>")
        xml_lines.append("\n")

        for find in finds:
            xml_lines.append("  <artifact>")
            xml_lines.append(f"    <id>{find[0]}</id>")
            xml_lines.append(f"    <name>{find[1] or ''}</name>")
            xml_lines.append(f"    <material>{find[2] or ''}</material>")
            xml_lines.append(f"    <type>{find[3] or ''}</type>")
            xml_lines.append(
                f"    <archaeologist_id>{find[4] or ''}</archaeologist_id>"
            )
            xml_lines.append(
                f"    <archaeologist_name>{find[5] or ''}</archaeologist_name>"
            )
            xml_lines.append(f"    <site_name>{find[6] or ''}</site_name>")
            xml_lines.append("  </artifact>")
            xml_lines.append("\n")

        xml_lines.append("</artifacts>")
        xml_content = "\n".join(xml_lines)

        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=artifacts.xml"},
        )

    except Exception as e:
        return {"error": f"Failed to export XML: {str(e)}"}


@app.post("/import_xml")
async def import_xml(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.xml'):
            return RedirectResponse("/?import_error=true&error_message=Неверный тип файла. Загрузите XML файл.", status_code=303)
        
        content = await file.read()
        try:
            xml_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                xml_content = content.decode('utf-16')
            except:
                xml_content = content.decode('latin-1')
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            return RedirectResponse(f"/?import_error=true&error_message=Ошибка парсинга XML: {str(e)}", status_code=303)
        
        conn = sqlite3.connect("archaeology.db")
        c = conn.cursor()
        
        imported_count = 0
        errors = []
        
        artifacts = root.findall('artifact') or root.findall('artifacts/artifact') or root.findall('find') or root.findall('finds/find') or [root]
        
        for artifact in artifacts:
            try:
                name_elem = artifact.find('name')
                material_elem = artifact.find('material')
                find_type_elem = artifact.find('type') or artifact.find('find_type')
                archaeologist_id_elem = artifact.find('archaeologist_id')
                
                name = name_elem.text if name_elem is not None else ''
                material = material_elem.text if material_elem is not None else ''
                find_type = find_type_elem.text if find_type_elem is not None else ''
                archaeologist_id = archaeologist_id_elem.text if archaeologist_id_elem is not None else ''
                
                if not name:
                    errors.append("Отсутствует название артефакта")
                    continue
                
                if not archaeologist_id:
                    errors.append(f"Отсутствует ID археолога для артефакта: {name}")
                    continue
                
                try:
                    archaeologist_id_int = int(archaeologist_id)
                except ValueError:
                    errors.append(f"Неверный формат ID археолога для артефакта: {name}")
                    continue
                
                c.execute("SELECT id FROM archaeologists WHERE id = ?", (archaeologist_id_int,))
                archaeologist = c.fetchone()
                
                if not archaeologist:
                    errors.append(f"Археолог с ID {archaeologist_id_int} не существует для артефакта: {name}")
                    continue
                
                c.execute("SELECT id FROM finds WHERE name = ? AND archaeologist_id = ?", 
                         (name, archaeologist_id_int))
                existing_find = c.fetchone()
                
                if not existing_find:
                    c.execute("INSERT INTO finds (name, material, find_type, archaeologist_id) VALUES (?, ?, ?, ?)",
                             (name, material, find_type, archaeologist_id_int))
                    imported_count += 1
                else:
                    errors.append(f"Артефакт {name} уже существует для археолога ID {archaeologist_id_int}")
                
            except Exception as e:
                errors.append(f"Ошибка импорта артефакта: {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        if errors:
            error_msg = f"Импортировано {imported_count} артефактов с ошибками: {'; '.join(errors[:5])}"
            return RedirectResponse(f"/?import_success=true&imported_count={imported_count}&import_error=true&error_message={error_msg}", status_code=303)
        else:
            return RedirectResponse(f"/?import_success=true&imported_count={imported_count}", status_code=303)
        
    except Exception as e:
        return RedirectResponse(f"/?import_error=true&error_message={str(e)}", status_code=303)
