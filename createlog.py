#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) Valentin Fedulov <vasnake@gmail.com>

u'''createlog.py
Скрипт для удаления и создания триггеров к таблицам в MS SQL Server.
Результат работы скрипта - SQL код для выполнения в БД.
Обязательно сохраните список 'DROP'-ов после выполнения SQL!

Триггеры записывают в спец.таблицу журнала {LOGTABLE}
сведения о измененных записях в отслеживаемых таблицах.
Подробности см. в прилагаемой документации.

Запускать можно онлайн
    http://repl.it/languages/Python
    http://www.compileonline.com/execute_python_online.php
    http://ideone.com/
    http://codepad.org/
или установить Python на локальную машину
    http://www.python.org/download/releases/2.7.6/
'''

# Входные параметры
DBNAME = 'PJM6'
LOGTABLE = '[nintex].[pmateLog]'
TRIGGERPREFIX = 'nintex_logTrigger_'

TABLESINFO = '''
    dbo.UserRole;UserID,RoleID
    dbo.Statement;ID
    dbo.Invoice;ID
    dbo.Payment;ID
    dbo.TimeEntry;ID
    dbo.Expense;ID
    dbo.Project;ID
    dbo.Calculation;ID
'''

################################################################################
# Текст скрипта

# Шаблоны
INTRO = '''
USE [{dbName}]
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

'''

DROPTRIGGER = '''DROP TRIGGER {triggerName}
GO
'''

#Cannot create trigger 'nintex.logTriggertesttab1' because its schema is different from the schema of the target table or view
#не выйдет добавить обработку ошибок, чтобы из-за облома журналирования не ломались прикладухи
#    http://www.sommarskog.se/error-handling-I.html#triggercontext
#проверено мульти-роу обновления таблиц

CREATETRIGGER = '''
CREATE TRIGGER {triggerName}
   ON  {tableName}
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
            {logInsert}
        IF @i > 0 AND @d > 0
            -- update
            {logUpdate}
        IF @i = 0 AND @d > 0
            -- delete
            {logDelete}
    END
END
GO
'''

INSERTOLOG = '''
            INSERT INTO %s(tableName, {keyNameFields} {keyValueFields} opName)
            SELECT '{tableName}' as tn, {keyNameValues} {keyValueValues} '{operation}' as opn
            from {fromTable}
''' % LOGTABLE


def getIntro(dbname):
    ''' Возвращает стандартный заголовок скрипта SQL
    '''
    res = INTRO.replace('{dbName}', dbname)
    return res


def getTriggerFullName(params):
    ''' возвращает полное имя триггера
    output example: [dbo].[logTriggerUserRole]

    input example: {'triggerName': 'logTriggerUserRole',
        'tableName': 'dbo.UserRole',
        'keys': [
            {'keyName':'UserID', 'keyValue':'UserID'},
            {'keyName':'RoleID', 'keyValue':'RoleID'}] }
    '''
    tn = params['triggerName'].strip()
    schm = params['tableName'].split('.')[0].strip()
    triggerName = '[%s].[%s]' % (schm, tn)
    return triggerName


def getDropTrigger(params):
    ''' возвращает текст для DROP конкретного триггера

    input example: {'triggerName': 'logTriggerUserRole',
        'tableName': 'dbo.UserRole',
        'keys': [
            {'keyName':'UserID', 'keyValue':'UserID'},
            {'keyName':'RoleID', 'keyValue':'RoleID'}] }
    '''
    triggerName = getTriggerFullName(params)
    res = DROPTRIGGER.replace('{triggerName}', triggerName)
    return res


