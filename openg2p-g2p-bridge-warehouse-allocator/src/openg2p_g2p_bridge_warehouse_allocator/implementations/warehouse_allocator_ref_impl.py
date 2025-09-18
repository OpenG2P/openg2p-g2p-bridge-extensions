import logging
import random
from typing import Dict, List

from sqlalchemy.orm import sessionmaker

from ..engine import get_engine
from ..interface import WarehouseAllocator
from ..models import (
    G2PAdministrativeAreaLargeWarehouseRel,
    G2PWarehouse,
    G2PWarehouseProgramBenefitCode,
)

_logger = logging.getLogger("warehouse_allocator_ref_impl")
_engine = get_engine()
session_maker = sessionmaker(bind=_engine.get("db_engine_pbms"), expire_on_commit=False)


class WarehouseAllocatorRefImpl(WarehouseAllocator):
    def allocate_warehouse(
        self,
        large_geo_list: List[Dict],
        benefit_code_id: str,
        program_id: str,
    ) -> List[Dict]:
        results = []
        with session_maker() as pbms_session:
            _logger.info(
                f"Allocating warehouses for benefit_code_id={benefit_code_id}, program_id={program_id}"
            )

            # 1. Get all warehouse_ids with program_id and benefit_code_id
            program_benefit_warehouse_ids = {
                row.warehouse_id
                for row in pbms_session.query(G2PWarehouseProgramBenefitCode)
                .filter(
                    G2PWarehouseProgramBenefitCode.program_id == program_id,
                    G2PWarehouseProgramBenefitCode.benefit_code_id == benefit_code_id,
                )
                .all()
            }

            for geo in large_geo_list:
                # 2. Get all warehouse_ids under geo["administrative_zone_id_large"]
                geo_warehouse_ids = {
                    row.g2p_warehouse_id
                    for row in pbms_session.query(G2PAdministrativeAreaLargeWarehouseRel)
                    .filter(
                        G2PAdministrativeAreaLargeWarehouseRel.g2p_administrative_area_large_id
                        == geo["administrative_zone_id_large"]
                    )
                    .all()
                }
                # 3. Intersect both sets
                warehouse_ids_intersection = list(program_benefit_warehouse_ids & geo_warehouse_ids)
                _logger.info(
                    f"Warehouse Intersections {warehouse_ids_intersection} for benefit_code_id={benefit_code_id} and large_geo_id={geo['administrative_zone_id_large']}"
                )
                g2p_warehouses_intersection = (
                    pbms_session.query(G2PWarehouse)
                    .filter(G2PWarehouse.id.in_(warehouse_ids_intersection))
                    .all()
                )
                g2p_warehouse = (
                    random.choice(g2p_warehouses_intersection) if g2p_warehouses_intersection else None
                )
                if g2p_warehouse:
                    results.append(
                        {
                            "batch_control_geo_id": geo["batch_control_geo_id"],
                            "administrative_zone_id_large": geo["administrative_zone_id_large"],
                            "administrative_zone_mnemonic_large": geo["administrative_zone_mnemonic_large"],
                            "benefit_code_id": benefit_code_id,
                            "program_id": program_id,
                            "warehouse_id": g2p_warehouse.id,
                            "warehouse_mnemonic": g2p_warehouse.warehouse_mnemonic,
                            "warehouse_name": g2p_warehouse.name,
                            "warehouse_admin_name": g2p_warehouse.admin_name,
                            "warehouse_admin_email": g2p_warehouse.admin_email,
                            "warehouse_admin_phone": g2p_warehouse.admin_mobile,
                            "warehouse_additional_attributes": None,
                        }
                    )
                else:
                    _logger.error(
                        f"No warehouse found for benefit_code_id={benefit_code_id}, program_id={program_id}, "
                        f"administrative_zone_id_large={geo['administrative_zone_id_large']}"
                    )
                    raise Exception(
                        f"No warehouse found for benefit_code_id={benefit_code_id}, "
                        f"program_id={program_id}, administrative_zone_id_large={geo['administrative_zone_id_large']}"
                    )
        return results
