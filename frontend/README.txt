Converted static frontend.
Expectations:
- Backend should expose:
  GET /api/books -> array of {id,title,author}
  GET /api/users -> array of {id,name,email}
  POST /api/users with JSON {name,email} -> create user
  DELETE /api/users/{id} -> delete
  GET /api/search?q=... -> array of results {title,author}
If your backend uses different paths, update the fetch() URLs in the HTML files.
