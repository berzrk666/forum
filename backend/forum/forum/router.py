import logging
from fastapi import APIRouter, Depends, HTTPException, status

log = logging.getLogger(__name__)

forum_router = APIRouter(prefix="/forums", tags=["forums"])
