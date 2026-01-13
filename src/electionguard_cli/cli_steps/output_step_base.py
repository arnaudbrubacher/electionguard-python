from typing import List, Any
import os

from electionguard import to_file
from electionguard.serialize import to_raw, construct_path
from electionguard.guardian import Guardian, GuardianRecord
from electionguard_tools.helpers.export import GUARDIAN_PREFIX
from electionguard_tools.helpers.key_encryption import encrypt_guardian_key

from .cli_step_base import CliStepBase
from ..cli_models import CliElectionInputsBase


class OutputStepBase(CliStepBase):
    """Responsible for common functionality across all CLI commands related to outputting results."""

    _COMPRESSION_FORMAT = "zip"

    def _export_private_keys(self, output_keys: str, guardians: List[Guardian]) -> None:
        if output_keys is None:
            return

        # Ensure output directory exists
        if not os.path.exists(output_keys):
            os.makedirs(output_keys)

        private_guardian_records = [
            guardian.export_private_data() for guardian in guardians
        ]
        file_path = output_keys
        for private_guardian_record in private_guardian_records:
            file_name = GUARDIAN_PREFIX + private_guardian_record.guardian_id
            
            # Serialize to JSON string
            json_str = to_raw(private_guardian_record)
            
            # Encrypt
            try:
                encrypted_bytes = encrypt_guardian_key(json_str.encode('utf-8'))
                
                full_path = construct_path(file_name, file_path)
                with open(full_path, "wb") as f:
                    f.write(encrypted_bytes)
                
                # Set restrictive permissions (owner read/write only)
                os.chmod(full_path, 0o600)
            except Exception as e:
                # If we can't print error using self.print_error (if not available), just raise
                # CliStepBase usually has print_error? No, let's check.
                # It inherits from CliStepBase.
                # Assuming standard logging or print
                print(f"Error encrypting guardian key: {e}")
                raise

        self.print_value("Guardian private keys (ENCRYPTED)", output_keys)
        self.print_warning(
            f"The files in {file_path} are encrypted secret keys and should be protected securely."
        )

    @staticmethod
    def _get_guardian_records(
        election_inputs: CliElectionInputsBase,
    ) -> List[GuardianRecord]:
        return [guardian.publish() for guardian in election_inputs.guardians]

    def _export_file(
        self,
        title: str,
        content: Any,
        file_dir: str,
        file_name: str,
    ) -> str:
        location = to_file(content, file_name, file_dir)
        self.print_value(title, location)
        return location
