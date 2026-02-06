"""
Try the Tiss API
"""

# import requests
from tiss_client import TissClient

def main():
    # Get the data science curriculum
    client = TissClient()
    # data science curriculum
    curriculum = client._get("/curriculum/public/curriculum.xhtml?dswid=4018&dsrid=567&key=67853")
    course = client._get("/course/105731-2026S")
    return course

if __name__ == "__main__":
    curriculum = main()