def getCreateTrigger(params):
    ''' возвращает текст для CREATE конкретного триггера

    input example: {'triggerName': 'logTriggerUserRole',
        'tableName': 'dbo.UserRole',
        'keys': [
            {'keyName':'UserID', 'keyValue':'UserID'},
            {'keyName':'RoleID', 'keyValue':'RoleID'}] }

    Params should be transfomed before using in template
        triggerName example: [dbo].[logStatementTrigger]
        tableName example: [dbo].[Statement]
        keyName example: [ID]
        keyValue example: [ID]
    '''
    triggerName = getTriggerFullName(params) # [dbo].[logStatementTrigger]
    tableName = params['tableName'].split('.')
    tableName = '[%s]' % ('].['.join(tableName), ) # [dbo].[Statement]
    keyNameFields = '' # keyName, keyName2,
    keyValueFields = '' # keyValue, keyValue2,
    keyNameValues = '' # '[ID]' as kn, '[uID]' as kn2,
    keyValueValues = '' # [ID] as kv, [uID] as kv2,

    cnt = 0
    for x in params['keys']:
        suff = ''
        cnt += 1
        if cnt > 1: suff = str(cnt)
        if cnt > 3: break
        keyNameFields += 'keyName%s, ' % (suff,)
        keyValueFields += 'keyValue%s, ' % (suff,)
        keyNameValues += "'[%s]' as kn%s, " % (x['keyName'], suff)
        keyValueValues += "[%s] as kv%s, " % (x['keyValue'], suff)

    insert = INSERTOLOG.replace('{keyNameFields}', keyNameFields
        ).replace('{keyValueFields}', keyValueFields
        ).replace('{keyNameValues}', keyNameValues
        ).replace('{keyValueValues}', keyValueValues)

    logInsert = insert.replace('{operation}', 'insert'
        ).replace('{fromTable}', 'inserted').strip()
    logUpdate = insert.replace('{operation}', 'update'
        ).replace('{fromTable}', 'inserted').strip()
    logDelete = insert.replace('{operation}', 'delete'
        ).replace('{fromTable}', 'deleted').strip()

    res = CREATETRIGGER.replace('{logInsert}', logInsert
        ).replace('{logUpdate}', logUpdate
        ).replace('{logDelete}', logDelete
        ).replace('{triggerName}', triggerName
        ).replace('{tableName}', tableName)
    return res


def getTableInfoList(tablesinfo):
    ''' разбирает входной текст и возвращает список строк с информацией по таблицам

    output example: ['dbo.Statement;ID', 'dbo.Calculation;ID', 'dbo.Invoice;ID', 'dbo.Payment;ID', 'dbo.UserRole;UserID,RoleID']
    '''
    res = []
    lines = tablesinfo.split('\n')
    for x in lines:
        x = x.strip()
        if x:
            res.append(x)
    return res


def getTrigParams(tableinfo):
    ''' разбирает входную строку, пример: "dbo.UserRole;UserID,RoleID"
    и возвращает словарь параметров, используемых при генерации триггера

    output example: {'triggerName': 'logTriggerUserRole',
        'tableName': 'dbo.UserRole',
        'keys': [
            {'keyName':'UserID', 'keyValue':'UserID'},
            {'keyName':'RoleID', 'keyValue':'RoleID'}] }
    '''
    (tableName, keys) = tableinfo.split(';')
    triggerName = TRIGGERPREFIX + tableName.split('.')[-1].strip()
    keysList = []
    for x in keys.split(','):
        x = x.strip()
        keysList.append({'keyName': x, 'keyValue': x})

    res = {'triggerName': triggerName,
        'tableName': tableName.strip(),
        'keys': keysList}
    #~ print "tn: '%s', ks: '%s', tgn: '%s', kl: '%s'" % (tableName, keys, triggerName, keysList)
    return res


def main():
    ''' создает и выводит в stdout скрипт удаления триггеров; скрипт создания триггеров
    '''
    res = getTableInfoList(TABLESINFO)
    #~ print "input list: '%s'" % (res, )
    print getIntro(DBNAME)
    for x in res:
        p = getTrigParams(x)
        #~ print "trigger parameters: '%s'" % (p, )
        print getDropTrigger(p)

    print '-- end drops ################################################################################'
    for x in res:
        p = getTrigParams(x)
        print getCreateTrigger(p)


if __name__ == "__main__":
    main()
