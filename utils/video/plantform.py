
# Temporary directory handling
def get_temp_directory():
    """Get temporary directory for video processing."""
    import folder_paths
    return folder_paths.get_temp_directory()
    # import tempfile
    # return tempfile.gettempdir()
