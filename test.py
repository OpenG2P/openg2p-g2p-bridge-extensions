#!/usr/bin/env python3
import logging
import re
import enum
from typing import List, Optional
from pydantic import BaseModel

# Logging setup
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("fa_test")


class MapperResolvedFaType(enum.Enum):
    BANK_ACCOUNT = "BANK_ACCOUNT"
    MOBILE_WALLET = "MOBILE_WALLET"
    EMAIL_WALLET = "EMAIL_WALLET"


class FAKeys(enum.Enum):
    account_number = "account_number"
    bank_code = "bank_code"
    branch_code = "branch_code"
    account_type = "account_type"
    mobile_number = "mobile_number"
    mobile_wallet_provider = "mobile_wallet_provider"
    email_address = "email_address"
    email_wallet_provider = "email_wallet_provider"
    fa_type = "fa_type"


class KeyValuePair(BaseModel):
    key: FAKeys
    value: str


class _Config:
    # Updated strategy with optional branch_code and email_address; non-greedy dot-safe groups
    bank_fa_deconstruct_strategy: str = (
        r"^account_number:(?P<account_number>[^.]*)\." \
        r"(?:branch_code:(?P<branch_code>[^.]*)\.)?" \
        r"bank_code:(?P<bank_code>[^.]*)\." \
        r"mobile_number:(?P<mobile_number>[^.]*)\." \
        r"(?:email_address:(?P<email_address>[^.]*)\.)?" \
        r"fa_type:(?P<fa_type>[^.]*)$"
    )
    mobile_wallet_fa_deconstruct_strategy: str = ""
    email_wallet_fa_deconstruct_strategy: str = ""


_config = _Config()


class Deconstructor:
    def _deconstruct(self, value: str, strategy: str) -> List[KeyValuePair]:
        _logger.info(f"Deconstructing ID/FA: {value}")
        regex_res = re.match(strategy, value)
        deconstructed_list: List[KeyValuePair] = []
        if regex_res:
            regex_res = regex_res.groupdict()
            try:
                # Coalesce None (from optional groups) to empty strings
                deconstructed_list = [
                    KeyValuePair(key=FAKeys(k), value=(v if v is not None else ""))
                    for k, v in regex_res.items()
                ]
            except Exception as e:
                _logger.error(f"Error while deconstructing ID/FA: {e}")
                raise ValueError("Error while deconstructing ID/FA") from e
        else:
            _logger.info("Regex did not match the FA string with the strategy provided.")
        _logger.info(f"Deconstructed ID/FA: {value}")
        return deconstructed_list

    def _get_deconstruct_strategy(self, fa: str) -> str:
        _logger.info("Getting deconstruction strategy")
        if fa.endswith(MapperResolvedFaType.BANK_ACCOUNT.value):
            return _config.bank_fa_deconstruct_strategy
        elif fa.endswith(MapperResolvedFaType.MOBILE_WALLET.value):
            return _config.mobile_wallet_fa_deconstruct_strategy
        elif fa.endswith(MapperResolvedFaType.EMAIL_WALLET.value):
            return _config.email_wallet_fa_deconstruct_strategy
        _logger.info("Deconstruction strategy not found!")
        return ""

    def deconstruct_fa(self, fa: str) -> dict:
        _logger.info("Deconstructing FA")
        deconstruct_strategy = self._get_deconstruct_strategy(fa)
        _logger.info(f"Deconstruction strategy: {deconstruct_strategy}")
        if deconstruct_strategy:
            deconstructed_pairs = self._deconstruct(fa, deconstruct_strategy)
            deconstructed_fa = {pair.key.value: pair.value for pair in deconstructed_pairs}
            _logger.info(f"Deconstructed FA Returning: {deconstructed_fa}")
            return deconstructed_fa
        return {}


def main() -> None:
    # FA string provided by the user
    fa = "account_number:97.bank_code:123456/78/2.mobile_number:+260971234567.fa_type:BANK_ACCOUNT"

    print("TEST: Using optional-branch/email regex strategy")
    print(f"FA: {fa}")

    dec = Deconstructor()
    result = dec.deconstruct_fa(fa)

    print("\nResult dictionary:")
    print(result)

    # Convenience prints
    print("\nExtracted:")
    for k in ["account_number", "branch_code", "bank_code", "mobile_number", "email_address", "fa_type"]:
        print(f"  {k}: {result.get(k)}")


if __name__ == "__main__":
    main()
