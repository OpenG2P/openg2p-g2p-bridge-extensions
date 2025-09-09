from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column


class G2PAgency(BaseORMModel):
    __tablename__ = "g2p_agency"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=True)
    agency_mnemonic = mapped_column(String, nullable=True)
    admin_name = mapped_column(String, nullable=True)
    admin_email = mapped_column(String, nullable=True)
    admin_mobile = mapped_column(String, nullable=True)


class G2PAgencyProgramBenefitCode(BaseORMModel):
    __tablename__ = "g2p_agency_program_benefit_codes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    agency_id = mapped_column(Integer, nullable=False)
    program_id = mapped_column(Integer, nullable=False)
    benefit_code_id = mapped_column(Integer, nullable=False)
    agency_mnemonic = mapped_column(String, nullable=True)
    agency_name = mapped_column(String, nullable=True)
    program_mnemonic = mapped_column(String, nullable=True)
    program_description = mapped_column(String, nullable=True)
    target_registry = mapped_column(String, nullable=True)
    program_status = mapped_column(String, nullable=True)
    benefit_mnemonic = mapped_column(String, nullable=True)
    benefit_type = mapped_column(String, nullable=True)
    measurement_unit = mapped_column(String, nullable=True)
    additional_info = mapped_column(String, nullable=True)  # text field
    benefit_description = mapped_column(String, nullable=True)


class G2PAdministrativeAreaSmallAgencyRel(BaseORMModel):
    __tablename__ = "g2p_administrative_area_small_g2p_agency_rel"

    g2p_agency_id = mapped_column(Integer, primary_key=True)
    g2p_administrative_area_small_id = mapped_column(Integer, primary_key=True)
