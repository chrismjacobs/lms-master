
    
    
    window.URL = window.URL || window.webkitURL;
    /** 
     * Detect the correct AudioContext for the browser 
     * */
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia  = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
    var recorder = new RecordVoiceAudios();    
    
    
    let startBtnGR = document.querySelector('.js-start1');
    let stopBtnGR = document.querySelector('.js-stop1');
    let saveBtnGR = document.querySelector('.js-save1');
    

    let startBtnGR2 = document.querySelector('.js-start2');
    let stopBtnGR2 = document.querySelector('.js-stop2');
    let saveBtnGR2 = document.querySelector('.js-save2');
    
    
    //Buttons control Recorder//
    startBtnGR.onclick = recorder.startRecord;
    stopBtnGR.onclick = recorder.stopRecord;

    startBtnGR2.onclick = recorder.startRecord;
    stopBtnGR2.onclick = recorder.stopRecord2;//different action on stop
    
    

    function RecordVoiceAudios() {
        let elementVolume = document.getElementById('canvas1'); 
        let elementVolume2 = document.getElementById('canvas2');             
        let ctx = elementVolume.getContext('2d') 
        let ctx2 = elementVolume2.getContext('2d') 

        let audioElement = document.getElementById('GRaudio1');
        let audioElement2 = document.getElementById('GRaudio2');

        let encoder = null;
        let microphone;
        let isRecording = false;
        var audioContext;
        let processor;
        let config = {
            bufferLen: 4096,
            numChannels: 2,
            mimeType: 'audio/mpeg'
        };

        this.startRecord = function() {
            audioContext = new AudioContext();
            /** Create a ScriptProcessorNode with a bufferSize of 
            * 4096 and two input and output channel 
            * */
            if (audioContext.createJavaScriptNode) {
                processor = audioContext.createJavaScriptNode(config.bufferLen, config.numChannels, config.numChannels);
            } else if (audioContext.createScriptProcessor) {
                processor = audioContext.createScriptProcessor(config.bufferLen, config.numChannels, config.numChannels);
            } else {
                console.log('WebAudio API has no support on this browser.');
            }

            timer = setTimeout(func, 180000) //3 min = 180000 millisecs
            function func(){
                $("#GRstop1").click()
                $("#GRstop2").click()
                alert('recording stopped at 3 min ')
                console.log('terminated');
            } 
        
            processor.connect(audioContext.destination);
            /**
            *  ask permission of the user for use microphone or camera  
            * */
            navigator.mediaDevices.getUserMedia({ audio: true, video: false })
            .then(gotStreamMethod)
            .catch(logError);
        };

        let getBuffers = (event) => {
            var buffers = [];
            for (var ch = 0; ch < 2; ++ch)
                buffers[ch] = event.inputBuffer.getChannelData(ch);
            return buffers;
        }

        let gotStreamMethod = (stream) => {
            startBtnGR.setAttribute('disabled', true);
            stopBtnGR.removeAttribute('disabled');
            
            startBtnGR2.setAttribute('disabled', true);
            stopBtnGR2.removeAttribute('disabled');
            
            audioElement.src = "";
            audioElement2.src = "";

            config = {
                bufferLen: 4096,
                numChannels: 2,
                mimeType: 'audio/mpeg'
            };
            isRecording = true;

            let tracks = stream.getTracks();
            /**Create a MediaStreamAudioSourceNode for the microphone **/
            microphone = audioContext.createMediaStreamSource(stream);
            /**connect the AudioBufferSourceNode to the gainNode **/
            microphone.connect(processor);
            /**log start time **/
            dnStart = Date.now()
            console.log('recording started @time: ' + dnStart)

            encoder = new Mp3LameEncoder(audioContext.sampleRate, 160); //bitRate set to 160 
            /** Give the node a function to process audio events **/
            processor.onaudioprocess = function(event) {
                encoder.encode(getBuffers(event));
            };

            stopBtnRecord = () => {
                clearTimeout(timer)
                dnStop = Date.now()
                console.log('recording stopped @time: ' + dnStop);            
                AudioLength = (Math.round((dnStop - dnStart)/950))
                console.log(AudioLength + ' secs recorded'); 
                
                isRecording = false;

                startBtnGR.removeAttribute('disabled');
                saveBtnGR.removeAttribute('disabled');
                stopBtnGR.setAttribute('disabled', true);
                startBtnGR2.removeAttribute('disabled');
                saveBtnGR2.removeAttribute('disabled');
                stopBtnGR2.setAttribute('disabled', true);

                audioContext.close();
                processor.disconnect();
                tracks.forEach(track => track.stop());
                audioElement.setAttribute('controls', true)
                audioElement.src = URL.createObjectURL(encoder.finish());
                                
                fetch(audioElement.src)
                .then( response => response.blob() )
                .then( blob =>{
                    var reader = new FileReader();
                    reader.readAsDataURL(blob);	
                    reader.onload = function(){ 
                        var base64data = this.result.split(',')[1]  // <-- this.result contains a base64 data URI                              
                        document.getElementById('audioLen01').value = AudioLength;                        
                        document.getElementById('audioData01').value = base64data
                        
                        saveBtnGR.onclick = function(){
                            $.ajax({
                                data : {
                                    title : '_' + ($('#assNumber').val() + '_1_GR'),
                                    base64 : base64data
                                },
                                type : 'POST',
                                url : '/audioUpload'                    
                            })
                            .done(function(data) {                    
                                $('#audioData01').val(data.title)
                                $("#submit").click();                       
                                })                        
                        }//end saveBtnGR

                    }; //end reader.onload

                })//end fetch
            
            };

            


            stopBtnRecord2 = () => {
                clearTimeout(timer)
                dnStop = Date.now()
                console.log('recording stopped @time: ' + dnStop);            
                AudioLength2 = (Math.round((dnStop - dnStart)/950))
                console.log(AudioLength2 + ' secs recorded'); 
                isRecording = false;

                startBtnGR.removeAttribute('disabled');
                saveBtnGR.removeAttribute('disabled');
                stopBtnGR.setAttribute('disabled', true);
                startBtnGR2.removeAttribute('disabled');
                saveBtnGR2.removeAttribute('disabled');
                stopBtnGR2.setAttribute('disabled', true);
                
                audioContext.close();
                processor.disconnect();
                tracks.forEach(track => track.stop());
                audioElement2.setAttribute('controls', true)
                audioElement2.src = URL.createObjectURL(encoder.finish());
                
                fetch(audioElement2.src)
                .then( response => response.blob() )
                .then( blob =>{
                    var reader = new FileReader();
                    reader.readAsDataURL(blob);	
                    reader.onload = function(){ 
                        var base64data = this.result.split(',')[1]  // <-- this.result contains a base64 data URI                              
                        document.getElementById('audioLen02').value = AudioLength2;                        
                        document.getElementById('audioData02').value = base64data
                        saveBtnGR2.onclick = function(){
                            $.ajax({
                                data : {
                                    title : '_' + ($('#assNumber').val() + '_2_GR'),
                                    base64 : base64data
                                },
                                type : 'POST',
                                url : '/audioUpload'                    
                            })
                            .done(function(data) {                    
                                $('#audioData02').val(data.title)
                                $("#submit").click();                       
                                })                        
                        }//end saveBtnGR
                    };
                })
            
            };

            analizer(audioContext);
        }

        this.stopRecord = function() {
            stopBtnRecord();
        };

        this.stopRecord2 = function() {
            stopBtnRecord2();
        };

        let analizer = (context) => {
            let listener = context.createAnalyser();
            microphone.connect(listener);
            listener.fftSize = 256;
            var bufferLength = listener.frequencyBinCount;
            let analyserData = new Uint8Array(bufferLength);

            let getVolume = () => {
                let volumeSum = 0;
                let volumeMax = 0;
    
                listener.getByteFrequencyData(analyserData);
    
                for (let i = 0; i < bufferLength; i++) {
                    volumeSum += analyserData[i];
                }
    
                let volume = volumeSum / bufferLength;

                if (volume > volumeMax)
                    volumeMax = volume;
    
                drawAudio(volume / 2);
                /** Call getVolume several time for catch the level until it stop the record*/
                return setTimeout(()=>{
                    if (isRecording)
                        getVolume();
                    else
                        drawAudio(0);
                }, 10);
            }

            getVolume();
        }

        let drawAudio = (volume) => {
            ctx.save();
            ctx.translate(0, 120);

            for (var i = 0; i < 14; i++) {
                fillStyle = '#eaffdb';
                if (i < volume)
                    fillStyle = '#94ff47';

                ctx.fillStyle = fillStyle;
                ctx.beginPath();
                ctx.arc(10, 2, 17, 0, Math.PI * 2);
                ctx.closePath();
                ctx.fill();
                ctx.translate(0, -7);
            }

            ctx.restore();
            ctx2.drawImage(elementVolume, 0, 0)
        }

        let logError = (error) => {
            alert(error);
            console.log(error);
        }

        
        drawAudio(0);
    }
