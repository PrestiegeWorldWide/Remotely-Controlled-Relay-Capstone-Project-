CREATE TABLE borgMemory (
    RowID INT PRIMARY KEY AUTO_INCREMENT,
    DeviceID NVARCHAR(MAX) NOTNULL,
    RecordTime DATETIME NOTNULL,
    RelayUpdated NVARCHAR(MAX) NOTNULL,
    StateChangedTo BIT NOTNULL,
    Connection_Description NVARCHAR(MAX) NOTNULL
);

