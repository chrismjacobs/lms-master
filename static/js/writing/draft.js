
let unit_number = document.getElementById('unit').innerHTML
console.log(unit_number)

let partner = document.getElementById('partner').innerHTML
console.log('partner', partner)

let user = document.getElementById('user').innerHTML
console.log('user', user)

let srcString = document.getElementById('sources').innerHTML
let sources = JSON.parse(srcString)
let slides = sources[unit_number]['Materials']

let fullString = document.getElementById('fullDict').innerHTML
let fullOBJ = JSON.parse(fullString)
let info = JSON.parse(fullOBJ['info'])
let plan = JSON.parse(fullOBJ['plan'])
let draft = JSON.parse(fullOBJ['draft'])

let newPlan = ''

Object.size = function(obj) {
    var size = 0
    for (key in obj) {
        size += 1
    }
    return size;
};

if (Object.size(plan) == 0 ){
    console.log('No data')
    alert('You must complete your plan before you can start the writing')
    window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number
}
else{
    newPlan = {
        0 : [plan['Topic'], plan['Thesis']],
        1 : [plan['Idea_1'], plan['Details_1']],
        2 : [plan['Idea_2'], plan['Details_2']],
        3 : [plan['Idea_3'], plan['Details_3']],
        4 : ["", ""]
    }
}
console.log();
if (Object.size(draft) == 0 ){
    draft = {
        "Intro" : "",
        "Part_1": "",
        "Part_2": "",
        "Part_3": "",
        "Closing": "",
        }
    }

startVue(newPlan, info, draft)


