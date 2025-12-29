



Criando o database postegresql no wsl  
```
    CREATE DATABASE studio_fun;

     CREATE USER natan33 WITH PASSWORD '$2y$10$mljyKGVEErZsv.bIjpZ6puaTbcAgmvaUe7GMMPr3j2/0Ytu7o0N4G';

    GRANT ALL PRIVILEGES ON DATABASE studio_fun TO natan33;

    \q
```

# No core/config.py
SQLALCHEMY_DATABASE_URI = "postgresql://natan33:$2y$10$mljyKGVEErZsv.bIjpZ6puaTbcAgmvaUe7GMMPr3j2/0Ytu7o0N4G@localhost:5432/studio_fun"