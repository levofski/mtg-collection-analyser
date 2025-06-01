"""
Service module for interacting with the Scryfall API.

This module handles all communication with the Scryfall API, including:
- Rate limiting to stay within API guidelines
- Error handling and retries
- Caching to reduce redundant API calls
- Methods to fetch card data by various identifiers
"""
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import os

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://api.scryfall.com"
USER_AGENT = "MTG-Collection-Analyser/1.0"
CACHE_DIR = "cache/scryfall"
CACHE_DURATION = timedelta(days=1)  # Cache data for 1 day
REQUEST_DELAY = 0.1  # 100ms delay between requests


class ScryfallService:
    """
    Service for interacting with the Scryfall API with rate limiting and caching.
    """

    def __init__(self, cache_dir: str = CACHE_DIR):
        """
        Initialize the Scryfall service.

        Args:
            cache_dir: Directory to store cached responses.
        """
        self.cache_dir = cache_dir
        self.last_request_time = 0

        # Create cache directory if it doesn't exist
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        # Set up the session for all requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        })

    def _rate_limit(self) -> None:
        """
        Implement rate limiting to avoid hitting Scryfall's rate limits.
        Ensures at least REQUEST_DELAY seconds between requests.
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)

        self.last_request_time = time.time()

    def _get_cache_path(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Generate a cache file path for a specific API call.

        Args:
            endpoint: The API endpoint.
            params: The query parameters.

        Returns:
            A string containing the path to the cache file.
        """
        # Create a unique filename based on the endpoint and params
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
        cache_key = f"{endpoint.replace('/', '_')}_{param_str}".replace(" ", "_")

        # Use a hash if the key is too long
        if len(cache_key) > 100:
            import hashlib
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()

        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def _check_cache(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if a cached response exists and is still valid.

        Args:
            endpoint: The API endpoint.
            params: The query parameters.

        Returns:
            The cached response if valid, None otherwise.
        """
        cache_path = self._get_cache_path(endpoint, params)

        if not os.path.exists(cache_path):
            return None

        # Check if cache is expired
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - file_modified_time > CACHE_DURATION:
            logger.debug(f"Cache expired for {endpoint}")
            return None

        # Load and return cached data
        try:
            with open(cache_path, 'r', encoding='utf-8') as cache_file:
                logger.debug(f"Using cached response for {endpoint}")
                return json.load(cache_file)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error reading cache for {endpoint}: {str(e)}")
            return None

    def _save_to_cache(self, endpoint: str, params: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Save response data to cache.

        Args:
            endpoint: The API endpoint.
            params: The query parameters.
            data: The data to cache.
        """
        cache_path = self._get_cache_path(endpoint, params)

        try:
            with open(cache_path, 'w', encoding='utf-8') as cache_file:
                json.dump(data, cache_file, ensure_ascii=False, indent=2)
            logger.debug(f"Cached response for {endpoint}")
        except IOError as e:
            logger.warning(f"Error saving cache for {endpoint}: {str(e)}")

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None,
                     use_cache: bool = True, max_retries: int = 3) -> Dict[str, Any]:
        """
        Make a request to the Scryfall API with rate limiting, caching, and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/cards/named")
            params: Query parameters
            use_cache: Whether to use cached responses
            max_retries: Maximum number of retry attempts

        Returns:
            The JSON response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails after all retries
        """
        if params is None:
            params = {}

        # Check cache before making request
        if use_cache and method.upper() == 'GET':
            cached_data = self._check_cache(endpoint, params)
            if cached_data is not None:
                return cached_data

        # Enforce rate limiting
        self._rate_limit()

        # Make the request with retries
        url = f"{BASE_URL}{endpoint}"
        retry_count = 0
        last_exception = None

        while retry_count < max_retries:
            try:
                response = self.session.request(method=method, url=url, params=params)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', '1'))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds.")
                    time.sleep(retry_after)
                    retry_count += 1
                    continue

                # Raise exception for other errors
                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                # Cache successful GET responses
                if use_cache and method.upper() == 'GET':
                    self._save_to_cache(endpoint, params, data)

                return data

            except requests.exceptions.RequestException as e:
                last_exception = e
                retry_count += 1

                # Only retry on server errors (5xx) or rate limiting
                if hasattr(e, 'response') and e.response is not None:
                    if 500 <= e.response.status_code < 600 or e.response.status_code == 429:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        logger.warning(f"Request failed: {str(e)}. Retrying in {wait_time}s. ({retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        continue

                # For client errors (4xx) or other errors, don't retry
                raise e

        # All retries failed
        if last_exception:
            logger.error(f"Request failed after {max_retries} retries: {str(last_exception)}")
            raise last_exception

        # This shouldn't happen, but just in case
        raise requests.exceptions.RequestException("Request failed for unknown reason")

    def get_card_by_name(self, card_name: str, set_code: Optional[str] = None, fuzzy: bool = False) -> Dict[str, Any]:
        """
        Fetch card data by name.

        Args:
            card_name: The name of the card to search for
            set_code: Optional set code to filter by
            fuzzy: Whether to use fuzzy matching

        Returns:
            Card data as a dictionary

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        params: Dict[str, Any] = {"set": set_code}

        if fuzzy:
            params["fuzzy"] = card_name
        else:
            params["exact"] = card_name

        try:
            return self._make_request("GET", "/cards/named", params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                if fuzzy:
                    logger.warning(f"No card found with fuzzy name: '{card_name}'")
                else:
                    # Try fuzzy match if exact match fails
                    logger.info(f"No exact match for '{card_name}', trying fuzzy match")
                    return self.get_card_by_name(card_name, set_code, True)
            raise e

    def get_card_by_set_and_number(self, set_code: str, collector_number: str) -> Dict[str, Any]:
        """
        Fetch card data by set code and collector number.

        Args:
            set_code: The set code (e.g., "inr")
            collector_number: The collector number (e.g., "139")

        Returns:
            Card data as a dictionary

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        endpoint = f"/cards/{set_code}/{collector_number}"
        return self._make_request("GET", endpoint)

    def search_cards(self, query: str, page: int = 1) -> Dict[str, Any]:
        """
        Search for cards using Scryfall's search syntax.

        Args:
            query: The search query
            page: Page number for paginated results

        Returns:
            Search results as a dictionary

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        params = {"q": query, "page": page}
        return self._make_request("GET", "/cards/search", params)

    def enrich_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a card with data from Scryfall based on its identifiers.

        This method tries to find the most precise match for a card:
        1. First by set code + collector number
        2. Then by exact name + set code
        3. Finally by name only

        Args:
            card: Card data dictionary with at least a name and optionally set and collector number

        Returns:
            Enriched card data

        Raises:
            ValueError: If the card doesn't have a name
            requests.exceptions.RequestException: If all API requests fail
        """
        if not card.get('Name'):
            raise ValueError("Card must have a name to be enriched")

        # Try by set code and collector number if available
        if card.get('Edition_Code') and card.get('Card_Number'):
            try:
                return self.get_card_by_set_and_number(
                    card['Edition_Code'].lower(),
                    card['Card_Number']
                )
            except requests.exceptions.RequestException:
                logger.info(f"Couldn't find card by set and number, trying by name+set")

        # Try by name and set if available
        if card.get('Edition_Code'):
            try:
                return self.get_card_by_name(
                    card['Name'],
                    card['Edition_Code'].lower()
                )
            except requests.exceptions.RequestException:
                logger.info(f"Couldn't find card by name+set, trying by name only")

        # Finally, try by name only
        return self.get_card_by_name(card['Name'])

# Create a singleton instance
scryfall = ScryfallService()
