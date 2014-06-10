-- -*- coding: utf-8 -*-
-- Copyright (c) Valentin Fedulov <vasnake@gmail.com>

-- logtable.sql
-- Скрипт воссоздания таблицы журнала

-- для очистки журнала можно применить запрос
-- delete from [nintex].[pmateLog] where DATEDIFF(MINUTE, [opDate], GETDATE()) > 6000
-- останутся записи за последние 100 часов

USE [PJM6]
GO

EXEC sys.sp_dropextendedproperty @name=N'MS_Description',
    @level0type=N'SCHEMA', @level0name=N'nintex',
    @level1type=N'TABLE', @level1name=N'pmateLog'
GO

EXEC sys.sp_dropextendedproperty @name=N'MS_Description',
    @level0type=N'SCHEMA', @level0name=N'nintex',
    @level1type=N'TABLE', @level1name=N'pmateLog',
    @level2type=N'COLUMN',@level2name=N'tableName'
GO

EXEC sys.sp_dropextendedproperty @name=N'MS_Description',
    @level0type=N'SCHEMA', @level0name=N'nintex',
    @level1type=N'TABLE', @level1name=N'pmateLog',
    @level2type=N'COLUMN', @level2name=N'id'
GO

DROP TABLE [nintex].[pmateLog]
GO

DROP SEQUENCE [nintex].[pmateLogSequence]
GO

-- end drops ################################################################################

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'nintex')
BEGIN
    EXEC('CREATE SCHEMA [nintex]');
END

CREATE SEQUENCE [nintex].[pmateLogSequence]
    AS [int]
    START WITH -2147483648
    INCREMENT BY 1
    MINVALUE -2147483648
    MAXVALUE 2147483647
    CACHE
GO

CREATE TABLE [nintex].[pmateLog](
    [id] [int] PRIMARY KEY CLUSTERED
        DEFAULT (NEXT VALUE FOR [nintex].[pmateLogSequence]),
    [tableName] [nvarchar](80) NOT NULL,
    [keyName] [nvarchar](80) NOT NULL,
    [keyName2] [nvarchar](80) NULL,
    [keyName3] [nvarchar](80) NULL,
    [keyValue] [nvarchar](80) NOT NULL,
    [keyValue2] [nvarchar](80) NULL,
    [keyValue3] [nvarchar](80) NULL,
    [opName] [varchar](7) NOT NULL,
    [opDate] [datetime] NOT NULL DEFAULT (getdate()),
    [recStatus] [nvarchar](50) NULL
) ON [PRIMARY]
GO

SET ANSI_PADDING OFF
GO

CREATE INDEX [IDX_pmateLog_recStatus] ON [nintex].[pmateLog]
    ([recStatus] ASC) WITH (ALLOW_ROW_LOCKS = ON) ON [PRIMARY]
GO

CREATE INDEX [IDX_pmateLog_opDate] ON
    [nintex].[pmateLog]([opDate] ASC)
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'суррогатный ключ, identity',
    @level0type=N'SCHEMA', @level0name=N'nintex',
    @level1type=N'TABLE',@level1name=N'pmateLog',
    @level2type=N'COLUMN',@level2name=N'id'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'название таблицы в которой изменились данные',
    @level0type=N'SCHEMA',@level0name=N'nintex',
    @level1type=N'TABLE',@level1name=N'pmateLog',
    @level2type=N'COLUMN',@level2name=N'tableName'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'таблица журнала, в нее записываются триггерами сведения о изменениях в записях нужных таблиц',
    @level0type=N'SCHEMA',@level0name=N'nintex',
    @level1type=N'TABLE',@level1name=N'pmateLog'
GO

GRANT INSERT ON [nintex].[pmateLog] TO public
GO

-- прикольные запросы к журналу ################################################################################

-- select DATEDIFF(MINUTE, opDate, getdate()) as minutesago, * from nintex.pmateLog
-- delete from [nintex].[pmateLog] where DATEDIFF(MINUTE, [opDate], GETDATE()) > 60
-- update nintex.pmateLog set recStatus = '1' where DATEDIFF(MINUTE, [opDate], GETDATE()) > 30
-- select * from nintex.pmateLog where recStatus not like '1' or recStatus is null
-- select * from nintex.pmateLog where opDate < '2014-03-08 16:55:59'
