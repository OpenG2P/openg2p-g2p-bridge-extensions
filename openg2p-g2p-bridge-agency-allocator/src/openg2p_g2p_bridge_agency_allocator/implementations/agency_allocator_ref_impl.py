import logging
import random
from typing import Dict, List

from sqlalchemy.orm import sessionmaker

from ..engine import get_engine
from ..interface import AgencyAllocator
from ..models import (
    G2PAdministrativeAreaSmallAgencyRel,
    G2PAgency,
    G2PAgencyProgramBenefitCode,
)

_logger = logging.getLogger("agency_allocator_ref_impl")
_engine = get_engine()

session_maker = sessionmaker(bind=_engine.get("db_engine_pbms"), expire_on_commit=False)


class AgencyAllocatorRefImpl(AgencyAllocator):
    def allocate_agency(
        self,
        small_geo_list: List[Dict],
        benefit_code_id: str,
        program_id: str,
    ) -> List[Dict]:
        results = []
        with session_maker() as pbms_session:
            # 1. Get agency_ids with program_id and benefit_code_id
            program_benefit_agency_ids = {
                row.agency_id
                for row in pbms_session.query(G2PAgencyProgramBenefitCode)
                .filter(
                    G2PAgencyProgramBenefitCode.program_id == program_id,
                    G2PAgencyProgramBenefitCode.benefit_code_id == benefit_code_id,
                )
                .all()
            }
            # Fetch G2P agencies based on the small geo list

            for geo in small_geo_list:
                # 2. Get agency_ids under geo["administrative_zone_id_small"]
                geo_agency_ids = {
                    row.g2p_agency_id
                    for row in pbms_session.query(G2PAdministrativeAreaSmallAgencyRel)
                    .filter(
                        G2PAdministrativeAreaSmallAgencyRel.g2p_administrative_area_small_id
                        == geo["administrative_zone_id_small"]
                    )
                    .all()
                }
                # 3. Intersect both sets
                agency_ids_intersected = list(program_benefit_agency_ids & geo_agency_ids)
                g2p_agencies = (
                    pbms_session.query(G2PAgency).filter(G2PAgency.id.in_(agency_ids_intersected)).all()
                )
                g2p_agency = random.choice(g2p_agencies) if g2p_agencies else None
                agency_additional_attributes = None
                if g2p_agency:
                    # Try to get the additional_info from G2PAgencyProgramBenefitCode for this agency
                    benefit_code_entry = (
                        pbms_session.query(G2PAgencyProgramBenefitCode)
                        .filter(
                            G2PAgencyProgramBenefitCode.agency_id == g2p_agency.id,
                            G2PAgencyProgramBenefitCode.program_id == program_id,
                            G2PAgencyProgramBenefitCode.benefit_code_id == benefit_code_id,
                        )
                        .first()
                    )
                    agency_additional_attributes = (
                        benefit_code_entry.additional_info if benefit_code_entry else None
                    )
                    results.append(
                        {
                            "batch_control_geo_id": geo["batch_control_geo_id"],
                            "administrative_zone_id_small": geo["administrative_zone_id_small"],
                            "administrative_zone_mnemonic_small": geo["administrative_zone_mnemonic_small"],
                            "benefit_code_id": benefit_code_id,
                            "program_id": program_id,
                            "agency_id": g2p_agency.id,
                            "agency_mnemonic": g2p_agency.agency_mnemonic,
                            "agency_name": g2p_agency.name,
                            "agency_admin_name": g2p_agency.admin_name,
                            "agency_admin_email": g2p_agency.admin_email,
                            "agency_admin_phone": g2p_agency.admin_mobile,
                            "agency_additional_attributes": agency_additional_attributes,
                        }
                    )
                else:
                    _logger.warning(
                        f"No agency found for geo {geo['administrative_zone_id_small']} with benefit_code_id={benefit_code_id} and program_id={program_id}"
                    )
                    raise Exception(
                        f"No agency found for geo {geo['administrative_zone_id_small']} with benefit_code_id={benefit_code_id} and program_id={program_id}"
                    )
        return results
