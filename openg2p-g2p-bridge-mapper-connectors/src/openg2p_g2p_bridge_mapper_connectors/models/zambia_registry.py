from datetime import datetime, date

from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import DateTime, Integer, String, Boolean, Date
from sqlalchemy.orm import mapped_column


class G2PRegistrantID(BaseORMModel):
    """Registrant ID table"""
    __tablename__ = "g2p_reg_id"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    partner_id = mapped_column(Integer, nullable=False, index=True)
    id_type = mapped_column(Integer, nullable=False)
    value = mapped_column(String(100), nullable=True)
    expiry_date = mapped_column(Date, nullable=True)


class G2PPhoneNumber(BaseORMModel):
    """Phone Number table"""
    __tablename__ = "g2p_phone_number"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    partner_id = mapped_column(Integer, nullable=False, index=True)
    phone_no = mapped_column(String, nullable=False)
    phone_sanitized = mapped_column(String, nullable=True)
    date_collected = mapped_column(Date, default=date.today)
    disabled = mapped_column(DateTime, nullable=True)
    disabled_by = mapped_column(Integer, nullable=True)
    country_id = mapped_column(Integer, nullable=True)


class ZambiaRegistry(BaseORMModel):
    """Main registrant table (res_partner) with Zambia-specific fields"""
    __tablename__ = "res_partner"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    is_registrant = mapped_column(Boolean, default=True)
    
    # Basic information
    email = mapped_column(String, nullable=True)
    create_date = mapped_column(DateTime, default=datetime.now())
    
    # Zambia-specific fields as mentioned
    family_name = mapped_column(String, nullable=True)
    given_name = mapped_column(String, nullable=True)
    addl_name = mapped_column(String, nullable=True)  # Additional Name
    birth_place = mapped_column(String, nullable=True)
    birthdate_not_exact = mapped_column(Boolean, default=False)  # Approximate Birthdate
    birthdate = mapped_column(Date, nullable=True)  # Date of Birth
    age = mapped_column(String(50), nullable=True)  # Computed age field
    gender = mapped_column(String, nullable=True)  # Gender selection
