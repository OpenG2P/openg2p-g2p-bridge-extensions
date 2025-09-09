from typing import Dict, List

from openg2p_fastapi_common.service import BaseService


class AgencyAllocator(BaseService):
    def allocate_agency(
        self,
        small_geo_list: List[Dict],
        benefit_code: Dict,
        program: Dict,
    ) -> List[Dict]:
        """
        Accepts:
          - small_geo_list: List of dicts, each with batch_control_geo_id, administrative_zone_id_small, administrative_zone_mnemonic_small
          - benefit_code: Dict with id and mnemonic
          - program: Dict with id and mnemonic
        Returns a list of dicts with agency allocation info for each geo.
        """
        raise NotImplementedError()
