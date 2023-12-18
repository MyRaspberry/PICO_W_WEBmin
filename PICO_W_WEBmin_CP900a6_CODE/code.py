'''
based on
https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/blob/main/examples/httpserver_simpletest_auto.py

but avoid the blocking
server.serve_forever(str(wifi.radio.ipv4_address))
what even uses a sleep() if ", poll_interval: float " is used!

and use fix IP and PORT as all web development projects suggest

here check on PICO W mem_free because of current issues of THIS CP900a6

also minimalistic use a dynamic html page to serve

v1.0.1 add a static "/static/about.html"

change from CP900a6 to CP829 / mem startup much better,
but at web page call mem rundown and recover
so we prepare and test gc.collect
'''

import gc # ______________________________________________ micropython garbage collection # use gc.mem_free() # use gc.collect()
Imp=(f"\nFREE MEM report after imports\n+ import gc {gc.mem_free()}\n")
import os
Imp+=(f"+ import os {gc.mem_free()}\n")
import microcontroller # _________________________________ for reboot
Imp+=(f"+ import microcontroller {gc.mem_free()}\n")
import time  # ___________________________________________ we use time.monotonic aka seconds in float
Imp+=(f"+ import time {gc.mem_free()}\n")
import socketpool
Imp+=(f"+ import socketpool {gc.mem_free()}\n")
from ipaddress import ip_address
Imp+=(f"+ from ipaddress {gc.mem_free()}\n")
import wifi
Imp+=(f"+ import wifi {gc.mem_free()}\n")
from adafruit_httpserver import Server, Request, Response, # Redirect, GET, POST # , Websocket
Imp+=(f"+ from adafruit_httpserver import Server, Request, Response {gc.mem_free()}\n")


DIAG = bool(os.getenv('DIAG')) # _________________________ change DIAG print in 'settings.toml' 1 0 and reload to board
if ( DIAG ) : print(Imp)
del Imp # ________________________________________________ variable needed for boot only

use_COLLECT = True

THIS_REVISION = os.getenv('THIS_REVISION')
THIS_OS = os.getenv('THIS_OS')
WIFI_SSID = os.getenv('WIFI_SSID')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD')
WIFI_IP = os.getenv('WIFI_IP')
PORT = os.getenv('PORT')

I_AM = f"!!! this is a PICO W with Circuit Python {THIS_OS}"
print(I_AM)

REFRESH = 30 # ___________________________________________ dynamic web pages might have a auto refresh

# ________________________________________________________ HTML STYLE section escape the { , } by {{ , }}
HTML_INDEX = """
<!DOCTYPE html><html><head>
<title>Pico W</title>
<link rel="icon" type="image/x-icon" href="favicon.ico">
<style>
body {{font-family: "Times New Roman", Times, serif; background-color: LavenderBlush;
display:inline-block; margin: 0px auto; text-align: center;}}
h1 {{color: deeppink; word-wrap: break-word; padding: 1vh; font-size: 30px;}}
p {{font-size: 1.5rem; word-wrap: break-word;}}
</style>
<meta http-equiv="refresh" content="{REFRESH}">
</head><body>
<h1>{I_AM}</h1>
<p style="color:blue; font-size:25px;"> runtime: {RUNTIME:,.2f} sec</p>
<p> autorefresh: {REFRESH} sec</p>
<hr>
<p style="text-align:right"><a href="about.html" target="_blank" >about</a></p>
<hr>
</body></html>
"""

wifi.radio.set_ipv4_address( # ___________________________ fixIP ( requires > CP 8.0.0 beta 4 )
    ipv4=ip_address(WIFI_IP),
    netmask=ip_address("255.0.0.0"),
    gateway=ip_address("192.168.1.1"),
    ipv4_dns=ip_address("192.168.1.1"),
)

wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"www Connected to {WIFI_SSID}")

pool = socketpool.SocketPool(wifi.radio)

server = Server(pool, "/static") # _______________________ use later and use PORT 80 unless you think of it as a password?
#server = Server(pool, "/static", debug=True)

@server.route("/")
def base(request: Request): # ____________________________ Serve a dynamic text message.
    if use_COLLECT : gc.collect()
    return Response(request, HTML_INDEX.format(
                REFRESH=REFRESH,
                I_AM=I_AM,
                RUNTIME=time.monotonic(),
                ),
                content_type='text/html'
            )

@server.route("/about")
def about(request: Request): # ____________________________ Serve a static HTML file
    if use_COLLECT : gc.collect()
    return FileResponse(request, "about.html") # __________ at /static/about.html

print(f"www Listening on http://{str(wifi.radio.ipv4_address)}:{PORT} " )

#server.serve_forever(str(wifi.radio.ipv4_address))
server.start(host=str(wifi.radio.ipv4_address),port=PORT) # _ startup the server
if DIAG : print(f"+ server.start {gc.mem_free()} ")
if use_COLLECT : gc.collect()

check_last1 = time.monotonic() # _________________________ init CPU seconds in float
dt1 = 1.0 # sec
check_last2 = check_last1 # ______________________________ init CPU seconds in float
dt2 = 60.0 # sec

while True:  # ___________________________________________ MAIN
    try:
        if ( check_last1 + dt1 <= time.monotonic() ) : # ___ make non blocking 1 sec timer loop for server.poll
            check_last1 += dt1 # ___________________________ this does not add up timing errors
            if DIAG : print(".",end="") # __________________ REPL show a 'dot' every second
            # the 1 sec JOB
            ret = server.poll() # __________________________ check if the page was called
            if ( ret == "no_request" ) :
                pass
            else:
                print(f"\n{ret}")
                if DIAG : print(f"free1: {gc.mem_free()}")
            if use_COLLECT : gc.collect()

        if ( check_last2 + dt2 <= time.monotonic() ) : # ___ make non blocking 1 min timer loop
            check_last2 += dt2 # ___________________________ this does not add up timing errors
            print("job2") # ________________________________ the 1 min JOB
            if DIAG : print(f"free2: {gc.mem_free()}")
            if use_COLLECT : gc.collect()

    except OSError:
        print("ERROR server poll")
        microcontroller.reset() # ________________________ here do a reboot

    # but as i am a micro controller aka PLC, there is so much more to do here!
    # like handling board I/O for measureing something  ...
