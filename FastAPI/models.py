from database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True) 
    date = Column(String, nullable=False)
    is_income = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Transaction(id={self.id}, description='{self.description}', amount={self.amount}, date='{self.date}', is_income={self.is_income})>"