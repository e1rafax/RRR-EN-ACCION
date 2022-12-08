from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from deta import Deta
import os
from pydantic import BaseModel, Field, AnyUrl
from fastapi import FastAPI, Query, Path, HTTPException, status, Body, Request, Response, File, UploadFile, Form
from typing import Optional, List, Dict


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

deta = Deta("b0pzdasf_ZqYjujH37D24AgyrrLJbyRV2gtAadCHu")
users = deta.Base("users")


class User(BaseModel):
    fullname: str
    code: str
    gender: str
    email: str
    password: str


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("Login.html",
                                      {"request": request,
                                       "title": "welcome"})


@app.get("/signup", response_class=HTMLResponse)
def signup(request: Request):
    return templates.TemplateResponse("Registro.html",
                                      {"request": request,
                                       "title": "welcome"})


@app.post("/signup", response_class=RedirectResponse)
def signup_post(fullname: str = Form(...), code: str = Form(...), gender: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if len(users.fetch({"email": email}).items) != 0 or len(users.fetch({"code": code}).items) != 0:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND,)
    else:
        users.put({'fullname': fullname, 'code': code, 'gender': gender,
                   'email': email, 'password': password, "points": 0, 'is_login': True})
        return RedirectResponse("/retos/" + code, status_code=status.HTTP_302_FOUND)


@app.post("/login", response_class=RedirectResponse)
def login_post(code: str = Form(...), password: str = Form(...)):
    if len(users.fetch({"code": code, "password": password}).items) != 0:
        user_data = users.get(users.fetch(
            {"code": code, "password": password}).items[0]['key'])
        users.update({"is_login": True}, user_data['key'])
        return RedirectResponse("/retos/" + code, status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse("/Login", status_code=status.HTTP_304_NOT_MODIFIED)


@app.post("/Logout", response_class=RedirectResponse)
def logout_post():
    user_id = users.get(users.fetch({'is_login': True}).items[0]['key'])
    users.update({'is_login': False}, user_id['key'])
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@app.get("/retos/{code:path}", response_class=HTMLResponse)
def retos(request: Request, code: str):
    if len(users.fetch({"code": code, "is_login": True}).items) != 0:
        user_data = users.get(users.fetch(
            {"code": code, "is_login": True}).items[0]['key'])
        return templates.TemplateResponse("retos.html",
                                          {"request": request,
                                           "code": user_data['code'],
                                           "fullname": user_data['fullname']})
    else:
        return templates.TemplateResponse("index.html",
                                          {"request": request})


@app.get("/perfil/{code:path}", response_class=HTMLResponse)
def perfil(request: Request, code: str):
    if len(users.fetch({"code": code, "is_login": True}).items) != 0:
        user_data = users.get(users.fetch(
            {"code": code, "is_login": True}).items[0]['key'])
        return templates.TemplateResponse("Perfil.html",
                                          {"request": request,
                                           "fullname": user_data['fullname'],
                                           "code": user_data['code'],
                                           "email": user_data['email']})
    else:
        return templates.TemplateResponse("index.html",
                                          {"request": request})


@app.get("/puntos/{code:path}", response_class=HTMLResponse)
def puntos(request: Request, code: str):
    if len(users.fetch({"code": code, "is_login": True}).items) != 0:
        user_data = users.get(users.fetch(
            {"code": code, "is_login": True}).items[0]['key'])
        return templates.TemplateResponse("Puntos.html",
                                          {"request": request,
                                           "fullname": user_data['fullname'],
                                           "code": user_data['code'],
                                           "points": user_data['points']})
    else:
        return templates.TemplateResponse("index.html",
                                          {"request": request})


@app.get("/about-us", response_class=HTMLResponse)
def about_us(request: Request):
    return templates.TemplateResponse("Aboutus.html",
                                      {"request": request,
                                       "title": "welcome"})


@app.get("/marciano", response_class=HTMLResponse)
def marciano(request: Request):
    return templates.TemplateResponse("Marciano.html",
                                      {"request": request,
                                       "title": "welcome"})
