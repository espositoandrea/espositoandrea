#!/usr/bin/env python3

import dataclasses
import urllib.parse


@dataclasses.dataclass
class Publication:
    title: str
    year: int
    doi: str
    repo: str = None

    @property
    def doi_badge(self):
        return f"https://img.shields.io/badge/DOI-{urllib.parse.quote_plus(self.doi).replace('_', '__').replace('-', '--')}-cfd8dc?labelColor=black&style=flat-square"

    def __str__(self):
        title = (
            f"**[{self.title} ({self.year})]({self.repo})**"
            if self.repo
            else f"**{self.title} ({self.year})**"
        )
        return f'<a href="https://doi.org/{self.doi}"><img src="{self.doi_badge}" align="right"></a>{title}'


publications = [
    Publication(
        title="Building Symbiotic Artificial Intelligence: Reviewing the AI Act for a Human-Centred, Principle-Based Framework",
        year=2025,
        doi="10.1007/s11023-025-09753-w",
    ),
    Publication(
        year=2025,
        title="Understanding User Mental Models in AI-driven Code Completion Tools: Insights from an Elicitation Study",
        doi="10.1016/j.ijhcs.2025.103648",
    ),
    Publication(
        year=2025,
        title="A Dataset of Interactions and Emotions for Website User Experience Evaluation",
        doi="10.1038/s41597-025-06079-1",
    ),
    Publication(
        year=2024,
        title="From Human-Centered to Symbiotic Artificial Intelligence: A Focus on Medical Applications",
        doi="10.1007/s11042-024-20414-5",
    ),
    Publication(
        year=2024,
        title="Bridging the Gap between GPDR and Software Development: The MATERIALIST Framework",
        doi="10.1007/s11042-024-19923-0",
    ),
    Publication(
        year=2024,
        title="A Human–AI Interaction Paradigm and Its Application to Rhinocytology",
        doi="10.1016/j.artmed.2024.102933",
    ),
    Publication(
        year=2024,
        title="The Fine Line between Automation and Augmentation in Website Usability Evaluation",
        doi="10.1038/s41598-024-59616-0",
    ),
    Publication(
        year=2024,
        title="Automated Detection of Alzheimer’s Disease: A Multi-Modal Approach with 3D MRI and Amyloid PET",
        doi="10.1038/s41598-024-56001-9",
    ),
]

articles = ["- " + str(s) + "\n" for s in publications]

with open("README.md", "r") as f:
    readme = f.readlines()

start, end = [
    i
    for i, s in enumerate(readme)
    if s
    in [
        "<!-- SCIENTIFIC-ARTICLES-LIST:START -->\n",
        "<!-- SCIENTIFIC-ARTICLES-LIST:END -->\n",
    ]
]

with open("README.md", "w") as f:
    f.writelines(readme[0 : start + 1] + articles + readme[end:])
