-- SQL Server schema for banking document validation
-- Tables, indexes, stored procedures, and error handling

SET NOCOUNT ON;

IF OBJECT_ID('dbo.DocumentHistory', 'U') IS NOT NULL DROP TABLE dbo.DocumentHistory;
IF OBJECT_ID('dbo.DocumentComment', 'U') IS NOT NULL DROP TABLE dbo.DocumentComment;
IF OBJECT_ID('dbo.Document', 'U') IS NOT NULL DROP TABLE dbo.Document;
IF OBJECT_ID('dbo.Profile', 'U') IS NOT NULL DROP TABLE dbo.Profile;
IF OBJECT_ID('dbo.[User]', 'U') IS NOT NULL DROP TABLE dbo.[User];

CREATE TABLE dbo.[User] (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(150) NOT NULL UNIQUE,
    Email NVARCHAR(254) NOT NULL,
    PasswordHash NVARCHAR(128) NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Profile (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL UNIQUE,
    IsWorker BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_Profile_User FOREIGN KEY (UserId) REFERENCES dbo.[User](Id)
);

CREATE TABLE dbo.Document (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    Title NVARCHAR(200) NOT NULL,
    FilePath NVARCHAR(500) NOT NULL,
    UploadedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    Status NVARCHAR(20) NOT NULL DEFAULT 'pending',
    AssignedToId INT NULL,
    UpdatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Document_User FOREIGN KEY (UserId) REFERENCES dbo.[User](Id),
    CONSTRAINT FK_Document_AssignedTo FOREIGN KEY (AssignedToId) REFERENCES dbo.[User](Id)
);

CREATE TABLE dbo.DocumentComment (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    DocumentId INT NOT NULL,
    AuthorId INT NULL,
    Comment NVARCHAR(MAX) NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_DocumentComment_Document FOREIGN KEY (DocumentId) REFERENCES dbo.Document(Id),
    CONSTRAINT FK_DocumentComment_Author FOREIGN KEY (AuthorId) REFERENCES dbo.[User](Id)
);

CREATE TABLE dbo.DocumentHistory (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    DocumentId INT NOT NULL,
    Status NVARCHAR(20) NOT NULL,
    Note NVARCHAR(MAX) NULL,
    AuthorId INT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_DocumentHistory_Document FOREIGN KEY (DocumentId) REFERENCES dbo.Document(Id),
    CONSTRAINT FK_DocumentHistory_Author FOREIGN KEY (AuthorId) REFERENCES dbo.[User](Id)
);

CREATE TABLE dbo.AuditLog (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    TableName NVARCHAR(100) NOT NULL,
    RowPk INT NOT NULL,
    Action NVARCHAR(20) NOT NULL,
    ChangedBy INT NULL,
    OldStatus NVARCHAR(50) NULL,
    NewStatus NVARCHAR(50) NULL,
    Note NVARCHAR(MAX) NULL,
    ChangedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_AuditLog_Author FOREIGN KEY (ChangedBy) REFERENCES dbo.[User](Id)
);

CREATE INDEX IX_Document_UserId ON dbo.Document(UserId);
CREATE INDEX IX_Document_Status ON dbo.Document(Status);
CREATE INDEX IX_Document_AssignedToId ON dbo.Document(AssignedToId);
CREATE INDEX IX_Document_UploadedAt ON dbo.Document(UploadedAt);
CREATE INDEX IX_DocumentComment_DocumentId ON dbo.DocumentComment(DocumentId);
CREATE INDEX IX_DocumentHistory_DocumentId ON dbo.DocumentHistory(DocumentId);
CREATE INDEX IX_AuditLog_TableName ON dbo.AuditLog(TableName);
CREATE INDEX IX_AuditLog_RowPk ON dbo.AuditLog(RowPk);
CREATE INDEX IX_AuditLog_ChangedAt ON dbo.AuditLog(ChangedAt);

GO

IF OBJECT_ID('dbo.trg_Document_InsertAudit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_Document_InsertAudit;
CREATE TRIGGER dbo.trg_Document_InsertAudit
ON dbo.Document
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.AuditLog(TableName, RowPk, Action, ChangedBy, NewStatus, Note)
    SELECT 'Document', inserted.Id, 'INSERT', inserted.UserId, inserted.Status, 'Documento creado'
    FROM inserted;
END;
GO

IF OBJECT_ID('dbo.trg_Document_UpdateAudit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_Document_UpdateAudit;
CREATE TRIGGER dbo.trg_Document_UpdateAudit
ON dbo.Document
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.AuditLog(TableName, RowPk, Action, ChangedBy, OldStatus, NewStatus, Note)
    SELECT 'Document', inserted.Id, 'UPDATE', inserted.AssignedToId, deleted.Status, inserted.Status, 'Documento modificado'
    FROM inserted
    JOIN deleted ON inserted.Id = deleted.Id;
END;
GO

IF OBJECT_ID('dbo.trg_Document_DeleteAudit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_Document_DeleteAudit;
CREATE TRIGGER dbo.trg_Document_DeleteAudit
ON dbo.Document
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.AuditLog(TableName, RowPk, Action, ChangedBy, OldStatus, Note)
    SELECT 'Document', deleted.Id, 'DELETE', deleted.AssignedToId, deleted.Status, 'Documento eliminado'
    FROM deleted;
END;
GO

IF OBJECT_ID('dbo.trg_DocumentComment_InsertAudit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_DocumentComment_InsertAudit;
CREATE TRIGGER dbo.trg_DocumentComment_InsertAudit
ON dbo.DocumentComment
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.AuditLog(TableName, RowPk, Action, ChangedBy, Note)
    SELECT 'DocumentComment', inserted.Id, 'INSERT', inserted.AuthorId, 'Comentario agregado'
    FROM inserted;
END;
GO

IF OBJECT_ID('dbo.trg_DocumentComment_DeleteAudit', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_DocumentComment_DeleteAudit;
CREATE TRIGGER dbo.trg_DocumentComment_DeleteAudit
ON dbo.DocumentComment
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.AuditLog(TableName, RowPk, Action, ChangedBy, Note)
    SELECT 'DocumentComment', deleted.Id, 'DELETE', deleted.AuthorId, 'Comentario eliminado'
    FROM deleted;
END;
GO

IF OBJECT_ID('dbo.usp_CreateDocument', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_CreateDocument;
CREATE PROCEDURE dbo.usp_CreateDocument
    @UserId INT,
    @Title NVARCHAR(200),
    @FilePath NVARCHAR(500),
    @AssignedToId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        INSERT INTO dbo.Document(UserId, Title, FilePath, Status, AssignedToId)
        VALUES(@UserId, @Title, @FilePath, 'pending', @AssignedToId);
        SELECT SCOPE_IDENTITY() AS DocumentId;
    END TRY
    BEGIN CATCH
        SELECT ERROR_NUMBER() AS ErrorNumber,
               ERROR_MESSAGE() AS ErrorMessage;
    END CATCH
END;
GO

IF OBJECT_ID('dbo.usp_CreateDocumentComment', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_CreateDocumentComment;
CREATE PROCEDURE dbo.usp_CreateDocumentComment
    @DocumentId INT,
    @AuthorId INT,
    @Comment NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        INSERT INTO dbo.DocumentComment(DocumentId, AuthorId, Comment)
        VALUES(@DocumentId, @AuthorId, @Comment);
    END TRY
    BEGIN CATCH
        SELECT ERROR_NUMBER() AS ErrorNumber,
               ERROR_MESSAGE() AS ErrorMessage;
    END CATCH
END;
GO

IF OBJECT_ID('dbo.usp_AddDocumentHistory', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_AddDocumentHistory;
CREATE PROCEDURE dbo.usp_AddDocumentHistory
    @DocumentId INT,
    @Status NVARCHAR(20),
    @Note NVARCHAR(MAX) = NULL,
    @AuthorId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        INSERT INTO dbo.DocumentHistory(DocumentId, Status, Note, AuthorId)
        VALUES(@DocumentId, @Status, @Note, @AuthorId);
    END TRY
    BEGIN CATCH
        SELECT ERROR_NUMBER() AS ErrorNumber,
               ERROR_MESSAGE() AS ErrorMessage;
    END CATCH
END;
GO

IF OBJECT_ID('dbo.usp_UpdateDocumentStatus', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_UpdateDocumentStatus;
CREATE PROCEDURE dbo.usp_UpdateDocumentStatus
    @DocumentId INT,
    @Status NVARCHAR(20),
    @AssignedToId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        UPDATE dbo.Document
        SET Status = @Status,
            AssignedToId = @AssignedToId,
            UpdatedAt = SYSUTCDATETIME()
        WHERE Id = @DocumentId;
    END TRY
    BEGIN CATCH
        SELECT ERROR_NUMBER() AS ErrorNumber,
               ERROR_MESSAGE() AS ErrorMessage;
    END CATCH
END;
GO

IF OBJECT_ID('dbo.usp_GetPendingDocumentsByWorker', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_GetPendingDocumentsByWorker;
CREATE PROCEDURE dbo.usp_GetPendingDocumentsByWorker
    @WorkerId INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        SELECT d.Id, d.Title, u.Username AS ClientUsername, d.UploadedAt, d.Status
        FROM dbo.Document d
        JOIN dbo.[User] u ON d.UserId = u.Id
        WHERE d.AssignedToId = @WorkerId
          AND d.Status = 'pending'
        ORDER BY d.UploadedAt DESC;
    END TRY
    BEGIN CATCH
        SELECT ERROR_NUMBER() AS ErrorNumber,
               ERROR_MESSAGE() AS ErrorMessage;
    END CATCH
END;
GO

IF OBJECT_ID('dbo.usp_GetRejectedDocuments', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_GetRejectedDocuments;
CREATE PROCEDURE dbo.usp_GetRejectedDocuments
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        SELECT d.Id, d.Title, u.Username AS ClientUsername, d.UpdatedAt, d.Status
        FROM dbo.Document d
        JOIN dbo.[User] u ON d.UserId = u.Id
        WHERE d.Status = 'rejected'
        ORDER BY d.UpdatedAt DESC;
    END TRY
    BEGIN CATCH
        SELECT ERROR_NUMBER() AS ErrorNumber,
               ERROR_MESSAGE() AS ErrorMessage;
    END CATCH
END;
GO
