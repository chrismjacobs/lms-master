var qDict = document.getElementById('qDict').innerHTML
var qOBJ = JSON.parse(qDict)
console.log('qOBJ', qOBJ)

var d = document.getElementById('design').innerHTML
var THEME = JSON.parse(d)
console.log('THEME', THEME)

var SCHEMA = document.getElementById('schema').innerHTML
console.log('SCHEMA', SCHEMA)

var deadline = document.getElementById('deadline').innerHTML
console.log('DEADLINE', deadline)


startVue(qOBJ)

function startVue(qOBJ){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted : function (){
        // start interval for ajax of participation data
        this.ansCheck()
        this.part_timer = setInterval(this.ansCheck, 30000);
        if (this.mode == 'Reader'){
          for (var btn in this.btnToggle){
            this.btnToggle[btn] = false
          }
          for (var s in this.show){
            this.show[s] = false
          }
        }
        if (this.mode == 'Team'){
          let name_count = (this.teamnames).length
          console.log('name_count', name_count);
          if (name_count == 1 ){
            this.mode = 'Writer'
          }
          else{
            this.teamSetUp(name_count)
            this.shareAnswer(0)
          }
        }
        if (this.mode == 'Instructor'){
            if (this.userID != 1 ){
              let url = (window.location.href).split('Instructor')[0] + 'Reader'
              console.log('goTO', url);
              window.location = url
            }
            else{
              clearInterval(this.part_timer)
              this.classCheck()
              this.class_timer = setInterval(this.classCheck, 10000);
            }

        var range = parseInt(this.teamcount) + 1
        for (i = 1; i < range; i++) {
            //this.leaderOBJ[i] = []
            this.leaderOBJ[i] = null
        }
        console.log('LeaderOBJ-mounted', this.leaderOBJ)
        }

        // deal with choices arrays
        for (let q in qOBJ) {
          if (qOBJ[q].t == 'mc') {
            // deal with MC choices
            qOBJ[q]['b'] = qOBJ[q].c[0]
            this.shuffle(qOBJ[q].c)
          } else if (qOBJ[q].t == 'tf') {
            // deal with TF choices
            console.log('TF setting', qOBJ[q].c)
            const answer = qOBJ[q].c[0]
            qOBJ[q]['b'] = answer
            this.setTF(q, qOBJ[q].c[0])
          } else if (qOBJ[q].t == 'set') {
            // deal with matching choices
            var answer = {}
            for (let ans in qOBJ[q].c) {
              answer[parseInt(ans) + 1] = qOBJ[q].c[ans]
            }
            qOBJ[q]['b'] = answer
            console.log('MATCH setting', qOBJ[q].c, answer)
            this.shuffle(qOBJ[q].c)
          } else if (qOBJ[q].t == 'sp') {
            // deal with spelling shuffle
            qOBJ[q].b = qOBJ[q].c

            var spList  = []

            for (let w in qOBJ[q].c) {
              let word = qOBJ[q].c[w].trim()
              console.log('sp word', word)
              if (word.includes(' ')) {
                let target = ''
                let spaces = word.split(' ')
                for (let nw in spaces) {
                  target += this.shuffleSpell(spaces[nw]) + ' '
                }
                spList.push(target)
              } else {
                spList.push(this.shuffleSpell(word))
              }
            }
            qOBJ[q].c = spList
          }

          this.qOBJ = {...this.qOBJ}
        }
    },
    data: {
      deadline : deadline,
      qOBJ : qOBJ,
      ansOBJ : null,
      classOBJ : null,
      leaderBar : {},
      leaderOBJ : {},
      unit : document.getElementById('un').innerHTML,
      part : document.getElementById('pn').innerHTML,
      qs : parseInt(document.getElementById('qs').innerHTML),
      mode :  document.getElementById('mode').innerHTML,
      userID : document.getElementById('userID').innerHTML,
      user : document.getElementById('user').innerHTML,
      teamcount : document.getElementById('teamcount').innerHTML,
      teamnames : JSON.parse(document.getElementById('teamnames').innerHTML),
      TEAMNAMES : [],
      teamShow : true,
      stage : 1,
      percent : 0,
      part_timer : null,
      class_timer : null,
      board_timer : null,
      seeAnswers: false,
      btnToggle : {
        1 : true,
        2 : true,
        3 : true,
        4 : true,
        5 : true,
        6 : true,
        7 : true,
        8 : true,
      },
      show : {
        1 : false,
        2 : false,
        3 : false,
        4 : false,
        5 : false,
        6 : false,
        7 : false,
        8 : false,
      },
      spelling : {
        0 : '',
        1 : '',
        2 : '',
        3 : ''
      },
      image_b64 : null
    },
    methods: {
      imageValidation : function(key) {
        let vue = this
        var fileInput = document.getElementById('image' + key);
        var allowedExtensions = /(\.jpeg|\.png|\.jpg)$/i;
        var filePath = fileInput.value;

      if(fileInput.files[0].size > 44000000){
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
          console.dir( 'FILE', fileInput.files[0] );
          var url = window.URL.createObjectURL(fileInput.files[0]);
          fetch(url)
          .then(function(res){
              return res.blob();
              })
          .then(function(savedBlob){
              var reader = new FileReader();
              reader.readAsDataURL(savedBlob);
              reader.onloadend = function() {
                  vue.image_b64 = reader.result.split(',')[1];
                  console.log(vue.image_b64)
            }
          })
      }//end else
        return true
    },
      shuffleSpell: function (word) {
        var a = word.split(""),
        n = a.length

        for(var i = n - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var tmp = a[i];
            a[i] = a[j];
            a[j] = tmp;
        }
        return a.join("");
      },
      getSpellBTN: function (key) {

        console.log('spell btn', this.spelling, this.qOBJ[key].b)
        var allow = true

        for (let b in this.qOBJ[key].b) {
          if (this.spelling[b] == '') {
            console.log('false ""')
            allow = false
          } else if (this.spelling[b].replace(/\s/g, '').toLowerCase() != this.qOBJ[key].b[b].replace(/\s/g, '').toLowerCase()) {
            console.log(this.spelling[b], this.qOBJ[key].b[b])
            allow = false
          }
        }

        return allow

      },
      getBG: function (key, s) {
        console.log('getBG', key, s, this.spelling, this.qOBJ[key].b)

        var entry = this.spelling[s].toLowerCase()

        if (entry.length > 0) {
          entry = entry.replace(/\s/g, '')
        } else {
          return false
        }

        let ans = this.qOBJ[key].b[s].replace(/\s/g, '').toLowerCase()

        if (entry.length > ans.length) {
          return 'background:red'
        }

        var style = 'background:green'
        for (let i = 0; i < entry.length; i++) {
          if (entry[i] != ans[i]) {
            style = 'background:red'
          }
        }

        if (style == 'background:green' && entry.length == ans.length) {
          return 'background:DarkTurquoise'
        }

        return style
      },
      getCount: function (a, b) {

        var c = a

        if (a != '') {
          c = a.replace(/\s/g, '')
        }

        return c.length + '/' + b.replace(/\s/g, '').length
      },
      setTF: function (q, ans) {
        let TFset = [ans]
        let options = [
          'T T T',
          'T F F',
          'T T F',
          'T F T',
          'F F F',
          'F T T',
          'F F T',
          'F T F'
        ]
        this.shuffle(options)
        for (let a in options) {
          if (TFset.length < 4 && options[a] != ans) {
            TFset.push(options[a])
          }
        }
        this.shuffle(TFset)
        this.qOBJ[q]['c'] = TFset
      },
      shuffle: function (array) {
        // Fisher-Yates shuffle
        for (let i = array.length - 1; i > 0; i--) {
          let j = Math.floor(Math.random() * (i + 1)); // random index from 0 to i
          [array[i], array[j]] = [array[j], array[i]]
        }
        return array
      },
      teamSetUp: function (name_count) {
        let rotator = {
          1 : {
            2 : [0,1,0,1,0,1,0,1],
            3 : [0,1,2,0,1,2,0,1],
            4 : [0,1,2,3,0,1,2,3]
          },
          2 : {
            2 : [1,0,1,0,1,0,1,0],
            3 : [1,2,0,1,2,0,1,2],
            4 : [1,2,3,0,1,2,3,0]
          },
          3 : {
            2 : [0,1,0,1,0,1,0,1],
            3 : [2,0,1,2,0,1,2,0],
            4 : [2,3,0,1,2,3,0,1]
          },
          4 : {
            2 : [1,0,1,0,1,0,1,0],
            3 : [0,2,1,0,2,1,0,2],
            4 : [3,0,1,2,3,0,1,2]
          }
        }

        let TEAMNAMES = []
        let teamnames = this.teamnames

        if (name_count == 1 ){
            this.mode = 'Writer'
        }
        else{
          items = rotator[this.part][name_count]
          console.log('itemsArray', items);
            items.forEach(function(item){
              TEAMNAMES.push(teamnames[item])
            })
        }

        this.TEAMNAMES = TEAMNAMES

        for (let btn in this.btnToggle){
          if (this.TEAMNAMES[btn - 1] != this.user){
            this.btnToggle[btn] = false
          }
        }

        console.log('TEAMNAMES ', this.TEAMNAMES);
        console.log('btnToggle ', this.btnToggle);

      },
      showAnswers: function (key){
        // if (this.deadline == false || this.deadline == 'False') {
        //   alert('Deadline Passed - Answer viewing is closed, ask your teacher for help')
        //   return false
        // }
        if (this.show[key] == true){
          for (var s in this.show){
          this.show[s] = false
          }
        }
        else{
          for (var s in this.show){
            this.show[s] = false
          }
          this.show[key] = true
        }
        console.log('showAnswers pressed')
      },
      stageCheck: function (key){
        if (this.mode == 'Reader') {
          return true
        }
        if (this.mode == 'Team') {
          return this.teamShow
        }
        else if (this.mode == 'Instructor') {
          this.seeAnswers = true
          return false
        }
        else if (this.mode == 'Writer') {
          if (key == this.stage) {
            return true
          }
          else{
            return false
          }
        }
        else {
          alert('No Mode Found')
          return false
        }
      },
      shareAnswer: function (question, answer){
        if (answer == 'perfect') {
          this.spelling = {
            0 : '',
            1 : '',
            2 : '',
            3 : ''
          }
        }

        if (answer == 'base') {
          answer = this.image_b64
        }
        console.log('ajax called');
        if (question == 0){
          answer = 'start_team'
          console.log(answer);
        }
        else if (answer == null) {
          answer = document.getElementById(question).value
          // remove all white space
          if (answer.replace(/\s/g, '').length < 1){
            alert('answer is empty')
            return false
          }
          this.btnToggle[question] = false
        } else {
          /// deal with MC answer where answer is given
          this.btnToggle[question] = false
        }

        $.ajax({
          data : {
              unit : this.unit,
              part : this.part,
              question : question,
              answer : answer,
              qs : this.qs, //qs == number of questions
          },
          type : 'POST',
          url : '/shareUpload'
          })
          .done(function(data) {
            if (data.action){
              alert(data.answer + ': Team - ' + vue.teamnames)
              if (data.answer == 'participation completed') {
                location.reload()
              }
            }
            if (data.action == '2'){
              vue.teamShow = false
            }
            vue.stage += 1
          })
          .fail(function(){
            alert('Failed, please reload page and try again')
          });
      },
      getInSplit: function (ans) {
        let rAns = []
        if (ans != null) {
          rAns = ans.split('/')
        }
        return rAns
      },
      getSetStyle: function (key, check) {

        var bg = 'background:saddlebrown'

        if (check) {
          bg = 'background:green'
        }

        var sStr = 'height:30px;width:100px;color:white;' + bg

        var answerOBJ = this.qOBJ[key].b
        // console.log('set style', answerOBJ)

        if (Object.keys(answerOBJ).length > 5) {
          sStr = 'height:30px;width:220px;color:white;' + bg
        }

        return sStr
      },
      shareMC: function (key){
        // key is the question number
        var localKey = this.unit + this.part + key
        var mce = document.getElementsByName('mc' + key)
        console.log('shareMC', key, mce, this.qOBJ)
        var correctAns = this.qOBJ[key].b
        for (let e in mce) {
          if (mce[e].checked) {
            if (mce[e].value ==  correctAns) {
              alert('Correct! Well done')
              if(!localStorage.getItem(localKey)) {
                this.shareAnswer(key, ':) ' + this.qOBJ[key].b)
              } else {
                this.shareAnswer(key, parseInt(localStorage.getItem(localKey)) + 1)
                localStorage.clear()
              }
            }
            else {
              if(!localStorage.getItem(localKey)) {
                var tries = 0
                localStorage.setItem(localKey, tries)
                alert("Incorrect - That's one try")
              } else {
                var tries = parseInt(localStorage.getItem(localKey)) + 1
                localStorage.setItem(localKey, tries)
                alert('Incorrect - ' + tries + ' tries')
              }
            }
          }
        }
      },
      shareInputs: function (key) {
        var answer = ''
        var gate = true
        var inputs = document.getElementsByName('input' + key)
        console.log('shareInputs', key, inputs)
        for (let i in inputs) {
          console.log('logi', inputs[i])
          if (inputs[i].value != undefined && inputs[i].value.length < 1 ) {
            alert('Answer Empty: ' + inputs[i].id)
            gate = false
          } else if (inputs[i].value != undefined) {
            answer += ' ' + inputs[i].value + ' /'
            const check = answer
            console.log(check)
          }
        }
        if (gate) {
          this.shareAnswer(key, answer)
        }
      },
      shareSet: function (key) {

        var localKey = this.unit + this.part + key

        var answerOBJ = this.qOBJ[key].b

        var aOBJlen = 0

        for (let k in answerOBJ){
          console.log(k)
          aOBJlen += 1
        }

        var aList = []
        var corrAns = []
        var correct = 0

        for (let q in answerOBJ) {

          var e = document.getElementById('set' + key + q)

          console.log(q, key, e.value)

          if (aList.includes(e.value)) {
            aList.push('duplicate')
          } else if (e.value == answerOBJ[q]) {
            aList.push(e.value)
            corrAns.push(q)
            correct += 1
          } else {
            aList.push(e.value)
          }
        }

        console.log(aList, correct, answerOBJ.length)

        if (aList.includes('0')) {
          alert('Please select one answer for each')
        } else if (aList.includes('duplicate')) {
          alert('Each answer must be different')
        } else if (correct < aOBJlen) {
          if (!localStorage.getItem(localKey)) {
            localStorage.setItem(localKey, 1)
          } else {
            var tries = localStorage.getItem(localKey)
            localStorage.setItem(localKey, parseInt(tries) + 1)
          }
          alert('You have ' + correct + ' correct answers: ( ' + corrAns + ' )')

          var setDrops = document.getElementsByName('set' + key)
          for (let sd in setDrops) {
            //console.log('aOBJ', sd+1, answerOBJ, answerOBJ[1])

            console.log('sd', sd, setDrops[sd].value, answerOBJ[parseInt(sd)+1])
            setDrops[sd].style = this.getSetStyle(key, setDrops[sd].value == answerOBJ[parseInt(sd)+1])
          }

        } else {
          alert('CORRECT!')
          if (!localStorage.getItem(localKey)) {
            this.shareAnswer(key, 'First try')
          } else if (parseInt(localStorage.getItem(localKey)) == 1) {
            this.shareAnswer(key, 'Second try')
          } else {
            this.shareAnswer(key, '>2 Tries')
          }
        }
      },
      ansCheck : function() {
        $.ajax({
          data : {
            unit : this.unit,
            part : this.part,
            check : 0  // signal to return one students data (not whole class)
          },
          type : 'POST',
          url : '/getPdata',
        })
        .done(function(data) {
            console.log(data.dataDict);
            vue.ansOBJ = JSON.parse(data.dataDict)
            let count = 1
            for (let ans in vue.ansOBJ){
              if (vue.ansOBJ[ans] != null){
                console.log(vue.ansOBJ[ans]);
                count += 1
                ///////NEW ADDITON
                vue.btnToggle[ans] = false
              }
            }
            // count starts at one and will be greater than qs
            // after last answer submitted
            if (count > vue.qs){
              vue.classCheck()
              vue.class_timer = setInterval(vue.classCheck, 10000);
              vue.seeAnswers = true
              //alert('The participation has been completed by ' + vue.teamnames)
              clearInterval(vue.part_timer)
            }
            vue.stage = count
            console.log(count, vue.ansOBJ);
          })
          .fail(function(){
                  alert('error')
          });
      },
      openPart : function() {
        $.ajax({
          data : {
            key : this.unit + '-' + this.part,
            number : this.unit
          },
          type : 'POST',
          url : '/openUnit',
        })
        .done(function(data) {
            location.reload()
          })
          .fail(function(){
            alert('error')
          });
      },
      classCheck : function() {
        $.ajax({
          data : {
            unit : this.unit,
            part : this.part,
            check : 1  // signal to return all class data
          },
          type : 'POST',
          url : '/getPdata',
        })
        .done(function(data) {
          //console.log('classCheck ', data.dataDict);
          vue.classOBJ = JSON.parse(data.dataDict)

          // clear leader obj back to zero
          for (let lead in vue.leaderOBJ){
            vue.leaderOBJ[lead] = []
          }
          console.log('RESET', JSON.stringify(vue.leaderOBJ));
          console.log('ClassOBJ', vue.classOBJ);


          for (let team in vue.leaderOBJ) {
            for (let qn in vue.classOBJ){
              let answer = vue.classOBJ[qn][team]
              if (answer != null && answer.length > 0 ){
                vue.leaderOBJ[team].push(vue.classOBJ[qn][team])
              }
            }
          }
          for (let rec in vue.leaderOBJ){
            if (vue.leaderOBJ[rec].length == 0 ){
              var width_percent = '5%'
              var background = 'red'
            }
            else if (vue.leaderOBJ[rec].length == vue.qs) {
              var width_percent = '100%'
              var bColor = {
                1 : 'mediumspringgreen',
                2 : 'gold',
                3 : 'turquoise',
                4 : 'gold',
                5 : 'deeppink',
                6 : 'deeppink',
              }
              console.log(bColor, parseInt(SCHEMA))

              var background = bColor[parseInt(SCHEMA)]
            }
            else {
              var width = ((vue.leaderOBJ[rec]).length / vue.qs ) * 100
              var width_percent = width + '%'
              var background = THEME['titleColor']
            }
            console.log('width ', width_percent);

            vue.leaderBar[rec] = { background:background,  height:'30px', width: width_percent, border: '1px solid grey', 'border-radius': '5px'}


          }
          var total = 0
          for (let team in vue.leaderOBJ){
            for (let answer in vue.leaderOBJ[team]){
              total += 1
            }
          }


          var percent_float = ( total / (vue.qs * vue.teamcount )  ) *100
          vue.percent = percent_float.toPrecision(4)
          console.log('%: qs/teamcount/total/percent', vue.qs, vue.teamcount, total, vue.percent);

          })
          .fail(function(){
                  alert('error')
          });
      }

    } // end methods


})// end NEW VUE

}// endFunction


