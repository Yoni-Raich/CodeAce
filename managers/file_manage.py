def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {path}")
    except IOError as e:
        raise IOError(f"Error reading file at {path}: {str(e)}")
    
