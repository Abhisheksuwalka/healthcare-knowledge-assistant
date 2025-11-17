from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Any, Dict
from .base_tool import BaseTool, ToolSchema, ToolCategory

class GetCurrentDateTimeTool(BaseTool):
    """Get current date, time, and day of week"""
    
    def _setup_schema(self) -> None:
        self.schema = ToolSchema(
            name="get_current_datetime",
            display_name="Get Current DateTime",
            description="Get current date, time, day of week, and timestamp",
            category=ToolCategory.TIME,
            parameters={
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone (e.g., 'Asia/Kolkata', 'UTC', 'America/New_York')",
                    "default": "UTC"
                }
            },
            required_params=[],
            return_type="object",
            examples=[
                {
                    "input": {"timezone": "Asia/Kolkata"},
                    "output": {
                        "datetime": "2025-11-17T23:30:45.123456+05:30",
                        "date": "2025-11-17",
                        "time": "23:30:45",
                        "day_of_week": "Monday",
                        "timezone": "Asia/Kolkata",
                        "unix_timestamp": 1737086445
                    }
                }
            ]
        )
    
    async def execute(self, timezone: str = "UTC", **kwargs) -> Dict[str, Any]:
        try:
            self.validate_params(timezone=timezone)
            
            # Get timezone
            try:
                tz = ZoneInfo(timezone)
            except Exception:
                tz = timezone.utc
            
            # Get current time in timezone
            now = datetime.now(tz)
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                   "Friday", "Saturday", "Sunday"]
            day_name = days[now.weekday()]
            
            data = {
                "datetime": now.isoformat(),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "day_of_week": day_name,
                "timezone": timezone,
                "unix_timestamp": int(now.timestamp()),
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second
            }
            
            return self.format_result(success=True, data=data)
        
        except Exception as e:
            return self.format_result(
                success=False, 
                error=f"Error getting datetime: {str(e)}"
            )

class CalculateAgeTool(BaseTool):
    """Calculate age from birthdate"""
    
    def _setup_schema(self) -> None:
        self.schema = ToolSchema(
            name="calculate_age",
            display_name="Calculate Age",
            description="Calculate patient age in years, months, days from birthdate",
            category=ToolCategory.MEDICAL,
            parameters={
                "birthdate": {
                    "type": "string",
                    "description": "Birth date in YYYY-MM-DD format"
                },
                "reference_date": {
                    "type": "string",
                    "description": "Reference date (default: today) in YYYY-MM-DD format"
                }
            },
            required_params=["birthdate"],
            return_type="object",
            examples=[
                {
                    "input": {"birthdate": "1990-05-15"},
                    "output": {
                        "age_years": 35,
                        "age_months": 6,
                        "age_days": 2,
                        "birthdate": "1990-05-15",
                        "is_birthday_today": False
                    }
                }
            ]
        )
    
    async def execute(self, birthdate: str, reference_date: str = None, **kwargs) -> Dict[str, Any]:
        try:
            self.validate_params(birthdate=birthdate)
            
            # Parse dates
            birth_dt = datetime.strptime(birthdate, "%Y-%m-%d").date()
            
            if reference_date:
                ref_dt = datetime.strptime(reference_date, "%Y-%m-%d").date()
            else:
                ref_dt = datetime.now().date()
            
            # Calculate age
            age_years = ref_dt.year - birth_dt.year
            age_months = ref_dt.month - birth_dt.month
            age_days = ref_dt.day - birth_dt.day
            
            # Adjust for incomplete months/years
            if age_days < 0:
                age_months -= 1
                age_days += 30
            
            if age_months < 0:
                age_years -= 1
                age_months += 12
            
            # Check if birthday today
            is_birthday = (ref_dt.month == birth_dt.month and 
                          ref_dt.day == birth_dt.day)
            
            data = {
                "age_years": age_years,
                "age_months": age_months,
                "age_days": age_days,
                "birthdate": birthdate,
                "reference_date": ref_dt.strftime("%Y-%m-%d"),
                "is_birthday_today": is_birthday,
                "total_days_lived": (ref_dt - birth_dt).days
            }
            
            return self.format_result(success=True, data=data)
        
        except ValueError as e:
            return self.format_result(
                success=False,
                error=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
            )
        except Exception as e:
            return self.format_result(
                success=False,
                error=f"Error calculating age: {str(e)}"
            )

class GetWorkingHoursTool(BaseTool):
    """Get hospital department working hours"""
    
    # Mock hospital schedule
    HOSPITAL_SCHEDULE = {
        "emergency": {
            "name": "Emergency Department",
            "hours": "24/7",
            "is_24_7": True,
            "note": "Always open"
        },
        "icu": {
            "name": "Intensive Care Unit",
            "hours": "24/7",
            "is_24_7": True,
            "note": "Always open"
        },
        "opd": {
            "name": "Out Patient Department",
            "monday_friday": "09:00 - 17:00",
            "saturday": "09:00 - 13:00",
            "sunday": "Closed",
            "is_24_7": False
        },
        "pharmacy": {
            "name": "Pharmacy",
            "monday_friday": "08:00 - 20:00",
            "saturday": "09:00 - 18:00",
            "sunday": "10:00 - 15:00",
            "is_24_7": False
        },
        "billing": {
            "name": "Billing Department",
            "monday_friday": "10:00 - 16:00",
            "saturday": "10:00 - 14:00",
            "sunday": "Closed",
            "is_24_7": False
        }
    }
    
    def _setup_schema(self) -> None:
        self.schema = ToolSchema(
            name="get_working_hours",
            display_name="Get Working Hours",
            description="Get working hours for hospital departments",
            category=ToolCategory.HOSPITAL,
            parameters={
                "department": {
                    "type": "string",
                    "description": "Department name (emergency, icu, opd, pharmacy, billing)"
                }
            },
            required_params=["department"],
            return_type="object",
            examples=[
                {
                    "input": {"department": "opd"},
                    "output": {
                        "department": "Out Patient Department",
                        "monday_friday": "09:00 - 17:00",
                        "saturday": "09:00 - 13:00",
                        "sunday": "Closed"
                    }
                }
            ]
        )
    
    async def execute(self, department: str, **kwargs) -> Dict[str, Any]:
        try:
            self.validate_params(department=department)
            
            dept_lower = department.lower().strip()
            
            if dept_lower not in self.HOSPITAL_SCHEDULE:
                available = list(self.HOSPITAL_SCHEDULE.keys())
                return self.format_result(
                    success=False,
                    error=f"Department not found. Available: {', '.join(available)}"
                )
            
            data = self.HOSPITAL_SCHEDULE[dept_lower]
            
            return self.format_result(success=True, data=data)
        
        except Exception as e:
            return self.format_result(
                success=False,
                error=f"Error fetching working hours: {str(e)}"
            )
