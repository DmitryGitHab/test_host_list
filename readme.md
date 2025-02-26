Установка зависимостей: 
"pip install req.txt"


запуск сервера:
'uvicorn main:app --reload'

Принцип работы, при старте сервера обращается к БД, если он пустая на странице сайта будет пусто, если в бд есть данные они отобразяться на главной стриничке.
Можно добавлять вручную, можно экспортировать из csv файла, сервера сохраняться в БД
Соответсвенно при удалении со страницы серверов они так же удаляются из БД


![alt text](https://github.com/DmitryGitHab/test_host_list/blob/main/demo.jpg?raw=true)

![alt text](https://github.com/DmitryGitHab/test_host_list/blob/main/task.jpg?raw=true)