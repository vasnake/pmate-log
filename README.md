pmate-log
=========

Logging changes in MS SQL tables via triggers.

Main idea was to do logging all changes in set of tables in MS SQL DB.
In fact we could use a MS SQL [CT, CDC] capabilities but we make a decision not to.
I'd say we need something simpler.
And here it is: two files for implement logging in DB

* logtable.sql -- SQL script for creating log table
* createlog.py -- Python script for creating SQL script for creating triggers

Edit these two files and change DB name, log-table name and list of tables for attach triggers to.
Then run createlog.py to generate SQL script.
Now you can run logtable.sql and generated script in your DB console.

See inside the scripts for details.


[CT, CDC]:https://www.google.ru/search?q=change+tracking%2C+change+data+capture+ms+sql
