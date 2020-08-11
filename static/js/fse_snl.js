var ansString = document.getElementById('ansDict').innerHTML
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

// ablank obj version of ansstring
var testString = document.getElementById('testDict').innerHTML
var testOBJ = JSON.parse(testString)
console.log('testOBJ', testOBJ);

var teamMembers = document.getElementById('teamMembers').innerHTML
var teamOBJ = JSON.parse(teamMembers)
console.log('teamOBJ', teamOBJ);

const mode = (window.location.href).split('/fse/')[1].split('/')[0]
const unit = (window.location.href).split('/fse/')[1].split('/')[1]
const team = (window.location.href).split('/fse/')[1].split('/')[2]
console.log(mode, unit, team);


startVue()

function startVue(){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted: function () {

        setInterval(function(){
            vue.updateAnswers()
        }, 15000)
        setTimeout(function(){
           vue.checkMarkers()
        }, 2000);

    },
    data: {
        ansOBJ: ansOBJ,
        teamOBJ: teamOBJ,
        testOBJ: testOBJ,
        mode: mode,
        unit: unit,
        team: team,
        marker:{
            1 : 1,
            2 : 1,
            3 : 1,
            4 : 1,
            5 : 1,
            6 : 1,
        },
        buttonColor:{
            3 : {background: 'dodgerblue', padding: '5px'},
            2 : {background: 'mediumseagreen', padding: '5px'},
            1 : {background: 'lightcoral', padding: '5px'},
            0 : {background: 'silver', padding: '5px'}
        },
        image64 : {
            fileType : null,
            base64 : null,
        },
        audio64 : {
            fileType : null,
            base64 : null,
        }
    },
    methods: {
        editMarkers : function(question) {
            this.resetB64()
            if (this.marker[question] == 3 ) {
                this.checkMarkers()
            }
            else{
                this.checkMarkers()
                this.marker[question] = 3
                // the role of the testOBJ is to store the changes
                //but not the alter the mainOBJ in case the changes are not saved
                let testString = JSON.stringify(this.ansOBJ[question])
                this.testOBJ[question] = JSON.parse(testString)

            }
        },
        resetMarkers : function(q) {
            for (var mark in vue.marker) {
                if (vue.marker[mark] == 3){
                    //console.log(vue.ansOBJ, vue.ansOBJ[q])
                    if (mark == q) {
                        alert('Question updated by ' + vue.ansOBJ[q]['user'])
                    }
                }
            }
        },
        checkMarkers : function() {
            for (var mark in vue.marker) {
                if ( vue.marker[mark] == 3 ){
                    console.log('open question', mark)
                    let reset = true
                    for (var item in vue.ansOBJ[mark]) {
                        console.log('CHECK', vue.ansOBJ[mark][item])
                        if(vue.ansOBJ[mark][item] == null){
                            reset = false
                        }
                    }
                    if ( reset == true ) {
                        vue.marker[mark] = 2
                    }
                }
                else {
                    vue.marker[mark] = 2
                    for (var item in vue.ansOBJ[mark]) {
                        // console.log(mark, item, vue.ansOBJ[mark][item]);
                        if(vue.ansOBJ[mark][item] == null){
                            vue.marker[mark] = 1
                        }
                    }
                }
            }
        },
        qStyle : function(key) {
            return this.buttonColor[this.marker[key]]
        },
        updateAnswers : function() {
            //runs in the background to check if others have changed something
            console.log('update via AJAX');
            $.ajax({

              data : {
                unit : this.unit,
                team : this.team,
                mode : this.mode
              },
              type : 'POST',
              url : '/FSEupdateAnswers',
            })
            .done(function(data) {
                var newOBJ = JSON.parse(data.ansString)
                for (var q in vue.ansOBJ){
                    // if the strings are not the same then a change has been made
                    if (   JSON.stringify(newOBJ[q]) != JSON.stringify(vue.ansOBJ[q])   ){
                        //alert(JSON.stringify(newOBJ[q]))
                        vue.ansOBJ = newOBJ
                        // reset markers knowing the question that has been changed
                        vue.resetMarkers(q)
                    }
                }
            })
            .fail(function(){
                console.log('error has occurred');
            });
        },
        storeData : function(key) {
            //reset the testOBJ
            this.testOBJ = testOBJ

            this.ansOBJ[key]['word'] = document.getElementById(key + 'w').value
            this.ansOBJ[key]['user'] = document.getElementById(key +  'u').value
            this.ansOBJ[key]['sentence'] = document.getElementById(key + 's').value

            this.checkMarkers()

            $.ajax({
              data : {
                unit : this.unit,
                team : this.team,
                mode : this.mode,
                ansOBJ : JSON.stringify(this.ansOBJ),
                question : key,
              },
              type : 'POST',
              url : '/FSEstoreAnswer',
            })
            .done(function(data) {
                console.log(data);
                vue.updateAnswers()
                vue.checkMarkers()
            })
            .fail(function(){
                alert('error - see instructor')
            });
        },
        storeB64 : function(key, b64) {
            //reset the testOBJ
            this.testOBJ = testOBJ

            if (b64 == 'i'){
                var b64data = this.image64['base64']
                var fileType = this.image64['fileType']
                this.ansOBJ[key]['imageLink'] = 'updating'
            }
            if (b64 == 'a'){
                var b64data = this.audio64['base64']
                var fileType = 'mp3'
                this.ansOBJ[key]['audioLink'] = 'updating'
            }

            $.ajax({
              data : {
                unit : this.unit,
                team : this.team,
                mode : this.mode,
                b64data : b64data,
                fileType : fileType,
                question : key,
                b64 : b64,
              },
              type : 'POST',
              url : '/FSEstoreB64',
            })
            .done(function(data) {
                //console.log(data);
                //alert('Question ' + data.question + ' updated')
                vue.resetB64()
                vue.updateAnswers()
                vue.checkMarkers()
            })
            .fail(function(){
                alert('error - see instructor')
            });
        },
        resetB64 : function() {
            vue.image64['fileType'] = false
            vue.audio64['fileType'] = false
        },
        imageValidation : function(){
            var fileInput = document.getElementById('image');
            //console.log('file', fileInput)
            var filePath = fileInput.value;
            //console.log(filePath);
            vue.image64['fileType'] = filePath.split('.')[1]


            var allowedExtensions = /(\.jpeg|\.png|\.jpg)$/i;

              if(fileInput.files[0].size > 7000000){ // 7 mb for video option
                  alert("File is too big!");
                  fileInput.value = '';
                  return false;
              }
              else if(!allowedExtensions.exec(filePath)){
                  alert('Please upload image: .jpeg/.png only.');
                  fileInput.value = '';
                  return false;
              }
              else{
                  console.dir( fileInput.files[0] );
                  var url = window.URL.createObjectURL(fileInput.files[0]);
                  fetch(url)
                  .then(function(res){
                      return res.blob();
                      })
                  .then(function(savedBlob){
                      var reader = new FileReader();
                      reader.readAsDataURL(savedBlob);
                      reader.onloadend = function() {
                          vue.image64['base64'] = reader.result.split(',')[1];
                          }
                  })
              }//end else
          },
        audioValidation : function(){
            var fileInput = document.getElementById('audio');
            console.log('file', fileInput)
            var filePath = fileInput.value;
            var allowedExtensions = /(\.mp3|\.m4a|\.m4v|\.mov|\.mp4)$/i;

            if(fileInput.files[0].size > 4400000){
                alert("File is too big!");
                location.reload()
                return false;
            }
            else if(!allowedExtensions.exec(filePath)){
                alert('Please upload audio file: .mp3/.m4a only.');
                fileInput.value = '';
                return false;
            }
            else{
                console.dir( fileInput.files[0] );
                var url = window.URL.createObjectURL(fileInput.files[0]);
                fetch(url)
                .then(function(res){
                    return res.blob();
                    })
                .then(function(savedBlob){

                var reader = new FileReader();
                reader.readAsDataURL(savedBlob);
                reader.onloadend = function() {
                        vue.audio64['base64'] = reader.result.split(',')[1];
                        vue.audio64['fileType'] = true
                    }
                })// end then function
            }//end else

          },//end audioValidation
        playAudio : function(key){
            player = document.getElementById('handler')
            button = document.getElementById(key)
            player.src = ansOBJ[key]['audioLink']
            player.load()
            button.innerHTML = 'Playing'
          },


    }, // end methods



})// end NEW VUE

}// endFunction

