var inpF, hist;
var inpFdefault = "Enter your text here.";

window.onload = setup;

function getResponse(){
  // Pushing prompt to the history
  var prompt = inpF.value;
  if (prompt === inpFdefault || prompt === "")
    return; // show warning message?
  hist = document.getElementById("history");
  hist.innerHTML += `<div class="history user">${prompt}</div>`;
  inpF.value = "";
  console.log([inpF.value]);
  console.log(prompt);

  // Sending stuff to server (for now, no server)
  var nlgResponse = "SWABHA's MY FAVORITE NLPer!";


  var slider = document.getElementById("scalingFactor");
  scalingFactor = Math.pow(10, slider.value);
 
  var toSend;
  toSend = $.trim(prompt).replace(/\n/g,"|||");
  toSend = toSend.replace(/[\u2018\u2019]/g, "'")
	         .replace(/[\u201C\u201D]/g, '"');
  toSend = toSend + '|||' + scalingFactor;
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
      console.log(xmlHttp.responseText);
      nlgResponse = xmlHttp.responseText;
      hist.innerHTML = `<div class="history nlg" style="font-size:34px">${nlgResponse}</div>`;
      hist.innerHTML += `<hr class="removable">`;
    }
  }
  xmlHttp.open("POST", window.location.href+"?inputText="+toSend, true);
  xmlHttp.send();
}

function setup(){
  /*Input field aesthetics*/
  inpF = document.getElementById("inputfield");
  inpF.onfocus = function(){
    if(inpF.value === inpFdefault){
      inpF.style = "color: black;font-style: normal";
      inpF.value = "";
    }
  };
  inpF.onblur = function(){
    if (inpF.value === ""){
      inpF.style = "color: grey;font-style: italic;";
      inpF.value = inpFdefault;
    }
  };
  inpF.onkeyup = function(e){
    if (e.keyCode === 13 && !e.shiftKey){
      getResponse();
    }
  };
}
