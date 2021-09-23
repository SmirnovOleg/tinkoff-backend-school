import os
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import click


@dataclass(frozen=True)
class MyGrepMatch:
    path_to_file: Path
    line_num: int
    line_content: str

    def __repr__(self):
        return f'{self.path_to_file} line={self.line_num}: {self.line_content.strip()}'


def grep(path: Path, substring: str) -> Generator[MyGrepMatch, None, None]:
    for dirname, _, files in os.walk(path):
        for filename in files:
            path_to_file = Path(dirname, filename)
            with open(path_to_file, 'rb') as file:
                for i, line in enumerate(file):
                    try:
                        line = line.decode('utf-8')
                    except UnicodeDecodeError:
                        continue
                    if line.find(substring) != -1:
                        yield MyGrepMatch(path_to_file, i + 1, line)


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
@click.argument('substring', type=str)
def main(path: Path, substring: str):
    """Search for SUBSTRING recursively in the files and all subdirectories of PATH"""
    for match in grep(path, substring):
        print(match)
