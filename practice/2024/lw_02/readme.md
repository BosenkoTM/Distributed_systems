# Лабораторная работа 2.Проектирование и реализация простой клиент-серверной системы. HTTP, веб-серверы и веб-сервисы

Научиться разными средствами делать HTTP запросы, разработать популярные сценарии для nginx и RESTful интерфейсы.

## Структура запроса и ответа

Пусть  есть хороший и надёжный канал связи, то есть он гарантирует нам доставку сообщения до конечного адресата ровно один раз. На самом деле это TCP и он гарантирует нам at-least-once доставку и at-most-once обработку на стороне адресата. Мы умеем открывать соединение, надёжно слать и получать какие-то байты и закрывать соединение. Очень простая модель.

Первая версия HTTP 0.9 появилась для того, чтобы получать с какого-нибудь сервера HTML странички. Это был позапросный протокол, в котором подразумевалось открыть TCP соединение, отправить запрос в сокет, получить из него ответ и закрыть соединение. Запрос был однострочным и состоял из слова `GET` и пути на сервере:

```http
$ nc apache.org 80
GET /
```

В ответе приходил чистый HTML.

HTTP 1.0 выглядел уже более привычным для нас образом: в запросах появились заголовки, появились HEAD и POST методы, а в теле могла быть любая последовательность байт.

```http
$ nc apache.org 80
GET <url> HTTP/1.0
Header1: header 1 value
Header2: header 2 value

request data
```

## Сделаем запросы руками

Поскольку про функциональность и особенности протокола вам рассказали на лекции, давайте попробуем сами поделать запросы разными средствами. Самый чистый способ сделать HTTP запрос это отправить байты в сокет, это мы сделаем с помощью `telnet`.

```http
$ sudo telnet mgpu.ru 80
GET / HTTP/1.1
Host:mgpu.ru
```

В ответе придёт что-то подобное:
```http
HTTP/1.1 301 Moved Permanently
Server: ddos-guard
Date: Tue, 03 Sep 2024 16:31:31 GMT
Connection: keep-alive
Keep-Alive: timeout=60
Location: https://mgpu.ru/
Content-Type: text/html; charset=utf-8
Content-Length: 568
 
<!DOCTYPE html
><html lang=en><meta charset=utf-8>
<meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width">
<title>Error 301</title><style>*{margin:0;padding:0}html{font:15px/22px arial,sans-serif;background: #fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}p{margin:11px 0 22px;overflow :hidden}ins{color:#777;text-decoration :none;}
</style><p>
<b>301 - Moved Permanently .</b> <ins>That’s an error.</ins>
<p>Requested content has been permanently moved.  <ins>That’s all we know.</ins>
```

В ответе нам пришел 301 код и заголовок Location. Сервер попросил нас не ходить по незащищенному HTTP на домен hse.ru, а вместо этого пойти по адресу `https://www.hse.ru/`, иными словами открыть TCP соединение, внутри него открыть TLS соединение и после этого сделать запрос вида
```http
GET / HTTP/1.1
Host: www.hse.ru
```

Код 301 Moved Permanently используется как константный редирект и скорее всего в следующий раз браузер не будет делать запрос, на который был получен ответ 301.

Чтобы руками не создавать TLS соединение, давайте воспользуемся утилитой `curl`. Просто `curl http://hse.ru` выведет в stdout тело ответа, stderr будет пустым, а мы хотим посмотреть содержимое запроса. Для этого можно указать опцию `-v`, тогда много дополнительной информации будет выведено в stderr:

<details>
  <summary><code>$ curl -v http://hse.ru/</code></summary>

  ```http
  *   Trying 186.2.163.228...
  * TCP_NODELAY set
  * Connected to hse.ru (186.2.163.228) port 80 (#0)
  > GET / HTTP/1.1
  > Host: hse.ru
  > User-Agent: curl/7.64.1
  > Accept: */*
  >
  < HTTP/1.1 301 Moved Permanently
  < Server: ddos-guard
  < Connection: keep-alive
  < Keep-Alive: timeout=60
  < Set-Cookie: __ddg1=8HeglgfPGcjsXZoLYU5J; Domain=.hse.ru; HttpOnly; Path=/; Expires=Mon, 23-Aug-2021 10:01:38 GMT
  < Date: Sun, 23 Aug 2020 10:01:38 GMT
  < Content-Type: text/html
  < Content-Length: 162
  < Location: https://www.hse.ru/
  < Strict-Transport-Security: max-age=15552000
  < X-XSS-Protection: 1; mode=block; report=https://www.hse.ru/n/api/xss/report
  <
  <html>
  <head><title>301 Moved Permanently</title></head>
  <body>
  <center><h1>301 Moved Permanently</h1></center>
  <hr><center>nginx</center>
  </body>
  </html>
  * Connection #0 to host hse.ru left intact
  * Closing connection 0
  ```

