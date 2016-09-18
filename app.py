from flask import Flask, render_template, redirect, url_for, request
from flask import make_response
from arroseur import ARROSEUR
app = Flask(__name__)

FONTSIZE = 24

def get_fieldset(index):
    string = """<form action="change_timer" method="post">
<fieldset id=fieldset%(index)i style="width: 90%%; background-color:%(color)s;">
<legend onclick=change_name%(index)i()> %(name)s </legend>"""
    if not ARROSEUR.get_state(index):
        string+="""time (s) <input style='width: 80px; font-size: %(fs)ipx;' "type="text" readOnly=false name="time%(index)i" id="time%(index)i" value=%(remaining_time)i>"""
        string+="""<input type="submit" name="submit" id="submit%(index)i" style="font-size: %(fs)ipx; height:60px" value="Motor %(index)i: Go">
</fieldset>"""
    else:
        string+="""time (s) <input style="width: 80px; font-size: %(fs)ipx;" type="text" readOnly=true name="time%(index)i" id="time%(index)i" value=%(remaining_time)i>"""
        string+="""<input type="submit" name="submit" style="font-size: %(fs)ipx;" id="submit%(index)i" value="Motor %(index)i: Stop">
</fieldset>"""
    string+=""" 
<script>
function change_name%(index)i() {
    var name = prompt("Enter new channel name", "%(name)s")
    var method = "post"; // Set method to post by default if not specified.
    var path = "change_name"
    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "name");
    hiddenField.setAttribute("value", name);
    var hiddenField2 = document.createElement("input");
    hiddenField2.setAttribute("type", "hidden");
    hiddenField2.setAttribute("name", "index");
    hiddenField2.setAttribute("value", "%(index)i");


    form.appendChild(hiddenField);
    form.appendChild(hiddenField2);

    document.body.appendChild(form);
    if(name!=null) {
        form.submit();
    }
}

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
    names = ARROSEUR.get_channel_names()
    print names
    string = string%dict(index=index, 
                         on_time=ARROSEUR.on_time[index],
                         remaining_time=ARROSEUR.get_remaining_time(index),
                         color='red' if ARROSEUR.get_state(index) else 'green',
                         name=names[index],
                         fs=FONTSIZE)
    return string

@app.route("/")
def home():
    string = "<html style='font-size:%ipx;'>"%FONTSIZE
    on_off = ["<a href=/%i,1>0</a>", "<a href=/%i,0>1"]
    for index, state in enumerate(ARROSEUR.get_states()):
        #string+=on_off[state]%index
    	string+=get_fieldset(index)
    string+="""<input type="submit" style="font-size: %i;" name="submit" id="submit_all" value="All Motors: Go">"""%FONTSIZE
    string+="</html>"
    return string

@app.route('/change_timer', methods=['POST'])
def handle_data():
    name = request.form["submit"]
    if name=='All Motors: Go':
        for i in xrange(ARROSEUR.n_channels):
            ARROSEUR.set_on_time(i, ARROSEUR.on_time[i])
        return home()
    index = int(name[6:7])
    print index
    start_or_stop = name[9:]
    print start_or_stop
    if start_or_stop=="Go":
        time  = int(request.form["time%i"%index])
        ARROSEUR.set_on_time(index, time)
    else:
        ARROSEUR.set_state(index, 0)
    return home()

@app.route("/index")
def bon():
    return "bon"

@app.route("/change_name", methods=['POST'])
def change_name():
    name = request.form["name"]
    index = int(request.form["index"])
    ARROSEUR.set_channel_name(index, name)
    return home()

if __name__ == "__main__":
    app.run(debug=True)
