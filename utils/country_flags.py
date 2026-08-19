"""Utilitarios para bandeiras dos paises das corridas."""


FLAG_DIR = "Country Flags"

TRACK_COUNTRY_CODES = {
    "Australia": "au",
    "Azerbaijan": "az",
    "Austria": "at",
    "Bahrain": "bh",
    "Belgium": "be",
    "Brazil": "br",
    "Canada": "ca",
    "China": "cn",
    "Great Britain": "gb",
    "Hungary": "hu",
    "Italy": "it",
    "Japan": "jp",
    "Mexico": "mx",
    "Monaco": "mc",
    "Netherlands": "nl",
    "Qatar": "qa",
    "Saudi Arabia": "sa",
    "Singapore": "sg",
    "Spain": "es",
    "United Arab Emirates": "ae",
    "United States": "us",
    "Miami": "us",
    "Barcelona-Catalunya":"es"
}


def build_flag_path(track: str) -> str:
    """Retorna o caminho estatico da bandeira associada a uma corrida."""
    country_code = TRACK_COUNTRY_CODES.get(str(track).strip())

    if not country_code:
        return ""

    return f"{FLAG_DIR}/{country_code}.svg"
