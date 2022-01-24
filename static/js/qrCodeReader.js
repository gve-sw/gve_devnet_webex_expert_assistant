// Taken and modified from https://www.sitepoint.com/create-qr-code-reader-mobile-website/
const loc_qrcode = window.qrcode;

const video = document.createElement("video");
const canvasElement = document.getElementById("qr-canvas");
const canvas = canvasElement.getContext("2d");

const qrResult = document.getElementById("qr-result");
const outputData = document.getElementById("outputData");
const btnScanQR = document.getElementById("btn-scan-qr");

let scanning = false;

// Tick function for each frame
function tick() {
    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;
    canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
  
    scanning && requestAnimationFrame(tick);
}

// Actual scan function that uses the qr code lib to scan for qr codes
function scan() {
    try {
        loc_qrcode.decode();
    } catch (e) {
        setTimeout(scan, 300);
    }
}
  
  
// Bind for the scan button
btnScanQR.onclick = () => {
  console.log("Starting qrcode scanner");
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then(function(stream) {
      scanning = true;
      qrResult.hidden = true;
      btnScanQR.hidden = true;
      canvasElement.hidden = false;
      video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
      video.srcObject = stream;
      video.play();
      tick();
      scan();
    });
};


// Callback for when qrcode is scanned
loc_qrcode.callback = (res) => {
    if (res) {
      var model = res;
      outputData.innerText = res;
      scanning = false;
  
      video.srcObject.getTracks().forEach(track => {
        track.stop();
      });
      // Create a hidden form to submit the data
      var worker_name = window.localStorage.getItem("worker_name");
      var callme = window.localStorage.getItem("callme");
      var realwear_headset = window.localStorage.getItem("realwear_headset");
      var forwardUrl = "/worker_expert_choice?model=" + model + "&worker_name=" + worker_name + "&realwear_headset=" + realwear_headset + "&callme=" + callme;

      window.location.href = forwardUrl;
    }
  };
