from io import TextIOWrapper
import click
import traceback
from typing import Any

from .setup_election_builder_step import SetupElectionBuilderStep
from .output_setup_files_step import OutputSetupFilesStep
from ..cli_steps import KeyCeremonyStep
from .setup_input_retrieval_step import SetupInputRetrievalStep


class SetupElectionCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super(SetupElectionCommand, self).__init__(*args, **kwargs)
        self.setup_input_retrieval_step = SetupInputRetrievalStep()
        self.key_ceremony_step = KeyCeremonyStep()
        self.election_builder_step = SetupElectionBuilderStep()
        self.output_step = OutputSetupFilesStep()

    def invoke(self, ctx: click.Context) -> Any:
        guardian_count = ctx.params["guardian_count"]
        quorum = ctx.params["quorum"]
        manifest = ctx.params["manifest"]
        url = ctx.params["url"]
        package_dir = ctx.params["package_dir"]
        keys_dir = ctx.params["keys_dir"]

        try:
            print("[PYTHON_DEBUG] Starting SetupElectionCommand.invoke") # DEBUG
            inputs = self.setup_input_retrieval_step.get_inputs(
                guardian_count, quorum, manifest, url
            )
            print(f"[PYTHON_DEBUG] Retrieved inputs: {inputs}") # DEBUG

            # Print Guardian info (even if n=1)
            print(f"[PYTHON_DEBUG] Number of guardians: {inputs.guardian_count}") # DEBUG
            print(f"[PYTHON_DEBUG] Quorum: {inputs.quorum}") # DEBUG

            # Run the key ceremony step to get the joint key
            print("[PYTHON_DEBUG] Running key ceremony step...") # DEBUG
            joint_key = self.key_ceremony_step.run_key_ceremony(inputs.guardians)
            print(f"[PYTHON_DEBUG] Key ceremony result (joint key): {joint_key is not None}") # DEBUG

            # build election, passing the actual joint_key object
            print("[PYTHON_DEBUG] Building election...") # DEBUG
            build_results = self.election_builder_step.build_election_for_setup(
                inputs, joint_key # Pass the result, not the step object
            )
            print(f"[PYTHON_DEBUG] Election build results obtained: {build_results is not None}") # DEBUG

            if build_results is None:
                 print("[PYTHON_DEBUG] Election build failed!") # DEBUG
                 # Consider raising an exception or exiting with error code
                 return

            # output files
            print("[PYTHON_DEBUG] Writing output files...") # DEBUG
            self.output_step.output(
                inputs, build_results, package_dir, keys_dir # Pass directories from context
            )
            print("[PYTHON_DEBUG] Finished writing output files.") # DEBUG

        except Exception as e:
            print("[PYTHON_DEBUG] Exception occurred in SetupElectionCommand!") # DEBUG
            print(traceback.format_exc()) # Print full traceback
            # Re-raise or handle as appropriate, maybe exit with non-zero code
            raise e


@click.command("setup")
@click.option(
    "--guardian-count",
    prompt="Number of guardians",
    help="The number of guardians that will participate in the key ceremony and tally.",
    type=click.INT,
)
@click.option(
    "--quorum",
    prompt="Quorum",
    help="The minimum number of guardians required to show up to the tally.",
    type=click.INT,
)
@click.option(
    "--manifest",
    prompt="Manifest file",
    help="The location of an election manifest.",
    type=click.File(),
)
@click.option(
    "--url",
    help="An optional verification url for the election.",
    required=False,
    type=click.STRING,
    default=None,
    prompt=False,
)
@click.option(
    "--package-dir",
    prompt="Election Package Output Directory",
    help="The location of a directory into which will be placed the output files such as "
    + "context, constants, and guardian keys. Existing files will be overwritten.",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, resolve_path=True),
)
@click.option(
    "--keys-dir",
    prompt="Private guardian keys directory",
    help="The location of a directory into which will be placed the guardian's private keys "
    + "This folder should be protected. Existing files will be overwritten.",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, resolve_path=True),
)
def setup_election_command(
    guardian_count: int,
    quorum: int,
    manifest: TextIOWrapper,
    url: str,
    package_dir: str,
    keys_dir: str,
) -> None:
    """
    This command runs an automated key ceremony and produces the files
    necessary to encrypt ballots, decrypt an election, and produce an election record.
    """
    # Pass the command name during internal instantiation
    # Use the context provided by click itself, which contains the params
    SetupElectionCommand(name="setup").invoke(click.get_current_context())
