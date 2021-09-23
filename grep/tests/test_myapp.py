import re

from click.testing import CliRunner

from myapp.app import grep, main


def test_one_simple_file(file_system_for_grep):
    file = file_system_for_grep / 'one_simple_file' / 'file.txt'
    result = set(str(match) for match in grep(file.parent, 'snow'))
    assert result == {
        f'{file} line=1: let it snow',
        f'{file} line=2: let it snow',
        f'{file} line=3: let it snow',
    }


def test_two_simple_files(file_system_for_grep):
    file_1 = file_system_for_grep / 'two_simple_files' / 'file_1.py'
    file_2 = file_system_for_grep / 'two_simple_files' / 'file_2.txt'
    result = set(str(match) for match in grep(file_1.parent, 'world'))
    assert result == {
        f'{file_1} line=1: print("Hello, world!")',
        f'{file_2} line=1: world',
    }


def test_subdirectories(file_system_for_grep):
    current_dir = file_system_for_grep / 'test_subdirectories'
    file_1 = current_dir / 'subdir_1' / 'file_1.txt'
    file_2 = current_dir / 'subdir_2' / 'file_2.txt'
    result = set(str(match) for match in grep(current_dir, 'aba'))
    assert result == {
        f'{file_1} line=1: abacaba d aba cab',
        f'{file_2} line=1: abacaba',
        f'{file_2} line=2: abacaba',
    }


def test_bytes(file_system_for_grep):
    current_dir = file_system_for_grep / 'bytes'
    result = set(str(match) for match in grep(current_dir, 'something'))
    assert result == set()


def test_empty_file(file_system_for_grep):
    current_dir = file_system_for_grep / 'empty_file'
    result = set(str(match) for match in grep(current_dir, 'something'))
    assert result == set()


def test_non_existent_path(file_system_for_grep):
    runner = CliRunner()
    current_dir = file_system_for_grep / 'non_existent_path'
    response = runner.invoke(main, [str(current_dir), ''])
    assert response.exit_code == 2
    assert re.search(f"Directory '{current_dir}' does not exist.", response.stdout)
