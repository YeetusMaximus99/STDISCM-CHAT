Run the server script first then the client scripts
use localhost so you dont have to run it through different machines over a network
use any unused port for the ports

NOTE: client scripts use localhost:8000 (previously 8080). we can add inputs to make the clients choose what server address and port to use

You need to download MySQL workbench and run a server on local host to run the code. create a schema called new_schema then create a table called messages. under the messages table there should be 2 columns. user and messagescol. user is a column made up of varchar(255) and messagescol is a LONGTEXT. To access the python mysql package, uses "pip install mysql-python" and "pip install mysql-python-connector
