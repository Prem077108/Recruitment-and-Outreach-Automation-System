from __future__ import annotations

from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent

CANDIDATE_ROLES = {
    "Java Developer": {
        "primary_role": "Java Developer",
        "search_roles": ["Java Developer", "Java Engineer", "Backend Developer"],
        "exclusion_keywords": ["hotlist", "fulltime", "available consultants", "bench"],
    },
    "Data Scientist": {
        "primary_role": "Data Scientist",
        "search_roles": ["Data Scientist", "ML Engineer", "AI Engineer"],
        "exclusion_keywords": ["hotlist", "fulltime", "bench marketer", "qa"],
    },
    "Frontend Engineer": {
        "primary_role": "Frontend Engineer",
        "search_roles": ["Frontend Engineer", "React Developer", "UI Developer"],
        "exclusion_keywords": ["hotlist", "bench", "fulltime"],
    },
}

CLIENTS = {
    "demo": {
        "name": "Demo Candidate",
        "email": "demo.candidate@example.com",
        "phone": "555-010-1234",
        "linkedin": "https://www.linkedin.com/in/demo-candidate",
        "location": "Dallas, TX",
        "relocation": "Yes",
        "work_auth": "H1B",
        "availability": "Immediate",
        "experience": "5+ Years",
        "resume_candidates": [
            str(BASE_DIR / "clients" / "demo_resume.docx"),
            str(BASE_DIR / "clients" / "demo_resume.pdf"),
        ],
        "role_map": {
            "Java Developer": {
                "primary_role": "Java Developer",
                "search_roles": ["Java Developer", "Java Engineer"],
                "exclusion_keywords": ["hotlist", "fulltime", "available consultants"],
            }
        },
    },
    "safi": {
        "name": "Safi Khan",
        "email": "safi.khan@example.com",
        "phone": "555-010-0001",
        "linkedin": "https://www.linkedin.com/in/safikhan",
        "location": "Austin, TX",
        "relocation": "Yes",
        "work_auth": "OPT",
        "availability": "Immediate",
        "experience": "6+ Years",
        "resume_candidates": [
            str(BASE_DIR / "clients" / "safi_resume.docx"),
        ],
        "role_map": {
            "Java Developer": {
                "primary_role": "Java Developer",
                "search_roles": ["Java Developer", "Backend Developer", "Spring Boot Developer"],
                "exclusion_keywords": ["hotlist", "fulltime", "bench marketer"],
            }
        },
    },
    "tanuja": {
        "name": "Tanuja Verma",
        "email": "tanuja.verma@example.com",
        "phone": "555-010-0002",
        "linkedin": "https://www.linkedin.com/in/tanujaverma",
        "location": "New York, NY",
        "relocation": "No",
        "work_auth": "US Citizen",
        "availability": "Immediate",
        "experience": "8+ Years",
        "resume_candidates": [
            str(BASE_DIR / "clients" / "tanuja_resume.docx"),
        ],
        "role_map": {
            "Data Scientist": {
                "primary_role": "Data Scientist",
                "search_roles": ["Data Scientist", "Machine Learning Engineer", "AI Engineer"],
                "exclusion_keywords": ["hotlist", "fulltime", "qa"],
            }
        },
    },
}


def get_candidate(candidate_key: str | None = None) -> dict[str, Any]:
    key = candidate_key or "demo"
    return CLIENTS.get(key, CLIENTS["demo"])


def get_target_roles(candidate_key: str | None = None) -> list[str]:
    candidate = get_candidate(candidate_key)
    role_map = candidate.get("role_map", {})
    return list(role_map.keys()) or list(CANDIDATE_ROLES.keys())


def ensure_candidate_resume(candidate: dict[str, Any]) -> str | None:
    resume_paths = candidate.get("resume_candidates", [])
    for resume_path in resume_paths:
        if Path(resume_path).exists():
            return str(Path(resume_path))
    return None
