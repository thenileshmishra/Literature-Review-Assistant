"""
teams
=====
Team classes wrapping AutoGen team configurations.
"""

from app.teams.base import BaseTeam
from app.teams.litrev_team import LitRevTeam

__all__ = ["BaseTeam", "LitRevTeam"]
