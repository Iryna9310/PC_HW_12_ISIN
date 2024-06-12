from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models, schemas, database, crud, utils
from typing import List, Optional

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Contact API"}

@app.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = utils.get_current_user(db, token)
    return crud.create_contact(db=db, contact=contact, user_id=user.id)

@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, search: Optional[str] = None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = utils.get_current_user(db, token)
    return crud.get_contacts(db=db, skip=skip, limit=limit, search=search, user_id=user.id)

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = utils.get_current_user(db, token)
    contact = crud.get_contact(db=db, contact_id=contact_id, user_id=user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = utils.get_current_user(db, token)
    db_contact = crud.get_contact(db=db, contact_id=contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=user.id)

@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = utils.get_current_user(db, token)
    db_contact = crud.get_contact(db=db, contact_id=contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    crud.delete_contact(db=db, contact_id=contact_id, user_id=user.id)
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/birthday/", response_model=List[schemas.Contact])
def upcoming_birthdays(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Логіка для отримання контактів з днями народження у наступні 7 днів
    pass

@app.get("/contacts/search/", response_model=List[schemas.Contact])
def search_contacts(query: Optional[str] = None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Логіка для пошуку контактів за ім'ям, прізвищем або електронною поштою
    pass

@app.on_event("startup")
def on_startup():
    database.Base.metadata.create_all(bind=database.engine)




