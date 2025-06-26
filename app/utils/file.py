# Example utility function for file operations
def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1] if '.' in filename else ''
