from typing import Dict, List

from openg2p_fastapi_common.service import BaseService


class WarehouseAllocator(BaseService):
    def allocate_warehouse(
        self,
        large_geo_list: List[Dict],
        benefit_code_id: str,
        program_id: str,
    ) -> List[Dict]:
        """
        Accepts:
          - large_geo_list: List of dicts, each with batch_control_geo_id, large_geo_ID, large_geo_Mnemonic
          - benefit_code_id: str
          - program_id: str
        Returns a list of dicts with warehouse allocation info for each geo.
        """
        raise NotImplementedError()
