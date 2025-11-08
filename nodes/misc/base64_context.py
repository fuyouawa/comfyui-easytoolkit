from ...utils.format import file_suffix_to_mime_type

class Base64Context:
    """
    Encapsulates base64 data and associated filename information.
    This class is used to store and retrieve base64 data in persistent context.
    """
    def __init__(self, base64: str, filename: str):
        """
        Initialize Base64Context with base64 data and filename.
        
        Args:
            base64: The base64 encoded string
            filename: The filename including extension (e.g., "image.png")
        """
        self._base64 = base64
        self._filename = filename

    def get_base64(self) -> str:
        """Get the base64 encoded data"""
        return self._base64
    
    def get_filename(self) -> str:
        """Get the full filename"""
        return self._filename
    
    def get_basename(self) -> str:
        """Get the filename without extension"""
        return self._filename.split(".")[0]
    
    def get_suffix(self) -> str:
        """Get the file extension (suffix)"""
        return self._filename.split(".")[-1]
    
    def get_format(self) -> str:
        """Get the formatted file suffix"""
        return file_suffix_to_mime_type(self.get_suffix())