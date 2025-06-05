from utils.helpers import STATE, state_url
from pathlib import Path
import logging
import requests
import tqdm

# instantiating base logging
logger = logging.getLogger(__name__)


def download_osm_file(state: str = "virginia", html_url: str = state_url) -> None:
    """
    Downloads OSM file for given state from the specified URL
    Args:
        state (str): the target state for the OSM file download
        url (str): the base URL for OSM file downloads
    Returns None
    """

    try:
        logger.info(f"Fetching HTML page for {state} from {html_url}")
        # could change this later to iterate over more states/territories
        response = requests.get(html_url)
        response.raise_for_status()
        # extracting .osm.pbf file URL
        start_index = response.text.find(f'href="{state.lower()}-latest.osm.pbf"')
        if start_index == -1:
            logger.error(f"Download link for {state} not found in the HTML page.")
            return
        file_url = f"https://download.geofabrik.de/north-america/us/{state.lower()}-latest.osm.pbf"
        logger.info(f"Found .osm.pbf file at {file_url}")
        # defining the filename and 'data' directory for saving state data
        filename = Path(f"../data/{state.lower()}-latest.osm.pbf")
        filename.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        # creating the progress bar
        total_size = int(response.headers.get("content-length", 0))
        with (
            open(filename, "wb") as file,
            tqdm.tqdm(
                total=total_size, unit="B", unit_scale=True, desc=f"Downloading {STATE}"
            ) as bar,
        ):
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))
        logger.info(f"Download completed: {filename}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during downloading: {e}")

    return


if __name__ == "__main__":
    download_osm_file("virginia")
