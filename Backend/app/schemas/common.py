"""
Common Pydantic schemas for API responses.
"""
from typing import Generic, TypeVar, List, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    code: str | None = Field(None, description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Resource not found",
                "detail": "Shipment with tracking number ABC123 does not exist",
                "code": "SHIPMENT_NOT_FOUND"
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response schema."""
    
    message: str = Field(..., description="Success message")
    data: Any | None = Field(None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": "123e4567-e89b-12d3-a456-426614174000"}
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }


# Made with Bob