from typing import Optional


class FastAPIJinja2Exception(Exception):
    pass


class FastAPIJinja2NotFoundException(FastAPIJinja2Exception):
    def __init__(self, message: Optional[str] = None, four04template_file: str = 'errors/404.pt'):
        super().__init__(message)

        self.template_file: str = four04template_file
        self.message: Optional[str] = message