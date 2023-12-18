# PICO_W_WEBmin
 featured example

details see:


http://kll.byethost7.com/kllfusion01/infusions/articles/articles.php?article_id=229

* only one code.py file
* only /lib/adafruit_httpserver/
* use fix IP:PORT http://192.168.1.215:1234
* html.Server with server.poll() in a 1 sec loop ( timing problems in MAIN ) serve
* * dynamic index.html ( all in code.py )
* * static /static/about.html
* * serve a favicon
* simple styling example
* use gc.mem_free to check ( optional: gc.collect )
* use a settings.toml
* add a empty 1 min loop


