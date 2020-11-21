
var report = navigator.userAgent
console.log(report);

let b64d = 'nothing'
let globlob = 'noURL'

//iphone recording
window.globalFunc = function (action){
  console.log('global started');
  window.URL = window.URL || window.webkitURL;
  /**
   * Detect the correct AudioContext for the browser
   * */
  window.AudioContext = window.AudioContext || window.webkitAudioContext;
  navigator.getUserMedia  = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
  var recorder = new RecordVoiceAudios();


  if (action == 'start'){
    recorder.startRecord()
    console.log('recorder start');
  }
  else if (action == 'stop'){
    recorder.stopRecord();
  }

  function RecordVoiceAudios() {

      let encoder = null;
      let microphone;

      var audioContext;
      let processor;
      let config = {
          bufferLen: 4096,
          numChannels: 2,
          mimeType: 'audio/mpeg'
      };

      this.startRecord = function() {
        console.log('startRecord');
          audioContext = new AudioContext();
          /** Create a ScriptProcessorNode with a bufferSize of
          * 4096 and two input and output channel
          * */
          if (audioContext.createJavaScriptNode) {
              processor = audioContext.createJavaScriptNode(config.bufferLen, config.numChannels, config.numChannels);
              console.log('java processer');
          } else if (audioContext.createScriptProcessor) {
              processor = audioContext.createScriptProcessor(config.bufferLen, config.numChannels, config.numChannels);
              console.log('script processer');
          } else {
              console.log('WebAudio API has no support on this browser.');
          }
          processor.connect(audioContext.destination);
          /**
          *  ask permission of the user for use microphone or camera
          * */
          navigator.mediaDevices.getUserMedia({ audio: true, video: false })
          .then(gotStreamMethod)
          .catch('logError');
      };

      let getBuffers = (event) => {
          var buffers = [];
          for (var ch = 0; ch < 2; ++ch)
              buffers[ch] = event.inputBuffer.getChannelData(ch);
          return buffers;
      }

      let gotStreamMethod = (stream) => {

          config = {
              bufferLen: 4096,
              numChannels: 2,
              mimeType: 'audio/mpeg'
          };

          let tracks = stream.getTracks();
          /**Create a MediaStreamAudioSourceNode for the microphone **/
          microphone = audioContext.createMediaStreamSource(stream);
          document.getElementById('mic').innerHTML = microphone
          /**connect the AudioBufferSourceNode to the gainNode **/
          microphone.connect(processor);
          encoder = new Mp3LameEncoder(audioContext.sampleRate, 160); //bitRate set to 160
          /** Give the node a function to process audio events **/
          document.getElementById('check').innerHTML = processor
          let count = 0

          processor.onaudioprocess = function(event) {
              encoder.encode(getBuffers(event));
              console.log('MP3 encoding');
              document.getElementById('count').innerHTML = count
              count += 1
          };

          stopBtnRecord = () => {
                  var stage = 1
                  console.log('stop Record');
                  audioContext.close();
                  processor.disconnect();
                  tracks.forEach(track => track.stop());
                  stage = 2
                  audioElement = document.getElementById('handler')
                  audioElement.src = URL.createObjectURL(encoder.finish());
                  stage = 3
                  document.getElementById('check').innerHTML = stage
                  globlob = audioElement.src

                    fetch(audioElement.src)
                    .then( response => response.blob() )
                    .then( blob =>{
                        var reader = new FileReader();
                        reader.readAsDataURL(blob);
                        reader.onload = function(){
                            var base64data = this.result.split(',')[1]  // <-- this.result contains a base64 data URI
                            b64d = base64data
                        }; //end reader.onload

                    })//end fetch then
                    .catch((error) => {
                      console.log(error);
                    })
                  return stage

          };// stopRecord
      }
      this.stopRecord = function() {
        try{
          var stage = stopBtnRecord()
          console.log(stage);
        }
        catch {
          document.getElementById('check').innerHTML = 'Error'
          console.log('Apple fail before fetch');
        }

      };
  }
}



startVue()

function startVue(){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    data: {
        count : false
    },
    methods: {
      start : function(arg){
        window.globalFunc('start')
      },
      stop: function(task){
        window.globalFunc('stop')
        vue.blobURL = globlob
        console.log('status: mp3 rec stopped');
      }

    } // end methods



})// end NEW VUE

}// endFunction
