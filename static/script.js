const ctx = document.getElementById('chart');

new Chart(ctx, {

type:'line',

data:{

labels:['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],

datasets:[{

label:'Habit Completion',

data:[0]

}]

}

});


if(Notification.permission!=="granted"){
Notification.requestPermission()
}

setInterval(function(){

console.log("Reminder check")

},60000)