window.onload=function(){
    type();
}
var speed = 50;

function typeWriter3(p_id,txtt,i,stb) {
    if (i < txtt.length) {
        document.getElementById(p_id).innerHTML += txtt.charAt(i);
        i++;
        setTimeout(typeWriter3, speed,p_id,txtt,i,stb);
    }
    else
    {
        if(stb.length>0)
        {
            typeWriter3(p_id+"1",stb,0)
        }
    }
}

function MakeVisualisation(array){
    if(array.length %2 !=0)
    {
        alert("minden esetett le kell kezelni");
        return;
    }
    var precent=[];
    var colors=[];
    var counter=0;
    for (var index = 0; index < array.length; index++) {
        const element = array[index];
        if(index%2)
        {
            colors[counter]=element;
            counter++;
        }
        else
        {
            precent[counter]=element;
        }
    }
    console.log(colors);
    counter=0;
    var div=document.getElementById("vizualizacio");
    var sum=0;
    for(var i=0;i<100;i++)
    {
        if(i-sum>=precent[counter])
        {
            sum+=precent[counter];
            counter++;
        } 
        var newNode = document.createElement('i');
        newNode.className="fas fa-male class1";
        newNode.style.color=colors[counter];
        newNode.appendChild(document.createTextNode(''));
        div.appendChild(newNode);
        console.log(newNode);
    }
}