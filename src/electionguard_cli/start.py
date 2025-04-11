import click

# Import the decorated command functions *directly* from their specific files
from .setup_election.setup_election_command import setup_election_command
from .e2e.e2e_command import E2eCommand
from .import_ballots.import_ballots_command import ImportBallotsCommand
from .encrypt_ballots.encrypt_command import EncryptBallotsCommand
from .mark_ballots.mark_command import MarkBallotsCommand
from .submit_ballots.submit_command import SubmitBallotsCommand


@click.group()
def cli() -> None:
    pass


# Add the command functions directly
cli.add_command(setup_election_command)
cli.add_command(E2eCommand)
cli.add_command(ImportBallotsCommand)
cli.add_command(EncryptBallotsCommand)
cli.add_command(SubmitBallotsCommand)
cli.add_command(MarkBallotsCommand)

if __name__ == "__main__":
    cli()
