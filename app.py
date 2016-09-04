from flask import Flask, render_template, redirect, url_for, request
from flask import make_response
from arroseur import ARROSEUR
app = Flask(__name__)

def get_fieldset(index):
    string = """<form action="change_timer" method="post">
<fieldset id=fieldset%(index)i style="width: 90%%; background-color:%(color)s;">
<legend> motor %(index)i </legend>"""
    if not ARROSEUR.get_state(index):
        string+="""time (s) <input style="width: 30px" "type="text" readOnly=false name="time%(index)i" id="time%(index)i" value=%(remaining_time)i>"""
        string+="""<input type="submit" name="submit" id="submit%(index)i" value="Motor %(index)i: Go">
</fieldset>"""
    else:
        string+="""time (s) <input style="width: 30px" type="text" readOnly=true name="time%(index)i" id="time%(index)i" value=%(remaining_time)i>"""
        string+="""<input type="submit" name="submit" id="submit%(index)i" value="Motor %(index)i: Stop">
</fieldset>"""
    string+=""" 
<script>
var timer%(index)i = document.getElementById("time%(index)i")
    , button%(index)i = document.getElementById("submit%(index)i")
    , fieldset%(index)i = document.getElementById("fieldset%(index)i")
    , counter%(index)i = %(remaining_time)i
    , now = new Date()
    , deadline = new Date(now.getFullYear, now.getMonth, now.getDate, now.getHours, now.getMinutes + 15);
  setInterval(function(){
    if(counter%(index)i==0) {
        button%(index)i.value="Motor %(index)i: Go";
        timer%(index)i.value = %(on_time)i;
        fieldset%(index)i.style.background = "green"
        counter%(index)i = -1;
    }
    if(button%(index)i.value==="Motor %(index)i: Stop") {
        counter%(index)i = counter%(index)i - 1;
        timer%(index)i.value = counter%(index)i;
        timer%(index)i.readOnly = true;
    }
    else {
        timer%(index)i.readOnly = false;
    }
  }, 1000);
</script>"""
    string = string%dict(index=index, 
                         on_time=ARROSEUR.on_time[index],
                         remaining_time=ARROSEUR.get_remaining_time(index),
                         color='red' if ARROSEUR.get_state(index) else 'green')
    return string

@app.route("/")
def home():
    string = "<html>"
    on_off = ["<a href=/%i,1>0</a>", "<a href=/%i,0>1"]
    for index, state in enumerate(ARROSEUR.get_states()):
        #string+=on_off[state]%index
    	string+=get_fieldset(index)
    string+="""<input type="submit" name="submit" id="submit_all" value="All Motors: Go">"""
    string+="</html>"
    return string

@app.route('/change_timer', methods=['POST'])
def handle_data():
    print "h"
    name = request.form["submit"]
    print "i"
    if name=='All Motors: Go':
        for i in xrange(ARROSEUR.n_channels):
            ARROSEUR.set_on_time(i, ARROSEUR.on_time[i])
        return home()
    index = int(name[6:7])
    print index
    start_or_stop = name[9:]
    print start_or_stop
    if start_or_stop=="Go":
        print "so"
        time  = int(request.form["time%i"%index])
        print 'y'
        ARROSEUR.set_on_time(index, time)
        print 'z'
    else:
        print 'tr'
        ARROSEUR.set_state(index, 0)
    return home()

@app.route("/index")
def bon():
    return "bon"

if __name__ == "__main__":
    app.run(debug=True)
