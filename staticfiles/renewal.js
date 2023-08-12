function searchfunction(){
    let input,filter,j;
    input=document.getElementById("search_session");
    filter=input.value.toUpperCase();
    let ul=document.getElementById("ul");
    let li=ul.getElementsByTagName("li");

    for(j=0;j<li.length;j++){
        message=document.getElementById("no_data");
        let a=li[j].getElementsByTagName('a')[0];
        let textValue=a.textContent || a.innerHTML;
        if(textValue.toUpperCase().indexOf(filter) > -1){
            li[j].style.display='';
            
        }                           
        else{
            li[j].style.display='none';

        }

    }
}
