IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'People')
BEGIN
    CREATE TABLE People (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        first_name NVARCHAR(100) NOT NULL,
        last_name  NVARCHAR(100) NOT NULL
    );
END