</details>

Видим, что нас опять просят проследовать по новому URL.

<details>
  <summary><code>$ curl -v https://www.hse.ru/</code></summary>

  ```http
  *   Trying 186.2.163.228...
  * TCP_NODELAY set
  * Connected to www.hse.ru (186.2.163.228) port 443 (#0)
  * ALPN, offering h2
  * ALPN, offering http/1.1
  * successfully set certificate verify locations:
  *   CAfile: /etc/ssl/cert.pem
    CApath: none
  * TLSv1.2 (OUT), TLS handshake, Client hello (1):
  * TLSv1.2 (IN), TLS handshake, Server hello (2):
  * TLSv1.2 (IN), TLS handshake, Certificate (11):
  * TLSv1.2 (IN), TLS handshake, Server key exchange (12):
  * TLSv1.2 (IN), TLS handshake, Server finished (14):
  * TLSv1.2 (OUT), TLS handshake, Client key exchange (16):
  * TLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):
  * TLSv1.2 (OUT), TLS handshake, Finished (20):
  * TLSv1.2 (IN), TLS change cipher, Change cipher spec (1):
  * TLSv1.2 (IN), TLS handshake, Finished (20):
  * SSL connection using TLSv1.2 / ECDHE-RSA-AES128-GCM-SHA256
  * ALPN, server accepted to use h2
  * Server certificate:
  *  subject: CN=*.hse.ru
  *  start date: Dec 26 00:00:00 2019 GMT
  *  expire date: Jan 29 23:59:59 2022 GMT
  *  subjectAltName: host "www.hse.ru" matched cert's "*.hse.ru"
  *  issuer: C=GB; ST=Greater Manchester; L=Salford; O=Sectigo Limited; CN=Sectigo RSA Domain Validation Secure Server CA
  *  SSL certificate verify ok.
  * Using HTTP2, server supports multi-use
  * Connection state changed (HTTP/2 confirmed)
  * Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
  * Using Stream ID: 1 (easy handle 0x7ff74400f600)
  > GET / HTTP/2
  > Host: www.hse.ru
  > User-Agent: curl/7.64.1
  > Accept: */*
  >
  * Connection state changed (MAX_CONCURRENT_STREAMS == 128)!
  < HTTP/2 302
  < server: ddos-guard
  < set-cookie: __ddg1=IkR3Ln7mvuUxJdYVZi8u; Domain=.hse.ru; HttpOnly; Path=/; Expires=Mon, 23-Aug-2021 10:04:33 GMT
  < date: Sun, 23 Aug 2020 10:04:33 GMT
  < content-type: text/html
  < content-length: 138
  < location: https://www.hse.ru/en/
  < expires: Sun, 23 Aug 2020 10:04:33 GMT
  < cache-control: max-age=0
  < strict-transport-security: max-age=15552000
  < x-xss-protection: 1; mode=block; report=https://www.hse.ru/n/api/xss/report
  < set-cookie: tracking=ZEsKBF9CPzGw/p/9CERiAg==; expires=Thu, 31-Dec-37 23:55:55 GMT; domain=.hse.ru; path=/
  <
  <html>
  <head><title>302 Found</title></head>
  <body>
  <center><h1>302 Found</h1></center>
  <hr><center>nginx</center>
  </body>
  </html>
  * Connection #0 to host www.hse.ru left intact
  * Closing connection 0
  ```

</details>

Тут мы видим 302 в ответе, это похоже на 301, но 302 говорит о том, что для данного запроса был найден новый путь, куда надо проследовать и возможно повторный запрос даст 302 на другую страницу (такое бывает). В ответе видно, что сервер решил, что мы англоязычный клиент и хотим читать английскую версию сайта вышки. Ну действительно, давайте сделаем запрос туда и получим свой долгожданный 200.

