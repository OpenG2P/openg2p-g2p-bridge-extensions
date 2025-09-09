from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column


class G2PWarehouse(BaseORMModel):
    __tablename__ = "g2p_warehouse"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=True)
    warehouse_mnemonic = mapped_column(String, nullable=True)
    admin_name = mapped_column(String, nullable=True)
    admin_email = mapped_column(String, nullable=True)
    admin_mobile = mapped_column(String, nullable=True)


class G2PWarehouseProgramBenefitCode(BaseORMModel):
    __tablename__ = "g2p_warehouse_program_benefit_codes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = mapped_column(Integer, nullable=False)
    program_id = mapped_column(Integer, nullable=False)
    benefit_code_id = mapped_column(Integer, nullable=False)
    warehouse_mnemonic = mapped_column(String, nullable=True)
    warehouse_name = mapped_column(String, nullable=True)
    program_mnemonic = mapped_column(String, nullable=True)
    program_description = mapped_column(String, nullable=True)
    target_registry = mapped_column(String, nullable=True)
    program_status = mapped_column(String, nullable=True)
    benefit_mnemonic = mapped_column(String, nullable=True)
    benefit_type = mapped_column(String, nullable=True)
    measurement_unit = mapped_column(String, nullable=True)
    additional_info = mapped_column(String, nullable=True)  # text field
    benefit_description = mapped_column(String, nullable=True)


class G2PAdministrativeAreaLargeWarehouseRel(BaseORMModel):
    __tablename__ = "g2p_administrative_area_large_g2p_warehouse_rel"

    g2p_warehouse_id = mapped_column(Integer, primary_key=True)
    g2p_administrative_area_large_id = mapped_column(Integer, primary_key=True)