function startVue(newPlan, info, draft){
    let app = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted: function(){
        for (var head in draft){
            this.deSelect(head)
        }
    },
    data: {
        partner : partner,
        user: user,
        planOBJ : newPlan,
        infoOBJ : info,
        draftOBJ : draft,
        save : false,
        stage : info['stage'],
        theme : { 'color' : info['theme'] },
        control : {
            0 : [],
            1 : [],
            2 : [],
            3 : [],
            4 : []
            },
        btn_control : {
            very : true,
            also : true,
            let  : true,
            everyone  : true,
            'no matter' : true,
            there : true,
            commas : true,
            words : true,
            spaces : true,
            although : true
        },
        slides : {
            very : "https://docs.google.com/presentation/d/e/2PACX-1vTlkKekrFpLAINvciyYh_KOxRRGSzikZN27pPoqijHQKlQhbKL0DQzlH6uUx5P862Y6i7Gn1qUASWo2/embed",
            everyone : "https://docs.google.com/presentation/d/e/2PACX-1vRlO8hOUw15yJVSMvlYRY7PYHPCo-G9m8vtK04s0ymu37LvshSYYxcNOXohNt9wNarz4ZVPVmDmvYRa/embed",
            also : "https://docs.google.com/presentation/d/e/2PACX-1vSaRz0wI_qa8iyIujCJjtEC_M_gJZa7Fw0OLLJbW2_QoQ_yOrezSvn-bvid1m-gR6n1baN1UAptFRFZ/embed",
            let  : "https://docs.google.com/presentation/d/e/2PACX-1vR7E00mYlONL3h6ZfkYkk0Eyiiz9K2xpSfLnTHMKhqLSCgsEI8tS6lPkIVSqxidm1t1-PT9tIvRkddZ/embed",
            'no matter' : "https://docs.google.com/presentation/d/e/2PACX-1vQtQUX1hrwY1RwYr229bQcvYgMBOMrfat87pGfWEzxDreQjsBpuCf4rSXokvKehDuE7hNGCloqi2yM9/embed",
            there : "https://docs.google.com/presentation/d/e/2PACX-1vSmrj_CTJ1xQUF3hn-mnVg43kfGDLnQ9cJUyZUkCuduM-HiVmfTHnlPfxonAk5KqAbfX6o5OR5SeuPZ/embed",
            commas : "https://docs.google.com/presentation/d/e/2PACX-1vSRaq_OKjKXXlm44qAjnedKcOYZiIBdmF_omtzLKU-mj4i-Mjglq8AsZRCME_OTFtEdwDNlKTkMg4m-/embed",
            words : "https://docs.google.com/presentation/d/e/2PACX-1vRQw3jKPPhHLVMJc4u8ILXIHcQaihiVU-CgxKSmWLWpifLLuorKDAfoHJ7G1sDX7ZDvxRNxTv0AYFIf/embed",
            although : "https://docs.google.com/presentation/d/e/2PACX-1vRUWMaHsRDRBU84JPTScvGDfwvByPXMEKa0AiL1U3npEh4KSk0WlSdKQVGFKPXCLVtHYuqr0zhNfTCd/embed",
            Intro  : "https://docs.google.com/presentation/d/e/2PACX-1vRzO8mqA8oD7N2p1BCSCb-4KgUXtnZcayai2JqTkSsdpxfXcL9WozNoh4Yv0AUAoDH7s1qFzXqEzIq_/embed",
            Thesis  : "https://docs.google.com/presentation/d/e/2PACX-1vRzO8mqA8oD7N2p1BCSCb-4KgUXtnZcayai2JqTkSsdpxfXcL9WozNoh4Yv0AUAoDH7s1qFzXqEzIq_/embed",
            Part_1 : "https://docs.google.com/presentation/d/e/2PACX-1vSAEgJxNqEHcCL0Q43mkiGzkVITGcVhNa90nL_jugy3NJ4Av22ydcnZFCZ9s1PipmBkAcHy8TtHBfUI/embed",
            Part_2 : "https://docs.google.com/presentation/d/e/2PACX-1vSAEgJxNqEHcCL0Q43mkiGzkVITGcVhNa90nL_jugy3NJ4Av22ydcnZFCZ9s1PipmBkAcHy8TtHBfUI/embed",
            Part_3 : "https://docs.google.com/presentation/d/e/2PACX-1vSAEgJxNqEHcCL0Q43mkiGzkVITGcVhNa90nL_jugy3NJ4Av22ydcnZFCZ9s1PipmBkAcHy8TtHBfUI/embed",
            Closing : "https://docs.google.com/presentation/d/e/2PACX-1vShLIQjSBDNgo-SZC7csptsZ-bbg7_1ERIHTo2lfJUgLNpPTysg596TwUwT68ZUUbvF0FxpPNWLrCBU/embed",
            spaces : "https://docs.google.com/presentation/d/e/2PACX-1vSUcZl4Q5psylypgyleZNWsPN9N6AcP4TsldRLVmIgFDAyB5oMW8gkNOygkrGBeVWWc80HclXSb2VQD/embed",
        },
        helper : {
            Intro : false,
            Part_1 : false,
            Part_2 : false,
            Part_3 : false,
            Closing : false
        }

    },
    methods: {
        getBG: function () {
            if (this.user == this.partner) {
                return {background:'#AB47BC'}
            }
        },
        selectText: function(id){
            console.log(id)
            document.getElementById(id).setAttribute('class', 'input2')
        },
        deSelect: function(id, idx){
            let string = (this.$refs[id])[0].value
            console.log('STRING', string, 'ID_INPUT', this.draftOBJ[id])
            //check if change has been made before updating object
            if (string != this.draftOBJ[id]){
                this.save = true
                this.draftOBJ[id] = string
                console.log('SAVE', string, this.draftOBJ );
            }


            if (string.length > 0 ) {
                let textBox = document.getElementById(id)
                console.log('Height', textBox.scrollHeight)
                textBox.setAttribute('class', 'input3')
                textBox.setAttribute('style', 'height:' + textBox.scrollHeight +'px !important')
            }

            else {
                document.getElementById(id).setAttribute('class', 'input1')
            }

            /// text checking and feedback
            this.control[idx] = []


            if (
                string.indexOf('very like') >= 0 ||
                string.indexOf('very appreciate') >= 0 ||
                string.indexOf('very hate') >= 0 ||
                string.indexOf('very enjoy') >= 0 ||
                string.indexOf('very love') >= 0
                ){
                this.control[idx].push('very')
            }

            // take all white space from text
            console.log(string.replace(/\s\s/g, " "));
            new_string = string.replace(/\s\s/g, " ")

            var feedback = [
                ['very' ,  /very like/i],
                ['very' ,  /very enjoy/i],
                ['very' ,  /very love/i],
                ['very' ,  /very hate/i],
                ['very' ,  /very appreciate/i],

                ['there' ,  /there have/i],
                ['there' ,  /there has/i],
                ['there' ,  /there had/i],

                ['also' ,  /also can/i],
                ['also' ,  /also is/i],
                ['also' ,  /also will/i],
                ['also' ,  /also am/i],
                ['also' ,  /also are/i],

                ['no matter' ,  /no matter/i],
                ['let' ,  /\slet\s/i],
                ['everyone' ,  /\severyone\s/i],
                //http://www.regular-expressions.info/lookaround.html
                ['although' ,  /lthough/i],

            ]

            for (var fb in feedback) {
                if (new_string.match(feedback[fb][1])){
                    if (this.control[idx].includes(feedback[fb][0]) ){
                        console.log('pass');
                    }
                    else{
                        this.control[idx].push(feedback[fb][0])
                    }
                }
            }



            var commaCheck = string.split(',')
            console.log('Comma', commaCheck);
            var commas = commaCheck.length
            var periodCheck = string.split('.')
            var periods = periodCheck.length

            if (periods < 1 && id == 0) {
                alert('Introduction need 2 sentences: Into + Thesis (see notes)')
            } else if (periods < 1 && id != 4) {
                alert('Each part should have 2 or more sentences:  Idea + Detail')
            }
            if (commas > periods * 1.8 ) {
                this.control[idx].push('commas')
            }

            for (var cLine in commaCheck){
                console.log(commaCheck[cLine])
                if (cLine != 0){
                    if (commaCheck[cLine][0] != ' '){
                        console.log('space issue: cLine', cLine);
                        if (this.control[idx].includes('spaces') ){
                            console.log('pass');
                        }
                        else{
                            this.control[idx].push('spaces')
                        }
                    }
                }
            }

            for (var pLine in periodCheck){
                console.log(periodCheck[pLine])
                if (pLine != 0){
                    if (periodCheck[pLine][0] != ' '){
                        console.log('space issue: pLine', pLine);
                        if (pLine != periodCheck.length - 1){
                            if (this.control[idx].includes('spaces') ){
                                console.log('pass');
                            }
                            else{
                                this.control[idx].push('spaces')
                            }
                        }
                    }
                }
            }

            var wordCheck = string.split(' ')
            var words = wordCheck.length
            if (string.indexOf('Part') >= 0 && words < 20) {
                this.control[idx].push('word_count')
            }

            console.log(this.control)
        },
        controller: function(item){
            for (btn in this.btn_control){
                if (btn == item){
                   this.btn_control[item] = !this.btn_control[item]
                }
                else {
                    this.btn_control[btn] = false
                }
            }
            console.log(this.btn_control[item])
        },
        helpButton: function(key){
            for (help in this.helper){
                if (help == key){
                   this.helper[help] = !this.helper[help]
                   console.log(help, 'DONE');
                }
                else {
                    this.helper[help] = false
                    console.log(help, 'ALSO');
                }
            }
            console.log(key, this.helper)
        },
        readRefs: function(){
            var count = 0
            for(var key in this.draftOBJ) {
                if (this.draftOBJ[key] == ''){
                    alert('Warning! ' + key + ' is not complete yet - but you can fix it later' )
                    stage = 1
                    date = 'none'
                }
                else{
                    count += (this.draftOBJ[key].split(' ')).length
                    if (stage = 1) {
                        stage = 2
                        //this will catch the first date of completed work
                        date = 'update'
                    }
                    else {
                        stage = 2
                        date = 'redo'
                    }

                    console.log('COUNT', count)
                }
            }
            this.sendData(this.draftOBJ, stage)
            alert('Please wait a moment while your writing is being updated')
        },
        sendData: function (obj, stage){
            console.log(obj, stage)
            $.ajax({
                type : 'POST',
                data : {
                    unit : document.getElementById('unit').innerHTML,
                    obj : JSON.stringify(obj),
                    stage : stage,
                    work : 'draft'
                },
                url : '/storeData',
            })
            .done(function(data) {
                if (data) {
                    alert('Thank you ' + data.name + ', your ' + data.work + ' has been saved')
                    window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number
                }
            });
        },
        cancel: function(){
            alert('You have cancelled so your changes will not be saved')
            window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number
        }
    }

})// end NEW VUE

}// end start vue function