<details>
  <summary><code>$ curl -v https://www.hse.ru/en/ > /dev/null</code></summary>

  ```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying 186.2.163.228...
  * TCP_NODELAY set
  * Connected to www.hse.ru (186.2.163.228) port 443 (#0)
  * ALPN, offering h2
  * ALPN, offering http/1.1
  * successfully set certificate verify locations:
  *   CAfile: /etc/ssl/cert.pem
    CApath: none
  * TLSv1.2 (OUT), TLS handshake, Client hello (1):
  } [224 bytes data]
  * TLSv1.2 (IN), TLS handshake, Server hello (2):
  { [102 bytes data]
  * TLSv1.2 (IN), TLS handshake, Certificate (11):
  { [3143 bytes data]
  * TLSv1.2 (IN), TLS handshake, Server key exchange (12):
  { [300 bytes data]
  * TLSv1.2 (IN), TLS handshake, Server finished (14):
  { [4 bytes data]
  * TLSv1.2 (OUT), TLS handshake, Client key exchange (16):
  } [37 bytes data]
  * TLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):
  } [1 bytes data]
  * TLSv1.2 (OUT), TLS handshake, Finished (20):
  } [16 bytes data]
  * TLSv1.2 (IN), TLS change cipher, Change cipher spec (1):
  { [1 bytes data]
  * TLSv1.2 (IN), TLS handshake, Finished (20):
  { [16 bytes data]
  * SSL connection using TLSv1.2 / ECDHE-RSA-AES128-GCM-SHA256
  * ALPN, server accepted to use h2
  * Server certificate:
  *  subject: CN=*.hse.ru
  *  start date: Dec 26 00:00:00 2019 GMT
  *  expire date: Jan 29 23:59:59 2022 GMT
  *  subjectAltName: host "www.hse.ru" matched cert's "*.hse.ru"
  *  issuer: C=GB; ST=Greater Manchester; L=Salford; O=Sectigo Limited; CN=Sectigo RSA Domain Validation Secure Server CA
  *  SSL certificate verify ok.
  * Using HTTP2, server supports multi-use
  * Connection state changed (HTTP/2 confirmed)
  * Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
  * Using Stream ID: 1 (easy handle 0x7ff027809600)
  > GET /en/ HTTP/2
  > Host: www.hse.ru
  > User-Agent: curl/7.64.1
  > Accept: */*
  >
  * Connection state changed (MAX_CONCURRENT_STREAMS == 128)!
  < HTTP/2 200
  < server: ddos-guard
  < set-cookie: __ddg1=bWr5vdSQhD8iGiaWrhYU; Domain=.hse.ru; HttpOnly; Path=/; Expires=Mon, 23-Aug-2021 10:13:40 GMT
  < date: Sun, 23 Aug 2020 10:13:40 GMT
  < content-type: text/html; charset=utf-8
  < content-length: 75220
  < etag: W/"125d4-VK+jGtkklHf8JJZyie9Jwn3mgN4"
  < x-ireland-cache-status: HIT
  < strict-transport-security: max-age=15552000
  < x-xss-protection: 1; mode=block; report=https://www.hse.ru/n/api/xss/report
  < set-cookie: tracking=ZEsKBF9CQVSv/Z/6A9lzAg==; expires=Thu, 31-Dec-37 23:55:55 GMT; domain=.hse.ru; path=/
  <
  { [15922 bytes data]
  100 75220  100 75220    0     0   773k      0 --:--:-- --:--:-- --:--:--  773k
  * Connection #0 to host www.hse.ru left intact
  * Closing connection 0
  ```

</details>

Прекрасно, мы получили ответ 200, причём curl выбрал HTTP/2 для запроса и мы видим новую версию в тексте.

Теперь давайте повторим этот же запрос через браузер и пронаблюдаем воочию все эти редиректы.

_гифка кикабельна_

