function switch_spoiler_hidden(b) {
	var c=b.parentNode.nextSibling.getElementsByTagName("div");
	var a=c[0];
	if(a.style.display=="") {
		if(a.currentStyle) {
			if(a.currentStyle.display=="block") {
				a.style.display="block"
			}
			else {
				if(a.currentStyle.display=="none") {
					a.style.display="none"
				}
			}
		}
		else {
			if(getComputedStyle(a,null).display=="block") {
				a.style.display="block"
			}
			else {
				if(getComputedStyle(a,null).display=="none") {
					a.style.display="none"
				}
			}
		}
	}
	if(a.style.display=="block") {
		a.style.display="none"
	}
	else {
		a.style.display="block"
	}
	return false
}

document.write('<style type="text/css">');
document.write('.spoiler3{visibility: hidden;}');
document.write('.spoiler3_hidden{display: none;}');
document.write('.spoiler_hidden a{visibility: visible;}');
document.write('.spoiler a{visibility: visible;');
document.write('</style>');
