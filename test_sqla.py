from db.models import Book
sort_by = "owner"
sort_column = getattr(Book, sort_by, Book.id)
print(type(sort_column))
try:
    print(sort_column.property.columns[0].type.python_type is str)
except Exception as e:
    print("Error:", e)

sort_by = "id"
sort_column = getattr(Book, sort_by, Book.id)
print(type(sort_column))
try:
    print(sort_column.property.columns[0].type.python_type is str)
except Exception as e:
    print("Error:", e)