[![Screencast](./media/hse-ru-network.gif)](https://yadi.sk/i/S3D89FJBhftcmQ)

Видимо, судя по отправленному IP в заголовке сервер понял, что мы из России и сразу показал нам русскую версию сайта, чего не произошло, когда мы использовали curl. Тем не менее после `http://hse.ru` нас отправили на `https://www.hse.ru/`, браузер отработал этот редирект и начал получать нормальную страницу и данные на ней.

## HTTP серверы

Имеет смысл разделить HTTP серверы на два вида:

1. Для раздачи статических файлов (html, css, js, медиа), проксирования запросов и полной поддержки протокола.
   
    _Пример:_ Apache, nginx, Traefik

2. Кастомные серверы, реализующие произвольное поведение ответа на запросы с помощью какой-нибудь библиотеки.
   
    _Популярные библиотеки:_ flask (python), aiohttp (python), phantom (c), spring (java)

Далее мы настроим простейшие сценарии в nginx и посмотрим примеры RESTful API, которые реализуют кастомные серверы.

### Nginx

Почему-то среди начинающих разработчиков есть ощущение, что nginx это что-то сложное. На самом деле конфигурации для простейших сценариев занимают меньше 10 строк и предельно понятны.

Сначала поставим `nginx` на вашу операционную систему.

Ubuntu/Debian:
```
$ sudo apt update && sudo apt install -y nginx
```

OS X:
```
$ brew install nginx
```

На OS X настраивать nginx не так приятно, как на Linux, поэтому примеры ниже будут валидны для Linux.

_Вообще, если у вас появилось желание поставить сырой nginx на OS X, то что-то идёт не так. Для локального тестирования лучше использовать docker контейнер с nginx, в него легко подсовывать статику или кастомные конфигурации (в т.ч. с проксированием в соседний контейнер). Подробнее можно прочитать [здесь](https://hub.docker.com/_/nginx).

_Хотя есть ситуации, когда вам может это понадобиться -- настольный Mac, который вы хотите использовать как медиацентр и как сервер для локальной сети, либо редиректы на локальном компьютере._

### Конфигурация сервера

Есть несколько подходов к хранению конфигурации nginx: с использованием директорий `sites-available` и `sites-enabled`; с использованием директории `conf.d`; любой кастомный. 

В первом случае:

- в директории `/etc/nginx` создаются `sites-available` и `sites-enabled`
- в файл `nginx.conf` в секцию `http`  добавляется `include /etc/nginx/sites-enabled/*.conf;`
- в `sites-available` кладутся все существующие файлы конфигурации
- в `sites-enabled` линкуются только активные конфигурации

Дерево файловой системы будет выглядеть следующим образом:

```
/etc/nginx
├── nginx.conf
├── sites-available
│   └── default
└── sites-enabled
    └── default -> /etc/nginx/sites-available/default

```

Во втором случае вместо двух директорий `sites-*` используется одна директория `conf.d`, в `nginx.conf` прописывается `include /etc/nginx/conf.d/*.conf;`

```
/etc/nginx
├── nginx.conf
└── conf.d
    └── default.conf

```

Nginx в докере использует второй подход, дистрибутив для `ubuntu` использует первый. Какой более удобный -- решать вам, в зависимости от того, как вы доставляете конфигурацию на ваши серверы. Мы будем использовать первый подход. Создадим нужные директории, если их еще нет:

```
$ mkdir -p /etc/nginx/sites-available
$ mkdir -p /etc/nginx/sites-enabled
```

Напишем файл конфигурации:

```
$ cat <<EOF > /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF
```

#### Раздача статики

Самая простая задача, которую можно реализовать с помощью nginx — захостить статические файлы. Будет странно это использовать, чтобы поделиться с кем-то файлом по сети, но, например, захостить простейший личный сайт или скомпилированное JS приложение можно именно так.

Для начала создадим простую статику, которую можно будет раздать — html файл и картинку. Это принято делать в `/var/www/your-website.com`:
```
$ sudo mkdir -p /var/www/simple_static
$ sudo chown gleb-novikov /var/www/simple_static
$ cd /var/www/simple_static
$ curl https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png > google.png
$ printf "<body>This is our first html file</body>\n" > index.html
```

Теперь в папке `/var/www/simple_static` есть два файла:

```
$ ls
google.png  index.html
```

Теперь напишем конфигурацию nginx, которая позволит получить доступ к этим файлам по HTTP. Создадим файл `/etc/nginx/sites-available/simple_static` и напишем в него очень простую конфигурацию:

```nginx
server {
  listen 80 default_server;
  server_name _;
  root /var/www/simple_static;
}
```

Теперь положим ссылку на файл в `sites-enabled` и перезагрузим nginx:

```
$ cd /etc/nginx/
$ sudo ln sites-available/simple_static sites-enabled/simple_static
$ sudo nginx -s reload
```

Сделаем запрос:

<details>
  <summary><code>$ curl -v http://localhost:80/</code></summary>
  <br>

  ```
  *   Trying ::1...
  * connect to ::1 port 80 failed: Connection refused
  *   Trying 127.0.0.1...
  * Connected to localhost (127.0.0.1) port 80 (#0)
  > GET / HTTP/1.1
  > Host: localhost
  > User-Agent: curl/7.47.0
  > Accept: */*
  >
  < HTTP/1.1 200 OK
  < Server: nginx/1.10.3 (Ubuntu)
  < Date: Wed, 02 Sep 2020 07:58:16 GMT
  < Content-Type: text/html
  < Content-Length: 43
  < Last-Modified: Mon, 31 Aug 2020 07:48:26 GMT
  < Connection: keep-alive
  < ETag: "5f4cab4a-2b"
  < Accept-Ranges: bytes
  <
  <body>
  This is our first html file
  </body>
  * Connection #0 to host localhost left intact
  ```

</details>

Стоит отметить, что несмотря на то, что мы не указали index.html в запросе, он всё равно выдался в ответе. Это происходит, так как по умолчанию в nginx открывается страница `index.html`, если она есть в корне каталога `root`.

Сделаем запрос за картинкой и спрячем содержимое картинки в `/dev/null`:

<details>
  <summary><code>$ curl -v http://localhost:80/google.png > /dev/null</code></summary>

  ```
  * connect to ::1 port 80 failed: Connection refused
  *   Trying 127.0.0.1...
  * Connected to localhost (127.0.0.1) port 80 (#0)
  > GET /google.png HTTP/1.1
  > Host: localhost
  > User-Agent: curl/7.47.0
  > Accept: */*
  >
  < HTTP/1.1 200 OK
  < Server: nginx/1.10.3 (Ubuntu)
  < Date: Wed, 02 Sep 2020 07:59:11 GMT
  < Content-Type: image/png
  < Content-Length: 13504
  < Last-Modified: Mon, 31 Aug 2020 07:51:30 GMT
  < Connection: keep-alive
  < ETag: "5f4cac02-34c0"
  < Accept-Ranges: bytes
  <
  { [13504 bytes data]
  100 13504  100 13504    0     0  12.5M      0 --:--:-- --:--:-- --:--:-- 12.8M
  * Connection #0 to host localhost left intact
  ```
</details>

Множество остальных примеров конфигураций и любые запросы можно задавать в google — nginx это самый популярный на сегодняшний день веб-сервер, поэтому инструкций великое множество.

#### HTTP проксирование

Очень важной и удобной возможностью nginx является http проксирование. Если у вас есть небольшой проект, доступный по http, то вместо прямого доступа скорее всего вы хотите спрятать его за nginx.

Пусть у нас локально на закрытом для внешнего мира порте работает какое-нибудь приложение. Мы хотим, чтобы nginx принимал запросы на конкретный домен `amazing-domain.com` по 80 порту (HTTP) и перенаправлял их в наше приложение. Для этого нужно все запросы от корня направить в наше приложение:

```nginx
server {
  listen 80;
  server_name amazing-domain.com;
  location /  {
    proxy_pass http://localhost:8123/
  }
}
```

Ещё понятнее, зачем нужно проксирование, на следующем примере. Допустим, у вас есть два сервиса — один раздаёт статику (html файлы, стили, скрипты, картинки, медиа), другой отвечает на различные запросы. Чтобы они были спрятаны за один домен, но на разных путях, то есть чтобы `amazing-domain.com` раздавал статику, а `amazing-domain.com/api/` вёл в бэкенд, можно взять первый сценарий с раздачей статики и добавить к нему `location /api/` с `proxy_pass` на любой урл для бэкенда, даже на другом сервере.

---

На самом деле, сценариев и настроек для использования nginx великое множество. Можно настраивать локальный SSL сертификат через lets-encrypt утилиту, можно крутить настройки запросов, заголовков и т.д. Рекомендую любую мысль "хочу такую настройку" загуглить, скорее всего вы найдете решение.

### Быстрая обработка клиентских запросов

Мы тут обсуждаем HTTP, запросы, серверы, которые обрабатывают запросы. Однако, вам так или иначе предстоит столкнуться с большой нагрузкой и в связи с этим хотелось бы разобрать, какие трудности при различных подходах обработки возникают, а так же какие существуют подходы к обработке большого числа запросов. На самом деле, на семинаре мы это расскажем, а в текстовой версии даём ссылку на [хороший разбор](https://iximiuz.com/ru/posts/writing-python-web-server-part-2/).

### REST & RESTful API

 _REST_ или _Representational State Transfer_ — аббревиатура, которую знает любой разработчик веб-сервисов. Формально говоря, это архитектурный подход для построения модели взаимодействия клиента и сервера. Звучит странно, но на самом деле всё просто — существует ряд принципов, следуя которым мы получим формально _REST_ приложение, вам скорее всего рассказывали о них на лекции, но их можно найти даже на [википедии](https://en.wikipedia.org/wiki/Representational_state_transfer). На деле же в индустрии сформировалась не просто лучшая, а скорее даже единственная устоявшаяся практика, согласно которой REST приложения реализуются с помощью HTTP, передают данные в форме JSON или XML, а так же следуют ряду принципов построения RESTful API.

 После того как мы научились раздавать статику через `GET` запросы с nginx сервера, можно догадаться, что похожим образом могут быть организованы модифицирующие операции. Например, добавить или удалить файл. Действительно, HTTP поддерживает также другие методы: `POST`, `HEAD`, `PUT`, `PATCH`, `DELETE`. В HTTP такой подход работы с данными называется WebDAV, он позволяет иметь полноценный доступ к удалённым файлам — читать, модифицировать и удалять. В nginx тоже можно как-то включить это, но сейчас не об этом. Помимо файлов существуют другие объекты, которыми мы бы хотели управлять.

На самом деле этот разговор начинает напоминать CRUD (акроним для Create Read Update Delete), но RESTful это не всегда CRUD. Это один из паттернов дизайна RESTful API, например:

- `GET /articles` – Список доступных статей, возможно с пагинацией и фильтрацией, настраиваемыми через GET-параметры запроса, например `GET /articles?limit=10&offset=5&author=Albert`;
- `POST /articles` – Создает статью из тела запроса;
- `GET /articles/{id}` – Статья с идентификатором `id`;
- `PUT /articles/{id}` - Полностью обновить существующую статью `id`;
- `PATCH /articles/{id}` – Частично обновить статью `id`;
- `DELETE /articles/{id}` – Удалить статью `id`.

Стоит отметить, что CRUD паттерн действительно удовлетворяет формальным требованиям REST: сервер не хранит состояние для взаимодействия с клиентом, данные могут кэшироваться на уровне HTTP, сервер умеет отвечать большому количеству клиентов, клиенты общаются с сервером одним и тем же форматом. Но можно придумать множество других модификаций формата или совсем отходящих от него веток, например, у Facebook API весьма похожий, но не совсем такой интерфейс: [документация](https://developers.facebook.com/docs/graph-api/reference/v2.2/user). Там Graph API, где к вершинам графа можно обращаться с помощью CRUD. Очень интересный и хорошо спроектированный пример RESTful API.

Или можно посмотреть на совсем странный пример: движок рекламы Яндекса. Допустим мы хотим получить рекламу для поиска по запросу «окна», для этого делается `GET` запрос в "ручку" `code`:

```
GET /code/2?text=окна HTTP/1.1
Host: yabs.yandex.ru
```

В ответе в теле баннеров будут ссылки, которые надо вызвать в случае, если пользователь кликает на тело баннера. Например

```
http://yabs.yandex.ru/count/WSuejI_zO6q19Gu051Stei35Lkz4TWK0RG8GWhY04343bbPV000003W4G0H81hgcou3h5O01-hiDY07cmiUFJf01XCwA_JAO0V2En-Grk06Wu8lp6y01PDW1qC236E01XhRx5kW1hW6W0hRBfnVm0i7Krk8Bc0FOp1gm0mJe1AI_0lW4c5o81PXSa0NJcG6W1P0Sg0Mu5x05k1Uu1OWdm0NJcG781OWdil_DiQa7vNU46I_ctqYm1u20c0ou1u05yGUqEtljdS1vmeI2s-N92geB4E20U_lbTm00AYM2yhwk1G3P2-WBc5pm2mM83D2Mthu1gGm00000miPbl-WC0U0DWu20GA0Em8GzeG_Pu0y1W12oXFiJ2lWG4e0H3GuRQ4gjsDi-y18Ku1E89w0KY2Ue5DEPlA74y0Ne50pG5RoXnF05s1N1YlRieu-y_6Fme1RGZy3w1SaMq1RGbjw-0O4Nc1VhdlmPm1SKs1V0X3sP6A0O1h0Oe-hP-WNG604O07QIHKDExP6popQOGFM8ydnMIQvapWs9jSugkDC8US5dVMyI9XpusjyR4_mgs44iCM2i6DqnsBZ9P0JvEcVcbgGBUI9ocBBODOmZeiW3V080~1?from=&q=%D0%BE%D0%BA%D0%BD%D0%B0&etext=
```

По ней можно кликнуть и где-то на серверах рекламы будет записан лог о том, что вы как пользователь кликнули по заголовку. Совершенно непонятно, что происходит. И на самом деле, простому пользователю и не должно быть понятно. Это далеко от CRUD (хотя бы потому, что почти Read-Only), однако это тоже можно назвать RESTful API, потому что соблюдаются основные принципы.


### Индивидуальное задание


#### Оборудование и ПО:
- Операционная система Ubuntu, OS X.
- Установленные пакеты `telnet`, `curl`, `nginx`.
- Установленный интерпретатор Python (для реализации REST API)
- Инструменты командной строки (curl, wget, telnet)
- Доступ к интернету.

#### Теоретическая часть.
1. **HTTP-запросы и ответы:** изучение структуры HTTP-запросов (методы GET, POST, PUT, DELETE и т.д.) и ответов (коды статуса, заголовки и тело ответа).
2. **Telnet:** инструмент для отправки HTTP-запросов на определенные порты и получения ответов. Позволяет вручную взаимодействовать с HTTP-сервером.
3. **Curl:** мощный инструмент командной строки для передачи данных с URL. Поддерживает различные протоколы, включая HTTP/HTTPS.
4. **nginx:** популярный HTTP-сервер, поддерживающий высокую производительность и гибкость в настройке.
5. **REST и RESTful API:** архитектурный стиль для создания веб-сервисов, использующий HTTP и методы GET, POST, PUT, DELETE для взаимодействия с ресурсами.

#### Ход работы:

##### Шаг 1: Установка необходимых инструментов

1.1. Установите `telnet` и `curl`, если они не установлены:
```bash
sudo apt-get update
sudo apt-get install telnet curl
```

1.2. Установите и настройте nginx:
```bash
sudo apt-get install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

##### Шаг 2: Анализ HTTP-запросов через telnet

2.1. Откройте терминал и подключитесь к HTTP-серверу через telnet:
```bash
telnet <доменное_имя> 80
```
Пример для домена `example.com`:
```bash
telnet example.com 80
```

2.2. Отправьте HTTP-запрос вручную, например, запрос типа GET:
```bash
GET / HTTP/1.1
Host: example.com
```

2.3. Анализируйте полученный ответ сервера: статусный код, заголовки и тело ответа.

##### Шаг 3: Использование curl для отправки HTTP-запросов

3.1. Отправьте простой GET-запрос с использованием curl:
```bash
curl http://example.com
```

3.2. Отправьте POST-запрос с данными:
```bash
curl -X POST http://example.com/resource -d "param1=value1&param2=value2"
```

3.3. Используйте опции curl для вывода заголовков ответа:
```bash
curl -I http://example.com
```

##### Шаг 4: Настройка и анализ HTTP-сервера nginx

4.1. Откройте файл конфигурации nginx:
```bash
sudo nano /etc/nginx/sites-available/default
```

4.2. Настройте сервер для работы с определенным доменом и добавьте необходимые директивы.

4.3. Перезапустите nginx:
```bash
sudo systemctl restart nginx
```

4.4. Проверьте работоспособность сервера с помощью curl:
```bash
curl http://localhost
```

##### Шаг 5: Изучение REST и RESTful API

5.1. Настройте простой REST API на сервере nginx с использованием curl и конфигурационных файлов nginx.

5.2. Создайте тестовые GET и POST запросы к вашему API и проверьте их работоспособность через curl.


##### Шаг 6: Установка и базовая настройка nginx

6.1. Установите nginx:
```bash
sudo apt-get update
sudo apt-get install nginx
```

6.2. Проверьте статус работы nginx:
```bash
sudo systemctl status nginx
```

6.3. Откройте конфигурационный файл nginx для редактирования:
```bash
sudo nano /etc/nginx/sites-available/default
```

6.4. Настройте виртуальный хост для обработки запросов к вашему лока��ьному сайту:
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /var/www/html;
        index index.html index.htm;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6.5. Перезапустите nginx для применения настроек:
```bash
sudo systemctl restart nginx
```

##### Шаг 7: Реализация простого REST API на Python

71. Установите Python и необходимые модули:
```bash
sudo apt-get install python3 python3-pip
pip3 install flask
```

72. Создайте простой Flask API:
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# Пример ресурсов
data = {
    "items": [
        {"id": 1, "name": "Item 1", "description": "Description of Item 1"},
        {"id": 2, "name": "Item 2", "description": "Description of Item 2"},
    ]
}

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(data)

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in data['items'] if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items', methods=['POST'])
def create_item():
    new_item = request.json
    data['items'].append(new_item)
    return jsonify(new_item), 201

if __name__ == '__main__':
    app.run(debug=True)
```

73. Запустите Flask API на порту 5000:
```bash
python3 app.py
```

##### Шаг 8: Тестирование работы REST API через nginx

8.1. Используйте curl для взаимодействия с API через nginx:
```bash
# Получение списка всех элементов
curl http://localhost/api/items

# Получение конкретного элемента
curl http://localhost/api/items/1

# Создание нового элемента
curl -X POST -H "Content-Type: application/json" -d '{"id":3,"name":"Item 3","description":"Description of Item 3"}' http://localhost/api/items
```

8.2. Проверьте, как nginx передает запросы от клиента к Flask-серверу и возвращает ответ.

##### Шаг 9: Разработка RESTful API и его настройка

9.1. Добавьте дополнительные маршруты и методы для обработки PUT и DELETE запросов в ваш API.

9.2. Настройте nginx для обработки CORS-запросов (если необходимо) и добавьте правила кеширования, если API будет использоваться на production сервере.

9.3. Убедитесь, что все методы работают корректно через тестирование с curl или через инструмент Postman.

#### Варианты заданий HTTP-запросы
1. Анализ главной страницы `yandex.ru` с помощью telnet.
2. Запрос погоды на `weather.yandex.ru` через curl.
3. Отправка POST-запроса к API `vk.com`.
4. Получение курса валют с сайта `cbr.ru` с помощью curl.
5. Проверка доступности сайта `lenta.ru` через telnet.
6. Анализ заголовков ответа сервера на `mail.ru`.
7. Запрос списка новостей с `rbc.ru`.
8. Отправка POST-запроса к API `sberbank.ru`.
9. Получение списка статей с `ria.ru`.
10. Запрос текущих котировок акций на `moex.com`.
11. Проверка состояния сайта `gazeta.ru`.
12. Анализ HTTP-ответов на `tass.ru`.
13. Получение списка товаров с `ozon.ru`.
14. Отправка запроса к API `rosbank.ru`.
15. Анализ главной страницы `kommersant.ru`.
16. Запрос информации о рейсах с сайта `aeroflot.ru`.
17. Отправка GET-запроса к API `yandex.maps`.
18. Получение информации с сайта `alrosa.ru`.
19. Запрос данных о недвижимости на `cian.ru`.
20. Проверка состояния сервера на `rzd.ru`.
21. Получение расписания поездов на `yandex.ru/rasp`.
22. Запрос информации о кредитах на `vtb.ru`.
23. Анализ главной страницы `banki.ru`.
24. Запрос данных о тарифах с сайта `beeline.ru`.
25. Проверка доступности сайта `tinkoff.ru`.

#### Варианты для студентов REST API или RESTful API через nginx

Создать конфигурацию nginx и REST API, которая будет взаимодействовать с указанным сайтом или API. 

1. Интеграция с API погоды от `weather.yandex.ru`.
2. Интеграция с API новостей от `newsapi.org` (с русскоязычными источниками).
3. Создание REST API для управления данными о фильмах с `kinopoisk.ru`.
4. Настройка nginx для кэширования данных с `mail.ru`.
5. Создание API для получения курса валют с `cbr.ru`.
6. Интеграция с API сервиса `dadata.ru`.
7. Настройка nginx для обратного проксирования запросов к API `mos.ru`.
8. Реализация REST API для получения данных о товарах с `ozon.ru`.
9. Создание API для доступа к новостям с `rbc.ru`.
10. Настройка nginx для работы с API `vk.com`.
11. Создание API для получения данных о текущих курсах акций с `moex.com`.
12. Интеграция с API `sberbank.ru`.
13. Настройка nginx для кеширования и балансировки запросов на `gazeta.ru`.
14. Создание REST API для работы с ресурсами `ria.ru`.
15. Настройка nginx для обработки запросов на `yandex.maps`.
16. Интеграция с API `tass.ru`.
17. Создание API для работы с данными о рейсах `aeroflot.ru`.
18. Интеграция с API `rzd.ru`.
19. Настройка nginx для обработки данных с `kommersant.ru`.
20. Создание REST API для обработки данных с `cian.ru`.
21. Интеграция с API `alrosa.ru`.
22. Настройка и тестирование работы с API `beeline.ru`.
23. Создание API для управления данными о кредитах с `tinkoff.ru`.
24. Интеграция с API `rosbank.ru`.
25. Настройка nginx для работы с API `vtb.ru`

#### Отчет по лабораторной работе
В отчете должны быть представлены:
1. Описание каждого шага работы.
2. Результаты выполнения HTTP-запросов через telnet и curl.
3. Настройки конфигурационных файлов nginx и API.
4. Результаты работы с REST и RESTful API.
7. Пример конфигурационных файлов и кода API.
8. Результаты тестирования API через curl.
9. Выводы о работе REST API через nginx.
