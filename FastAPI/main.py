from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated , List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionBase(BaseModel):
    description: str
    amount: float
    category: str
    date: str
    is_income: bool = False

class TransactionModel(TransactionBase):
    id: int

    class Config:
         from_attributes = True    
        

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()        
db_dependency = Annotated[Session, Depends(get_db)] # dependency injection for database session
models.Base.metadata.create_all(bind=engine)  # create database tables if they don't exist
       
@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db: db_dependency): # transaction: TransactionBase, db: db_dependency
    db_transaction = models.Transaction(**transaction.dict()) # convert TransactionBase to Transaction
    db.add(db_transaction) # add transaction to the session
    db.commit() # commit the transaction
    db.refresh(db_transaction) # refresh to get the id and other fields
    return db_transaction # return the created transaction
       
@app.get("/transactions/", response_model=List[TransactionModel])     
async def get_transactions(db: db_dependency, skip: int = 0, limit: int = 100): # db: db_dependency  
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all() # get all transactions 
    return transactions
@app.get("/transactions/{transaction_id}", response_model=TransactionModel)
async def get_transaction(transaction_id: int, db: db_dependency): # transaction_id: int
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first() # get transaction by id
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.delete("/transactions/{transaction_id}", response_model=TransactionModel)
async def delete_transaction(transaction_id: int, db: db_dependency): # transaction_id: int
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first() # get transaction by id
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction) # delete the transaction
    db.commit() # commit the transaction
    return transaction # return the deleted transaction

@app.put("/transactions/{transaction_id}", response_model=TransactionModel)
async def update_transaction(transaction_id: int, transaction: TransactionBase, db: db_dependency):
    # Find the existing transaction
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    
    # Check if transaction exists
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update the transaction fields
    db_transaction.description = transaction.description
    db_transaction.amount = transaction.amount
    db_transaction.category = transaction.category
    db_transaction.date = transaction.date
    db_transaction.is_income = transaction.is_income
    
    # Commit the changes
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction