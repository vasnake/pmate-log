-- -*- coding: utf-8 -*-
-- Copyright (c) Valentin Fedulov <vasnake@gmail.com>

-- trigger.sql
-- Исходный шаблон для триггеров журналирования
-- Не используется, служит только для иллюстрации к идее

USE [PJM7_razborka]
GO

drop trigger dbo.[logStatementTrigger]
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TRIGGER dbo.[logStatementTrigger]
   ON  dbo.[Statement]
   AFTER INSERT,DELETE,UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @i INT, @d INT;
    SELECT @i = COUNT(*) FROM inserted;
    SELECT @d = COUNT(*) FROM deleted;
    IF @i + @d > 0
    BEGIN
        IF @i > 0 AND @d = 0
            -- insert
            INSERT INTO dbo.[pmateLog](tableName, keyName, keyValue, opName)
            SELECT 'dbo.Statement' as tn, 'ID' as kn, [ID] as kv, 'insert' as opn
            from inserted
        IF @i > 0 AND @d > 0
            -- update
            INSERT INTO dbo.[pmateLog](tableName, keyName, keyValue, opName)
            SELECT 'dbo.Statement' as tn, 'ID' as kn, [ID] as kv, 'update' as opn
            from inserted
        IF @i = 0 AND @d > 0
            -- delete
            INSERT INTO dbo.[pmateLog](tableName, keyName, keyValue, opName)
            SELECT 'dbo.Statement' as tn, 'ID' as kn, [ID] as kv, 'delete' as opn
            from deleted
    END
END
GO
