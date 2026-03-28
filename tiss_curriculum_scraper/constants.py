from pathlib import Path

import pandas as pd

SECTION_NAMES = {
    "Pruefungsfach Data Science - Foundations": "Foundations",
    "Prüfungsfach Data Science - Foundations": "Foundations",
    "Modul FDS/FD - Fundamentals of Data Science - Foundations": "Foundations",
    "Modul MLS/FD - Machine Learning and Statistics - Foundations": "Foundations",
    "Modul BDHPC/FD - Big Data and High Performance Computing - Foundations": "Foundations",
    "Modul VAST/FD - Visual Analytics and Semantic Technologies - Foundations": "Foundations",
    "Pruefungsfach Domain-Specific Aspects of Data Science": "DSA",
    "Prüfungsfach Domain-Specific Aspects of Data Science": "DSA",
    "Modul DSA - Domain-Specific Aspects of Data Science": "DSA",
    "Modul FDS/CO - Fundamentals of Data Science - Core": "FDS/CO",
    "Modul FDS/EX - Fundamentals of Data Science - Extension": "FDS/EX",
    "Modul MLS/CO - Machine Learning and Statistics - Core": "MLS/CO",
    "Modul MLS/EX - Machine Learning and Statistics - Extension": "MLS/EX",
    "Modul BDHPC/CO - Big Data and High Performance Computing - Core": "BDHPC/CO",
    "Modul BDHPC/EX - Big Data and High Performance Computing - Extension": "BDHPC/EX",
    "Modul VAST/CO - Visual Analytics and Semantic Technologies - Core": "VAST/CO",
    "Modul VAST/EX - Visual Analytics and Semantic Technologies - Extension": "VAST/EX",
    "Pruefungsfach Freie Wahlfaecher und Transferable Skills": "Free Electives",
    "Prüfungsfach Freie Wahlfächer und Transferable Skills": "Free Electives",
    "Module Free Electives and Transferable Skills": "Free Electives",
}

THESIS_MODULE = pd.DataFrame(
    {
        "module": ["Thesis"] * 3,
        "title": [
            "Master Thesis",
            "Seminar for Master students in Data Science",
            "Defense of Master Thesis",
        ],
        "code": ["none", "180.772", "none"],
        "type": [None, "SE", None],
        "semester": ["W and S"] * 3,
        "credits": [27, 1.5, 1.5],
    }
)

DUPL_COLS = ["link", "code"]

DATA_SCIENCE_URL = (
    "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml"
    "?dswid=7871&dsrid=370&key=67853"
)
TSK_URL = (
    "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml"
    "?dswid=2955&dsrid=810&date=20241001&key=57214"
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_PATH = REPO_ROOT / "curriculum.tsv"
LOGS_PATH = REPO_ROOT / "logs.tsv"
