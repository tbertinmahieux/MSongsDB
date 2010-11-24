function randomIsmirPaper() {
var ismirfile = 'ismirpapers_html.txt'
var req = false;
// For Safari, Firefox, and other non-MS browsers
// for Chrome, will only work once updated to an actual server
if (window.XMLHttpRequest) {
    try {
	req = new XMLHttpRequest();
    } catch (e) {
	req = false;
    }
} else if (window.ActiveXObject) {
    // For Internet Explorer on Windows
    try {
	req = new ActiveXObject("Msxml2.XMLHTTP.6.0");
    } catch (e) {
	try {
	    req = new ActiveXObject("Msxml2.XMLHTTP");
	} catch (e) {
	    try {
		req = new ActiveXObject("Microsoft.XMLHTTP");
	    } catch (e) {
		req = false;
	    }
	}
    }
}
var id = 'randomismir'
var element = document.getElementById(id);
if (!element) {
    alert("Bad id " + id +
	  "passed to clientSideInclude." +
	  "You need a div or span element " +
	  "with this id in your page.");
    return;
}
if (req) {
    // Synchronous request, wait till we have it all
    req.open('GET', ismirfile, false);
    req.send(null);
    // count lines
    var alltext = req.responseText;
    var alllines = alltext.split('\n');
    // get random number
    var randomline = Math.floor(Math.random()*(alllines.length+1))
    // set that line
    element.innerHTML = alllines[randomline];
} else {
    element.innerHTML =
	"Sorry, your browser does not support " +
	"XMLHTTPRequest objects. This page requires " +
	"Internet Explorer 5 or better for Windows, " +
	"or Firefox for any system, or Safari. Other " +
	"compatible browsers may also exist.";
}
}
