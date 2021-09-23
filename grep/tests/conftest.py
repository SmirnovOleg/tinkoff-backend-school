import pytest


@pytest.fixture()
def file_system_for_grep(tmp_path):
    """Prepare temporary file system for testing `mygrep` util."""
    current_dir = tmp_path / 'one_simple_file'
    current_dir.mkdir()
    file = current_dir / 'file.txt'
    with file.open('a') as f:
        f.write('let it snow\n')
        f.write('let it snow\n')
        f.write('let it snow\n')
        f.write('to be or not to be')

    current_dir = tmp_path / 'two_simple_files'
    current_dir.mkdir()
    (current_dir / 'file_1.py').write_text('print("Hello, world!")')
    (current_dir / 'file_2.txt').write_text('world\nhello')

    current_dir = tmp_path / 'test_subdirectories'
    current_dir.mkdir()
    subdir_1 = current_dir / 'subdir_1'
    subdir_1.mkdir()
    subdir_2 = current_dir / 'subdir_2'
    subdir_2.mkdir()
    (subdir_1 / 'file_1.txt').write_text('abacaba d aba cab')
    (subdir_2 / 'file_2.txt').write_text('abacaba\n' 'abacaba')

    current_dir = tmp_path / 'bytes'
    current_dir.mkdir()
    file = current_dir / 'file.txt'
    with file.open('wb') as f:
        f.write(bytes(int(i, 16) for i in ['0x00', '0x93', '0x0b', '0xa7', '0x96']))

    current_dir = tmp_path / 'empty_file'
    current_dir.mkdir()
    (current_dir / 'file.txt').write_text('')

    return tmp_path
