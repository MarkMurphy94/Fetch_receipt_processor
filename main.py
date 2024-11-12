from datetime import datetime, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, model_validator
from uuid import uuid4
from math import ceil

app = FastAPI()

class ReceiptItem(BaseModel):
    shortDescription: str
    price: float

class Receipt(BaseModel):
    retailer: str
    purchaseDate: datetime
    purchaseTime: time
    items: list[ReceiptItem]
    total: float

class ProcessedReceipt(Receipt):
    receipt_id: str
    
    @model_validator(mode='before')
    @classmethod
    def set_defaults(cls, data):
        data['receipt_id'] = data.get('receipt_id', str(uuid4()))
        return data

RECEIPTS: list[ProcessedReceipt] = []


@app.get("/")
def root():
    return "Welcome to Receipt Processor"

@app.get("/receipts")
def root():
    return RECEIPTS

@app.post("/receipts/process") 
def process_receipt(receipt: Receipt):
    processed_receipt = ProcessedReceipt(**receipt.model_dump())
    RECEIPTS.append(processed_receipt)
    return {'id': processed_receipt.receipt_id}

@app.get("/receipts/{receipt_id}/points")
def get_points(receipt_id: str):
    for r in RECEIPTS:
        if r.receipt_id == receipt_id:
            return {'points': calculate_points(r)}
    raise HTTPException(status_code=404, detail=f"Receipt with id {receipt_id} does not exist.") 

def calculate_points(data: ProcessedReceipt):
    points = 0
    alphanumeric = 'abcdefghijklmnopqrstuvwxyz1234567890'

    # One point for every alphanumeric character in the retailer name
    for char in data.retailer:
        if char.lower() in alphanumeric:
            points += 1

    # 50 points if the total is a round dollar amount with no cents
    points += 50 if data.total.is_integer() else 0

    # 25 points if the total is a multiple of 0.25.
    points += 25 if data.total % 0.25 == 0 else 0

    # 5 points for every two items on the receipt.
    for i in range(len(data.items)//2):
        points += 5

    # If the trimmed length of the item description is a multiple of 3, 
    # multiply the price by 0.2 and round up to the nearest integer. 
    # The result is the number of points earned.
    # Assuming "trimmed length" here means length minus space characters
    for item in data.items:
        if len(item.shortDescription.strip(' ')) % 3 == 0:
            new_price = ceil(item.price * 0.2)
            points += new_price
    
    # 6 points if the day in the purchase date is odd.
    points += 6 if data.purchaseDate.day % 2 != 0 else 0

    # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    points += 10 if time(14, 0, 0) < data.purchaseTime < time(16, 0, 0) else 0

    return points