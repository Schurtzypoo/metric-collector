from fastapi import APIRouter, Depends
import os, sqlite3
from dependencies import user_store

auth = APIRouter(
    dependencies=[Depends(user_store)],
    prefix="/auth",
    tags = ["Authentication"]
    )
