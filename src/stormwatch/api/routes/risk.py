from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from stormwatch.api.schemas.errors import ErrorResponse
from stormwatch.api.schemas.risk import RiskMapItem
from stormwatch.database.connection import create_database_engine
from stormwatch.repositories.risk_repository import RiskRepository

router = APIRouter(prefix="/risk", tags=["risk"])
repository = RiskRepository(create_database_engine())


@router.get(
    "/map",
    response_model=list[RiskMapItem],
    responses={
        404: {"model": ErrorResponse, "description": "Risk data not found"},
        503: {"model": ErrorResponse, "description": "Risk data store unavailable"},
    },
)
def get_risk_map(forecast_date: date) -> list[RiskMapItem]:
    try:
        rows = repository.get_risk_map(forecast_date)
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Risk data is temporarily unavailable.",
        ) from error
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk data matched the request.",
        )
    return [RiskMapItem(**row) for row in rows]
