from fastapi.templating import Jinja2Templates

from utils.validators import format_isbn

templates = Jinja2Templates(directory="templates")
templates.env.filters["format_isbn"] = format_isbn
