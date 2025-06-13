"""API client for Provident Energy."""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

from .const import *

_LOGGER = logging.getLogger(__name__)


@dataclass
class Utility:
    id: str
    text: str
    title: str


@dataclass
class UtilityGroup:
    """Class to store utility group data."""
    id: str
    text: str
    utilities: List[Utility]


@dataclass
class Consumption:
    """Class to store daily consumption data."""

    utility: Utility
    utility_name: str
    units: str
    name: str
    site: str
    start_date: datetime
    end_date: datetime
    data: List[float]


class ProvidentEnergyAPI:
    """API client for Provident Energy."""

    def __init__(self, username: str, password: str):
        """Initialize the API client.

        Args:
            username: Provident Energy account username
            password: Provident Energy account password
        """
        self.username = username
        self.password = password
        self.authenticated = False

    def _init_session(self) -> bool:
        """Initialize the requests session."""

        try:
            self.session = requests.Session()
            response = self.session.get(
                f"{API_BASE_URL}",
                headers={"User-Agent": API_USER_AGENT}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            _LOGGER.error(f"Failed to initialize session: {e}")
            return False
        return True

    def login(self) -> bool:
        """Log in to the Provident Energy API.

        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            self._init_session()

            # Make a POST request to the login endpoint with the required payload
            response = self.session.post(
                f"{API_BASE_URL}{API_LOGIN_ENDPOINT}",
                json={
                    "username": self.username,
                    "password": self.password,
                    "rememberMe": False
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": API_USER_AGENT
                }
            )
            response.raise_for_status()

            # Check if we received the ASP.NET_SessionId cookie
            if "ASP.NET_SessionId" in self.session.cookies:
                self.authenticated = True
                _LOGGER.info("Successfully logged in to Provident Energy API")
                return True
            else:
                _LOGGER.error("No session cookie received from Provident Energy API")
                return False

        except requests.RequestException as e:
            _LOGGER.error(f"Failed to log in to Provident Energy API: {e}")
            return False

    def get_utility_groups(self) -> Optional[List[UtilityGroup]]:
        """Get the list of utility groups."""

        if not self._check_auth():
            _LOGGER.error("Failed to authenticate with Provident Energy API")
            return None

        try:

            response = self.session.get(
                f"{API_BASE_URL}{API_ROOT_NODES_ENDPOINT}",
                params={"depth": 2},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": API_USER_AGENT
                }
            )
            response.raise_for_status()

            data = response.json()
            if len(data) == 0:
                _LOGGER.error("No utility groups found")
                return None

            utility_groups: Dict[str, UtilityGroup] = {}
            for d in data:
                if d["parent"] == "#":
                    utility_groups[d["id"]] = UtilityGroup(
                        id=d["id"],
                        text=d["text"],
                        utilities=[]
                    )
                else:
                    utility_groups[d["parent"]].utilities.append(
                        Utility(id=d["id"], text=d["text"], title=d["a_attr"]["title"])
                    )

            return list(utility_groups.values())

        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            # If unauthorized, try to log in again
            if isinstance(e, requests.RequestException) and e.response and e.response.status_code == 401:
                _LOGGER.info("Session expired, logging in again")
                self.authenticated = False
                if self.login():
                    return self.get_utility_groups()

            _LOGGER.error(f"Failed to get utilities: {e}")
            return None

    def get_utility_consumption(self, utility: Utility) -> Optional[Consumption]:
        """Get energy consumption data for a specific utility.

        Args:
            utility: The utility type to get consumption data for

        Returns:
            Optional[Consumption]: Consumption data for the utility, or None if there was an error
        """

        if not self._check_auth():
            _LOGGER.error("Failed to authenticate with Provident Energy API")
            return None

        try:

            today = datetime.now()
            yesterday = today - timedelta(days=1)
            tomorrow = today + timedelta(days=1)

            # Make a GET request to the QuickGraphs endpoint
            # This will return 48 data points (24 for yesterday, 24 for today)
            response = self.session.get(
                f"{API_BASE_URL}{API_QUICKGRAPHS_ENDPOINT}",
                params={
                    "aggregateGroups": True,
                    "meterlist": utility.id,
                    "startDate": yesterday.strftime("%Y-%m-%d"),
                    "endDate": tomorrow.strftime("%Y-%m-%d")
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": API_USER_AGENT
                }
            )
            response.raise_for_status()

            # Parse the response
            data = response.json()
            if len(data) == 0:
                _LOGGER.error(f"No energy data found for {utility}")
                return None

            d = data[0]

            utility_name = self._get_utility_name_clean(d["utility"])
            units = self._get_units_for_utility(utility_name)

            # Create a Consumption object with the data
            consumption = Consumption(
                utility=utility,
                utility_name=utility_name,
                units=units,
                name=d["name"],
                site=d["site"],
                start_date=yesterday,
                end_date=tomorrow,
                data=d["data"]
            )

            _LOGGER.debug(f"Retrieved energy data for {utility_name}: {consumption}")
            return consumption

        except (requests.RequestException, json.JSONDecodeError, KeyError, ValueError) as e:
            # If unauthorized, try to log in again
            if isinstance(e, requests.RequestException) and e.response and e.response.status_code == 401:
                _LOGGER.info("Session expired, logging in again")
                self.authenticated = False
                if self.login():
                    # Try again with this utility
                    return self.get_utility_consumption(utility)

            _LOGGER.error(f"Failed to get energy data for {utility}: {e}")
            return None

    def get_consumption_data(self) -> Dict[str, Consumption]:
        """Get energy data from the Provident Energy API.

        Returns:
            Dict[str, Consumption]: Energy consumption data for each utility
        """
        # If not authenticated, login first
        if not self.authenticated:
            if not self.login():
                _LOGGER.error("Failed to authenticate with Provident Energy API")
                return {}

        # Get the list of available utilities
        groups = self.get_utility_groups()
        if not groups:
            _LOGGER.error("Failed to get utilities")
            return {}

        # Dictionary to store consumption data for each utility
        consumption_data = {}

        # Fetch energy data for each utility
        for group in groups:
            for utility in group.utilities:
                consumption = self.get_utility_consumption(utility)
                if consumption:
                    consumption_data[utility.id] = consumption

        return consumption_data

    def _check_auth(self) -> bool:
        """Check if the API client is authenticated."""
        # If not authenticated, login first
        if not self.authenticated:
            return self.login()
        return True

    @staticmethod
    def _get_units_for_utility(utility: str) -> str:
        """Get the units for a specific utility."""
        if utility in UTILITY_UNITS:
            return UTILITY_UNITS[utility]
        return ""

    @staticmethod
    def _get_utility_name_clean(in_name: str) -> str:
        """Get the utility name without the "Utility" part."""
        match = re.match(r"^(.*)\s\(.*\)$", in_name)
        if match:
            return match.group(1)
        return in_name
